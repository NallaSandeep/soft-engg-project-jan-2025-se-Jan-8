"""Document management endpoints for StudyIndexer"""
from typing import List, Tuple, Optional
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status, Query, Form, BackgroundTasks
from app.core.auth import require_teacher, require_student, UserContext, get_current_user
from app.core.errors import (
    DocumentNotFoundError,
    InvalidFileTypeError,
    FileSizeTooLargeError,
    StudyIndexerError,
    ValidationError
)
from app.schemas.documents import DocumentMetadata, DocumentResponse, DocumentListResponse, DocumentInfo, DocumentStatus
from app.schemas.base import DocumentType, CollectionType
from app.services.indexer import DocumentIndexer, ALLOWED_MIME_TYPES
from app.core.config import settings
from app.tasks.indexing_tasks import process_document, reindex_document, delete_document
from app.services.tracker import DocumentTracker
import logging
import uuid
import os
from datetime import datetime
import mimetypes
import json
import shutil

logger = logging.getLogger(__name__)
router = APIRouter()
indexer = DocumentIndexer()

async def process_document_results(results: List[dict], seen_docs: set) -> List[DocumentInfo]:
    """Helper function to process document search results into DocumentInfo objects"""
    documents = []
    for result in results:
        doc_id = result.metadata.get("document_id")
        if not doc_id or doc_id in seen_docs:
            continue
            
        seen_docs.add(doc_id)
        
        try:
            # Get document status
            status = await indexer.get_document_status(doc_id)
            
            # Create document info
            doc_info = DocumentInfo(
                document_id=doc_id,
                status=DocumentStatus(status["status"]),
                metadata=DocumentMetadata(
                    title=status["metadata"].get("title", "Untitled"),
                    author=status["metadata"].get("author", "Unknown"),
                    course_id=status["metadata"].get("course_id"),
                    document_type=status["metadata"].get("document_type", "text"),
                    tags=status["metadata"].get("tags", []),
                    collection=status["metadata"].get("collection", "general"),
                    custom_metadata=status["metadata"].get("custom_metadata", {})
                ),
                error=status.get("error")
            )
            documents.append(doc_info)
        except Exception as e:
            logger.warning(f"Failed to get status for document {doc_id}: {str(e)}")
            continue
    
    return documents

