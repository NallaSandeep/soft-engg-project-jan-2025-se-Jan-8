"""Document indexing and processing service"""
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
import uuid
import aiofiles
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from typing import Awaitable
import json
import logging
import PyPDF2
import docx2txt
from fastapi import UploadFile, HTTPException, status
import chromadb
from chromadb.api.models.Collection import Collection
import mimetypes

from app.core.config import settings
from app.core.errors import (
    StudyIndexerError,
    DocumentNotFoundError,
    InvalidFileTypeError,
    FileSizeTooLargeError,
    DocumentProcessingError,
    InvalidDocumentError,
    SearchError
)
from app.schemas.documents import DocumentMetadata, PersonalMetadata
from app.schemas.base import DocumentStatus, CollectionType
from app.schemas.search import SearchResult
from app.services.chroma import ChromaService

logger = logging.getLogger(__name__)

ALLOWED_MIME_TYPES = {
    "text/plain": ".txt",
    "text/markdown": ".md",
    "application/pdf": ".pdf",
    "application/msword": ".doc",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
    "application/vnd.ms-powerpoint": ".ppt",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation": ".pptx"
}

def check_ml_dependencies():
    """Check if ML dependencies are available"""
    try:
        # Check all required ML packages
        import sentence_transformers
        import chromadb
        import torch
        import transformers
        import langchain
        
        # Try importing but don't initialize
        from sentence_transformers import SentenceTransformer
        return True
    except ImportError as e:
        logger.warning(f"ML dependencies not available: {str(e)}")
        return False

# Global instance for singleton
_indexer_instance = None

class DocumentLoader:
    """Simple document loader for various file types"""
    
    @staticmethod
    def load_pdf(file_path: str) -> str:
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text()
            return text
        except Exception as e:
            raise DocumentProcessingError(f"Error processing PDF file: {str(e)}")
    
    @staticmethod
    def load_text(file_path: str) -> str:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            raise DocumentProcessingError(f"Error processing text file: {str(e)}")
    
    @staticmethod
    def load_docx(file_path: str) -> str:
        try:
            return docx2txt.process(file_path)
        except Exception as e:
            raise DocumentProcessingError(f"Error processing DOCX file: {str(e)}")
    
    @staticmethod
    def load_markdown(file_path: str) -> str:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            raise DocumentProcessingError(f"Error processing Markdown file: {str(e)}")