@router.post("/", response_model=DocumentResponse)
async def index_document(
    file: UploadFile = File(...),
    title: str = Query(None),
    course_id: str = Query(None),
    document_type: DocumentType = Query(DocumentType.TEXT),
    tags: str = Query(None),
    collection: CollectionType = Query(CollectionType.GENERAL),
    current_user: UserContext = Depends(get_current_user),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Index a new document in the vector store
    """
    try:
        # Generate document ID
        document_id = str(uuid.uuid4())
        
        # Parse tags
        tag_list = []
        if tags:
            tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
        
        # Determine content type
        content_type = file.content_type or mimetypes.guess_type(file.filename)[0] or "text/plain"
        
        # Create metadata
        metadata = {
            "title": title or file.filename,
            "filename": file.filename,
            "document_type": document_type,
            "collection": collection,
            "course_id": course_id,
            "tags": tag_list,
            "user_id": current_user.user_id,
            "upload_time": datetime.now().isoformat()
        }
        
        # Get file extension based on content type
        file_ext = ALLOWED_MIME_TYPES.get(content_type, ".txt")
        
        # Save file to disk with proper extension
        file_path = os.path.join(settings.UPLOAD_DIR, f"{document_id}{file_ext}")
        
        # Ensure upload directory exists
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        
        # Save the file
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Ensure processed directory exists
        os.makedirs(settings.PROCESSED_DIR, exist_ok=True)
        
        # Create initial status file
        status_data = {
            "document_id": document_id,
            "status": DocumentStatus.PENDING,
            "content_type": content_type,
            "file_path": file_path,
            "file_extension": file_ext,
            "metadata": metadata,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # Save status file
        status_path = os.path.join(settings.PROCESSED_DIR, f"{document_id}.json")
        with open(status_path, "w") as f:
            json.dump(status_data, f, indent=2)
        
        # Update document tracker
        document_tracker = DocumentTracker()
        document_tracker.update_document_status(document_id, DocumentStatus.PENDING, metadata)
        
        # Process document in background
        background_tasks.add_task(process_document, document_id)
        
        return DocumentResponse(
            success=True,
            document_id=document_id,
            status=DocumentStatus.PENDING,
            message="Document uploaded and queued for processing"
        )
    
    except Exception as e:
        logger.error(f"Error indexing document: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error indexing document: {str(e)}"
        )

@router.get(
    "/my",
    response_model=DocumentListResponse,
    dependencies=[Depends(require_teacher)]
)
async def list_my_documents(
    current_user: UserContext = Depends(require_teacher)
) -> DocumentListResponse:
    """List all documents uploaded by the current user"""
    try:
        # Get all document status files
        processed_dir = settings.PROCESSED_DIR
        documents = []
        total = 0
        
        if os.path.exists(processed_dir):
            for filename in os.listdir(processed_dir):
                if filename.endswith('.json'):
                    try:
                        with open(os.path.join(processed_dir, filename), 'r') as f:
                            status = json.load(f)
                            
                            # Check if this document belongs to the current user
                            if status.get("metadata", {}).get("user_id") == current_user.user_id:
                                document_id = status.get("document_id")
                                documents.append(DocumentInfo(
                                    document_id=document_id,
                                    status=status.get("status", "unknown"),
                                    metadata=DocumentMetadata(
                                        title=status["metadata"].get("title", "Untitled"),
                                        author=status["metadata"].get("author", "Unknown"),
                                        course_id=status["metadata"].get("course_id"),
                                        document_type=status["metadata"].get("document_type", "text"),
                                        tags=status["metadata"].get("tags", []),
                                        collection=status["metadata"].get("collection", "general"),
                                        custom_metadata=status["metadata"].get("custom_metadata", {})
                                    ),
                                    error=status.get("error")
                                ))
                                total += 1
                    except Exception as e:
                        logger.error(f"Error processing document status file {filename}: {str(e)}")
        
        return DocumentListResponse(
            success=True,
            documents=documents,
            total=total
        )
    except Exception as e:
        logger.error(f"Error listing user documents: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error listing documents: {str(e)}"
        )

@router.get(
    "/course/{course_id}",
    response_model=DocumentListResponse,
    dependencies=[Depends(require_student)]
)
async def list_course_documents(
    course_id: str,
    current_user: UserContext = Depends(require_student)
) -> DocumentListResponse:
    """List all documents for a specific course"""
    try:
        # Search for documents with course filter
        total_results, results = await indexer.search(
            query="",  # Empty query to get all documents
            filters={"course_id": course_id},
            limit=100  # Reasonable limit for course documents
        )
        
        # Process results
        seen_docs = set()
        documents = await process_document_results(results, seen_docs)
        
        return DocumentListResponse(
            success=True,
            documents=documents,
            total=total_results
        )
    except Exception as e:
        logger.error(f"StudyIndexer error when listing course documents [course={course_id}, user={current_user.user_id}]: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list course documents: {str(e)}"
        )

@router.get("/{document_id}", response_model=DocumentInfo)
async def get_document(
    document_id: str,
    current_user: UserContext = Depends(get_current_user)
):
    """
    Get document details by ID
    """
    try:
        # Get document status
        doc_status = await indexer.get_document_status(document_id)
        
        # Create document info
        return DocumentInfo(
            document_id=document_id,
            status=DocumentStatus(doc_status["status"]),
            metadata=DocumentMetadata(
                title=doc_status["metadata"].get("title", "Untitled"),
                author=doc_status["metadata"].get("author", "Unknown"),
                course_id=doc_status["metadata"].get("course_id"),
                document_type=doc_status["metadata"].get("document_type", "text"),
                tags=doc_status["metadata"].get("tags", []),
                collection=doc_status["metadata"].get("collection", "general"),
                custom_metadata=doc_status["metadata"].get("custom_metadata", {})
            ),
            error=doc_status.get("error")
        )
    except DocumentNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {document_id} not found"
        )
    except Exception as e:
        logger.error(f"Error getting document {document_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving document: {str(e)}"
        )

@router.delete("/{document_id}", response_model=DocumentResponse)
async def remove_document(
    document_id: str,
    current_user: UserContext = Depends(require_teacher)
):
    """
    Delete a document from the vector store
    """
    try:
        # Check if document exists
        from app.core.background_tasks import document_tracker
        status = document_tracker.get_status(document_id)
        if not status:
            raise HTTPException(
                status_code=404,
                detail=f"Document {document_id} not found"
            )
        
        # Delete document in a background task
        from app.core.background_tasks import background_tasks
        from app.tasks.indexing_tasks import delete_document
        background_tasks.add_task(delete_document, document_id)
        
        return DocumentResponse(
            success=True,
            document_id=document_id,
            status=DocumentStatus.PENDING,
            message="Document deletion queued"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error deleting document: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting document: {str(e)}"
        )

@router.post("/{document_id}/reindex", response_model=DocumentResponse)
async def reindex_document_endpoint(
    document_id: str,
    current_user: UserContext = Depends(require_teacher)
):
    """
    Reindex a document in the vector store
    """
    try:
        # Check if document exists
        from app.core.background_tasks import document_tracker
        status = document_tracker.get_status(document_id)
        if not status:
            raise HTTPException(
                status_code=404,
                detail=f"Document {document_id} not found"
            )
        
        # Reindex document in a background task
        from app.core.background_tasks import background_tasks
        from app.tasks.indexing_tasks import reindex_document
        background_tasks.add_task(reindex_document, document_id)
        
        return DocumentResponse(
            success=True,
            document_id=document_id,
            status=DocumentStatus.PENDING,
            message="Document reindexing queued"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error reindexing document: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error reindexing document: {str(e)}"
        )

@router.post(
    "/{document_id}/reindex",
    response_model=DocumentResponse,
    dependencies=[Depends(require_student)]
)
async def reindex_document_endpoint(
    document_id: str,
    current_user: UserContext = Depends(require_student),
    background_tasks: BackgroundTasks = BackgroundTasks()
) -> DocumentResponse:
    """Reindex a document"""
    try:
        # Check if document exists
        status = await indexer.get_document_status(document_id)
        if not status:
            raise DocumentNotFoundError(document_id)
            
        # Check if user has permission to reindex this document
        if status.get("user_id") != current_user.user_id and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to reindex this document"
            )
            
        # Reindex document in background
        background_tasks.add_task(reindex_document, document_id)
        
        logger.info(
            "Document reindexing initiated [id=%s, user=%s]",
            document_id,
            current_user.user_id
        )
        
        return DocumentResponse(
            success=True,
            document_id=document_id,
            status=DocumentStatus.PENDING,
            message="Document reindexing initiated"
        )
        
    except DocumentNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {document_id} not found"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to reindex document [id=%s, user=%s]: %s",
            document_id,
            current_user.user_id,
            str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reindex document: {str(e)}"
        )

@router.delete(
    "/{document_id}",
    response_model=DocumentResponse,
    dependencies=[Depends(require_student)]
)
async def delete_document_endpoint(
    document_id: str,
    current_user: UserContext = Depends(require_student),
    background_tasks: BackgroundTasks = BackgroundTasks()
) -> DocumentResponse:
    """Delete a document and all its chunks"""
    try:
        # Check if document exists
        status = await indexer.get_document_status(document_id)
        if not status:
            raise DocumentNotFoundError(document_id)
            
        # Check if user has permission to delete this document
        if status.get("user_id") != current_user.user_id and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to delete this document"
            )
            
        # Delete document in background
        background_tasks.add_task(delete_document, document_id)
        
        logger.info(
            "Document deletion initiated [id=%s, user=%s]",
            document_id,
            current_user.user_id
        )
        
        return DocumentResponse(
            success=True,
            document_id=document_id,
            message="Document deletion initiated"
        )
        
    except DocumentNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {document_id} not found"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to delete document [id=%s, user=%s]: %s",
            document_id,
            current_user.user_id,
            str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete document: {str(e)}"
        )

@router.get(
    "/{document_id}/status",
    response_model=DocumentResponse,
    dependencies=[Depends(require_student)]
)
async def get_document_status_endpoint(
    document_id: str,
    current_user: UserContext = Depends(require_student)
) -> DocumentResponse:
    """Get the current status of a document"""
    try:
        # Check if document exists
        status = await indexer.get_document_status(document_id)
        if not status:
            raise DocumentNotFoundError(document_id)
            
        # Check if user has permission to view this document
        if status.get("user_id") != current_user.user_id and current_user.role != "admin":
            # For course documents, check if user is enrolled in the course
            course_id = status.get("metadata", {}).get("course_id")
            if not course_id or course_id not in current_user.courses:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't have permission to view this document"
                )
        
        # Extract relevant information
        doc_status = DocumentStatus(status.get("status", "unknown"))
        metadata = status.get("metadata", {})
        error = status.get("error")
        chunk_count = status.get("chunk_count", 0)
        indexed_time = status.get("indexed_time")
        
        return DocumentResponse(
            success=True,
            document_id=document_id,
            status=doc_status,
            metadata=metadata,
            error=error,
            message=f"Document status: {doc_status}",
            details={
                "chunk_count": chunk_count,
                "indexed_at": indexed_time
            }
        )
        
    except DocumentNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {document_id} not found"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to get document status [id=%s, user=%s]: %s",
            document_id,
            current_user.user_id,
            str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get document status: {str(e)}"
        ) 