class DocumentIndexer:
    """Service for document processing and indexing"""
    
    def __new__(cls):
        global _indexer_instance
        if _indexer_instance is None:
            instance = super(DocumentIndexer, cls).__new__(cls)
            instance._initialized = False
            _indexer_instance = instance
        return _indexer_instance
    
    def __init__(self):
        """Initialize document indexer"""
        if getattr(self, '_initialized', False):
            return
            
        # Initialize ML components first
        try:
            from sentence_transformers import SentenceTransformer
            logger.info("Initializing ML components...")
            self.embedder = SentenceTransformer(
                settings.EMBEDDING_MODEL,
                device=settings.EMBEDDING_DEVICE
            )
            
            # Initialize text splitter
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=settings.MAX_CHUNK_SIZE,
                chunk_overlap=settings.CHUNK_OVERLAP
            )
            
            self.ml_enabled = True
            logger.info("ML components initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize ML components: {str(e)}")
            self.ml_enabled = False
        
        # Initialize ChromaDB separately
        try:
            # Initialize ChromaDB service
            self.chroma = ChromaService()
            
            # Ensure general collection exists - we'll do this asynchronously later
            # during the first request instead of during initialization
            self.chroma_enabled = True
            logger.info("ChromaDB initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {str(e)}")
            self.chroma_enabled = False
        
        # Ensure directories exist
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        os.makedirs(settings.PROCESSED_DIR, exist_ok=True)
        
        self.loader = DocumentLoader()
        self._initialized = True
        self._general_collection_initialized = False
    
    async def _ensure_general_collection(self):
        """Ensure the general collection exists"""
        if self._general_collection_initialized:
            return
            
        try:
            general_metadata = {
                "description": "General collection for all documents",
                "created_by": "StudyIndexer",
                "version": settings.VERSION,
                "collection_type": "general"
            }
            await self.chroma.get_or_create_collection("general", general_metadata)
            logger.info("General collection initialized")
            self._general_collection_initialized = True
        except Exception as e:
            logger.error("Failed to initialize general collection: %s", str(e))
            self.chroma_enabled = False
            raise StudyIndexerError("Failed to initialize ChromaDB: Failed to initialize general collection")
    
    def prepare_document(
        self,
        file: UploadFile,
        metadata: DocumentMetadata,
        user_id: str
    ) -> str:
        """Prepare document for indexing"""
        # Validate file type
        content_type = file.content_type or mimetypes.guess_type(file.filename)[0]
        if not content_type or content_type not in ALLOWED_MIME_TYPES:
            raise InvalidFileTypeError(f"Unsupported file type: {content_type}")
            
        # Generate unique ID
        document_id = str(uuid.uuid4())
        
        # Save file
        file_ext = ALLOWED_MIME_TYPES.get(content_type, ".txt")
        upload_path = os.path.join(settings.UPLOAD_DIR, f"{document_id}{file_ext}")
        
        try:
            contents = file.file.read()
            if len(contents) > settings.MAX_UPLOAD_SIZE:
                raise FileSizeTooLargeError(
                    f"File size exceeds limit of {settings.MAX_UPLOAD_SIZE} bytes"
                )
                
            with open(upload_path, "wb") as f:
                f.write(contents)
                
            # Add user ID to metadata
            metadata_dict = metadata.model_dump()
            metadata_dict["user_id"] = user_id
            
            # Initialize personal metadata if needed
            if metadata.collection == CollectionType.PERSONAL and not metadata.personal:
                metadata_dict["personal"] = PersonalMetadata().model_dump()
                
            # Save status
            status_path = os.path.join(settings.PROCESSED_DIR, f"{document_id}.json")
            status = {
                "document_id": document_id,
                "filename": file.filename,
                "content_type": content_type,
                "size": len(contents),
                "upload_time": datetime.utcnow().isoformat(),
                "status": "pending",
                "metadata": metadata_dict
            }
            
            with open(status_path, "w") as f:
                json.dump(status, f, indent=2)
                
            logger.info(
                "Document prepared for indexing [id=%s, size=%d, type=%s]",
                document_id,
                len(contents),
                content_type
            )
            
            return document_id
            
        except Exception as e:
            # Cleanup on error
            if os.path.exists(upload_path):
                os.unlink(upload_path)
            raise StudyIndexerError(f"Failed to prepare document: {str(e)}")
    
    async def update_document_metadata(
        self,
        document_id: str,
        metadata: Dict[str, Any]
    ) -> None:
        """Update document metadata"""
        try:
            # Get current status
            status = await self.get_document_status(document_id)
            if not status:
                raise DocumentNotFoundError(f"Document {document_id} not found")
            
            # Update metadata
            status["metadata"] = metadata
            
            # Save updated status
            status_path = os.path.join(settings.PROCESSED_DIR, f"{document_id}.json")
            with open(status_path, "w") as f:
                json.dump(status, f, indent=2)
            
            # Update ChromaDB metadata
            collection_name = await self._get_collection_name(document_id)
            await self.chroma.update_metadata(
                collection_name=collection_name,
                where={"document_id": document_id},
                metadata=metadata
            )
            
            logger.info(
                "Document metadata updated [id=%s]",
                document_id
            )
            
        except Exception as e:
            logger.error(
                "Failed to update document metadata %s: %s",
                document_id,
                str(e)
            )
            raise StudyIndexerError(
                message=f"Failed to update document metadata: {str(e)}",
                code="UPDATE_ERROR"
            )
    
    async def index_document(self, document_id: str) -> Dict[str, Any]:
        """Index a document"""
        if not self.ml_enabled:
            raise StudyIndexerError(
                message="ML processing is not available. Please install ML dependencies.",
                code="ML_NOT_AVAILABLE"
            )
            
        if not self.chroma_enabled:
            raise StudyIndexerError(
                message="ChromaDB is not available. Please check ChromaDB connection.",
                code="CHROMA_NOT_AVAILABLE"
            )
            
        try:
            # Ensure general collection is initialized
            if not self._general_collection_initialized:
                await self._ensure_general_collection()
                
            # Get document status
            status = await self.get_document_status(document_id)
            if not status:
                raise DocumentNotFoundError(f"Document {document_id} not found")
                
            # Read file
            file_ext = ALLOWED_MIME_TYPES.get(status["content_type"], ".txt")
            file_path = os.path.join(settings.UPLOAD_DIR, f"{document_id}{file_ext}")
            
            # Process document into chunks
            chunks = self._process_document(file_path)
            if not chunks:
                raise DocumentProcessingError("Document processing resulted in no chunks")
            
            # Get or create collection
            collection_name = await self._get_collection_name(document_id)
            collection = await self._get_or_create_collection(collection_name)
            
            # Prepare base metadata
            base_metadata = {
                "document_id": document_id,
                "title": str(status["metadata"].get("title", "")),
                "author": str(status["metadata"].get("author", "")),
                "course_id": str(status["metadata"].get("course_id", "")),
                "document_type": str(status["metadata"].get("document_type", "text")),
                "collection": str(status["metadata"].get("collection", "general")),
                "tags": ",".join(str(tag) for tag in status["metadata"].get("tags", [])),
                "is_chunk": False,  # This is the parent document
                "parent_document_id": None,  # No parent as this is the original document
                "total_chunks": len(chunks)
            }
            
            # Prepare chunks for indexing
            documents = []
            metadatas = []
            ids = []
            
            for i, chunk in enumerate(chunks):
                # Generate chunk ID
                chunk_id = f"{document_id}_chunk_{i}"
                
                # Create chunk-specific metadata
                chunk_metadata = {
                    **base_metadata,
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "chunk_size": len(chunk["page_content"]),
                    "is_chunk": True,  # Mark as a chunk
                    "parent_document_id": document_id  # Reference to parent document
                }
                
                documents.append(chunk["page_content"])
                metadatas.append(chunk_metadata)
                ids.append(chunk_id)
            
            # Generate embeddings in batches
            batch_size = 32
            for i in range(0, len(documents), batch_size):
                batch_docs = documents[i:i + batch_size]
                batch_meta = metadatas[i:i + batch_size]
                batch_ids = ids[i:i + batch_size]
                
                # Generate embeddings
                embeddings = self.embedder.encode(batch_docs).tolist()
                
                # Add to collection
                await self.chroma.add_documents(
                    collection_name=collection_name,
                    documents=batch_docs,
                    metadatas=batch_meta,
                    ids=batch_ids,
                    embeddings=embeddings
                )
            
            # Update status
            status["status"] = "completed"
            status["indexed_time"] = datetime.utcnow().isoformat()
            status["chunk_count"] = len(chunks)
            status["vector_ids"] = ids
            status["is_chunk"] = False  # This is the parent document
            
            status_path = os.path.join(settings.PROCESSED_DIR, f"{document_id}.json")
            with open(status_path, "w") as f:
                json.dump(status, f, indent=2)
                
            logger.info(
                "Document indexed successfully [id=%s, chunks=%d]",
                document_id,
                len(chunks)
            )
            
            # Return indexing results
            return {
                "success": True,
                "document_id": document_id,
                "chunk_count": len(chunks),
                "vector_ids": ids
            }
            
        except Exception as e:
            logger.error("Failed to index document %s: %s", document_id, str(e))
            # Update status on error
            if 'status' in locals() and status:
                status["status"] = "failed"
                status["error"] = str(e)
                status_path = os.path.join(settings.PROCESSED_DIR, f"{document_id}.json")
                with open(status_path, "w") as f:
                    json.dump(status, f, indent=2)
            raise StudyIndexerError(f"Failed to index document {document_id}: {str(e)}")
    
    async def search(
        self,
        query: str,
        offset: int = 0,
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        collection: Optional[str] = None,
        min_score: float = 0.0
    ) -> Tuple[int, List[SearchResult]]:
        """Search for similar documents with pagination"""
        if not self.ml_enabled:
            raise StudyIndexerError(
                message="Search is not available. Please install ML dependencies.",
                code="ML_NOT_AVAILABLE"
            )
        
        if not self.chroma_enabled:
            raise StudyIndexerError(
                message="ChromaDB is not available. Please check the connection.",
                code="CHROMA_NOT_AVAILABLE"
            )
        
        try:
            # Ensure general collection is initialized
            if not self._general_collection_initialized:
                await self._ensure_general_collection()
                
            # Generate query embedding
            logger.info(f"Generating embedding for query: '{query}'")
            query_embedding = self.embedder.encode(query)
            
            # Prepare collection name
            collection_name = collection if isinstance(collection, str) else "general"
            logger.info(f"Searching in collection: {collection_name}")
            
            # Prepare filters
            where_clause = filters if filters and len(filters) > 0 else {"document_id": {"$ne": ""}}
            
            # Get total count first (with filters but no limit)
            try:
                logger.info(f"Counting matches for query in {collection_name}")
                total_results = await self.chroma.count_matches(
                    collection_name=collection_name,
                    query_embeddings=[query_embedding.tolist()],
                    where=where_clause
                )
                logger.info(f"Found {total_results} total matches")
            except Exception as count_error:
                logger.warning(f"Failed to count matches: {str(count_error)}")
                # Continue with search, assume total is unknown
                total_results = 0
            
            # Perform search with pagination
            logger.info(f"Performing search with limit={limit}, offset={offset}")
            results = await self.chroma.search(
                collection_name=collection_name,
                query_embeddings=[query_embedding.tolist()],
                n_results=limit,
                offset=offset,
                where=where_clause
            )
            
            # Format results
            search_results = []
            if results and results.get('ids') and len(results['ids']) > 0:
                logger.info(f"Processing {len(results['ids'][0])} search results")
                for i in range(len(results['ids'][0])):
                    # Extract document ID from the composite ID
                    doc_id = results['ids'][0][i].split('_')[0]
                    
                    # Normalize score to [0, 1] range
                    distance = float(results['distances'][0][i])
                    score = 1.0 / (1.0 + distance)
                    
                    # Skip results below minimum score
                    if score < min_score:
                        continue
                    
                    # Get page number from metadata
                    metadata = results['metadatas'][0][i] if results.get('metadatas') else {}
                    page = metadata.get('page')
                    if page is not None:
                        page = max(1, page + 1)
                    
                    # Extract content and highlights
                    content = results['documents'][0][i] if results.get('documents') else ""
                    highlights = self._extract_highlights(content, query)
                    
                    # Get position information from metadata
                    position = {}
                    if metadata.get('chunk_index') is not None:
                        position['chunk'] = metadata.get('chunk_index')
                    
                    search_results.append(
                        SearchResult(
                            document_id=doc_id,
                            score=score,
                            content=content,
                            metadata=metadata,
                            page_number=page,
                            position=position if position else None,
                            highlight=highlights
                        )
                    )
            
            logger.info(f"Returning {len(search_results)} formatted search results")
            return total_results, search_results
            
        except Exception as e:
            logger.error(f"Search operation failed: {str(e)}")
            raise SearchError(f"Search operation failed: {str(e)}")
    
    def _extract_highlights(self, content: str, query: str) -> Dict[str, List[str]]:
        """Extract relevant text snippets for highlighting"""
        try:
            highlights = []
            if content and query:
                words = set(query.lower().split())
                sentences = content.split('.')
                
                for sentence in sentences:
                    sentence = sentence.strip()
                    if sentence and any(word in sentence.lower() for word in words):
                        highlights.append(sentence + '.')
            
            return {"text": highlights} if highlights else None
        except Exception as e:
            logger.warning(f"Failed to extract highlights: {str(e)}")
            return None
    
    async def get_document_status(self, document_id: str) -> Dict[str, Any]:
        """Get document processing status"""
        status_path = os.path.join(settings.PROCESSED_DIR, f"{document_id}.json")
        try:
            with open(status_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            raise DocumentNotFoundError(document_id)
    
    async def delete_document(self, document_id: str):
        """Delete a document and its chunks"""
        try:
            # Delete from ChromaDB
            collection_name = await self._get_collection_name(document_id)
            
            # Delete parent document
            await self.chroma.delete_documents(
                collection_name=collection_name,
                where={"document_id": document_id}
            )
            
            # Delete all chunks associated with this document
            await self.chroma.delete_documents(
                collection_name=collection_name,
                where={"parent_document_id": document_id}
            )
            
            # Delete files
            file_path = self._get_document_path(document_id)
            status_path = os.path.join(settings.PROCESSED_DIR, f"{document_id}.json")
            
            if os.path.exists(file_path):
                os.remove(file_path)
            if os.path.exists(status_path):
                os.remove(status_path)
            
            logger.info("Document deleted successfully [id=%s]", document_id)
            
        except Exception as e:
            logger.error(
                "Failed to delete document %s: %s",
                document_id,
                str(e)
            )
            raise StudyIndexerError(
                message=f"Failed to delete document: {str(e)}",
                code="DELETE_ERROR"
            )
    
    async def list_collections(self) -> List[Dict[str, Any]]:
        """List all available collections with stats"""
        try:
            # Ensure general collection is initialized
            if not self._general_collection_initialized:
                await self._ensure_general_collection()
                
            return await self.chroma.list_collections()
        except Exception as e:
            logger.error(f"Failed to list collections: {str(e)}")
            raise StudyIndexerError(
                message=f"Failed to list collections: {str(e)}",
                code="LIST_ERROR"
            )
    
    async def _update_status(
        self,
        document_id: str,
        status: str,
        message: str
    ):
        """Update document processing status"""
        status_path = os.path.join(settings.PROCESSED_DIR, f"{document_id}.json")
        current_status = await self.get_document_status(document_id)
        
        current_status.update({
            "status": status,
            "message": message,
            "updated_at": datetime.utcnow().isoformat()
        })
        
        with open(status_path, 'w') as f:
            json.dump(current_status, f, indent=2)
    
    def _get_document_path(self, document_id: str) -> str:
        """Get the path of an uploaded document"""
        for ext in ['.pdf', '.txt', '.docx', '.md']:
            path = os.path.join(settings.UPLOAD_DIR, f"{document_id}{ext}")
            if os.path.exists(path):
                return path
        raise DocumentNotFoundError(document_id)
    
    def _process_document(self, file_path: str) -> List[Any]:
        """Process a document into chunks"""
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == '.pdf':
            text = self.loader.load_pdf(file_path)
        elif ext == '.txt':
            text = self.loader.load_text(file_path)
        elif ext == '.docx':
            text = self.loader.load_docx(file_path)
        elif ext == '.md':
            text = self.loader.load_markdown(file_path)
        else:
            raise InvalidDocumentError(f"Unsupported file type: {ext}")
        
        chunks = self.text_splitter.split_text(text)
        return [{"page_content": chunk} for chunk in chunks]
    
    async def _get_collection_name(self, document_id: str) -> str:
        """Get the collection name for a document"""
        # Get document metadata from status
        status = await self.get_document_status(document_id)
        metadata = status.get("metadata", {})
        
        # Determine collection based on metadata
        collection = metadata.get("collection", CollectionType.GENERAL)
        if collection == CollectionType.PERSONAL:
            user_id = metadata.get("user_id")
            return f"personal_{user_id}" if user_id else "personal"
        elif collection == CollectionType.COURSE:
            course_id = metadata.get("course_id")
            return f"course_{course_id}" if course_id else "course"
        return collection
    
    async def _get_or_create_collection(self, name: str) -> Collection:
        """Get or create a collection in ChromaDB"""
        # Ensure general collection is initialized
        if not self._general_collection_initialized:
            await self._ensure_general_collection()
            
        return await self.chroma.get_or_create_collection(name)
    
    async def process_document(self, document_id: str) -> Dict[str, Any]:
        """Process and index a document"""
        try:
            logger.info(f"Processing document {document_id}")
            
            # Index the document
            result = await self.index_document(document_id)
            
            # Get metadata from the result
            metadata = {
                "chunks": result.get("chunk_count", 0),
                "pages": 1,  # Default to 1 page for now
                "vector_ids": result.get("vector_ids", [])
            }
            
            # Return success result
            return {
                "success": True,
                "document_id": document_id,
                "metadata": metadata,
                "message": "Document processed successfully"
            }
        except DocumentNotFoundError:
            logger.error(f"Failed to index document {document_id}: Document {document_id} not found")
            return {
                "success": False,
                "document_id": document_id,
                "error": f"Document {document_id} not found"
            }
        except Exception as e:
            logger.error(f"Failed to process document {document_id}: {str(e)}")
            return {
                "success": False,
                "document_id": document_id,
                "error": str(e)
            } 