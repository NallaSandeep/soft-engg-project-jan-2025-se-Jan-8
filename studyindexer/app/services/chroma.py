"""ChromaDB service for vector storage and retrieval"""
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
from chromadb.api.models.Collection import Collection
import logging
import shutil
import os
import time
from app.core.config import settings
from app.core.errors import StudyIndexerError

logger = logging.getLogger(__name__)

class ChromaService:
    """Service class for ChromaDB operations"""
    
    _instance = None
    _client = None
    
    def __new__(cls):
        """Singleton pattern to ensure only one ChromaDB client instance"""
        if cls._instance is None:
            cls._instance = super(ChromaService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize ChromaDB client"""
        if self._initialized:
            return
            
        try:
            # Initialize client with consistent settings
            if ChromaService._client is None:
                # Ensure directory exists
                os.makedirs(settings.CHROMA_PERSIST_DIR, exist_ok=True)
                
                ChromaService._client = chromadb.PersistentClient(
                    path=settings.CHROMA_PERSIST_DIR,
                    settings=ChromaSettings(
                        allow_reset=True,
                        anonymized_telemetry=False,
                        is_persistent=True
                    )
                )
            
            self.client = ChromaService._client
            self._initialized = True
            logger.info(
                "ChromaDB client initialized [persist_dir=%s]",
                settings.CHROMA_PERSIST_DIR
            )
        except Exception as e:
            logger.error("Failed to initialize ChromaDB client: %s", str(e))
            raise StudyIndexerError(
                message="Failed to initialize vector database",
                code="DB_INIT_ERROR"
            )
    
    def get_or_create_collection(
        self,
        name: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Get or create a collection"""
        try:
            # Ensure metadata is not empty
            default_metadata = {
                "description": f"Collection for {name}",
                "created_by": "StudyIndexer",
                "version": settings.VERSION,
                "hnsw:space": "cosine",  # Specify distance metric
                "hnsw:construction_ef": 100,  # Index construction parameter
                "hnsw:search_ef": 50  # Search accuracy parameter
            }
            if metadata:
                default_metadata.update(metadata)
            
            # Try to get existing collection
            try:
                collection = self.client.get_collection(name=name)
                logger.info(f"Retrieved existing collection: {name}")
                return collection
            except ValueError:
                # Collection doesn't exist, create it
                logger.info(f"Creating new collection: {name}")
                try:
                    collection = self.client.create_collection(
                        name=name,
                        metadata=default_metadata
                    )
                    logger.info(f"Successfully created collection: {name}")
                    return collection
                except Exception as create_error:
                    logger.error(f"Failed to create collection {name}: {str(create_error)}")
                    # Try to create a general collection as fallback
                    if name != "general":
                        logger.info("Attempting to use general collection as fallback")
                        return self.get_or_create_collection("general", metadata)
                    raise StudyIndexerError(
                        message=f"Failed to create collection {name}",
                        code="COLLECTION_ERROR"
                    )
                
        except Exception as e:
            logger.error(
                "Failed to get/create collection %s: %s",
                name,
                str(e)
            )
            raise StudyIndexerError(
                message=f"Failed to access collection {name}",
                code="COLLECTION_ERROR"
            )
    
    def add_documents(
        self,
        collection_name: str,
        documents: List[str],
        embeddings: List[List[float]],
        metadatas: List[Dict[str, Any]],
        ids: List[str]
    ) -> None:
        """Add documents to a collection"""
        try:
            collection = self.get_or_create_collection(collection_name)
            collection.add(
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(
                "Added %d documents to collection %s",
                len(documents),
                collection_name
            )
        except Exception as e:
            logger.error(
                "Failed to add documents to collection %s: %s",
                collection_name,
                str(e)
            )
            raise StudyIndexerError(
                message="Failed to store documents",
                code="STORAGE_ERROR"
            )
    
    def update_metadata(
        self,
        collection_name: str,
        where: Dict[str, Any],
        metadata: Dict[str, Any]
    ) -> None:
        """Update metadata for documents matching the where clause"""
        try:
            collection = self.get_or_create_collection(collection_name)
            
            # Get documents matching the where clause
            results = collection.get(where=where)
            if not results or not results['ids']:
                return
                
            # Update metadata for each document
            for i, doc_id in enumerate(results['ids']):
                # Merge existing metadata with new metadata
                existing_metadata = results['metadatas'][i] if results.get('metadatas') else {}
                updated_metadata = {**existing_metadata, **metadata}
                
                # Update the document
                collection.update(
                    ids=[doc_id],
                    metadatas=[updated_metadata]
                )
            
            logger.info(
                "Updated metadata for %d documents in collection %s",
                len(results['ids']),
                collection_name
            )
            
        except Exception as e:
            logger.error(
                "Failed to update metadata in collection %s: %s",
                collection_name,
                str(e)
            )
            raise StudyIndexerError(
                message="Failed to update metadata",
                code="UPDATE_ERROR"
            )
    
    def search(
        self,
        collection_name: str,
        query_embeddings: List[List[float]],
        n_results: int = 10,
        offset: int = 0,
        where: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Search for similar documents with pagination"""
        try:
            collection = self.get_or_create_collection(collection_name)
            
            # Prepare where clause
            where_clause = {}
            if where:
                # Handle $or operator
                if "$or" in where:
                    conditions = where["$or"]
                    if len(conditions) >= 2:
                        where_clause = {"$or": conditions}
                    elif len(conditions) == 1:
                        where_clause = conditions[0]
                # Handle $and operator
                elif "$and" in where:
                    conditions = where["$and"]
                    if len(conditions) >= 2:
                        where_clause = {"$and": conditions}
                    elif len(conditions) == 1:
                        where_clause = conditions[0]
                else:
                    # Direct field comparison
                    where_clause = where

                # Clean up any None values to prevent $exists operator
                def clean_none_values(d):
                    if isinstance(d, dict):
                        return {k: clean_none_values(v) if isinstance(v, (dict, list)) else ('' if v is None else v) 
                               for k, v in d.items()}
                    elif isinstance(d, list):
                        return [clean_none_values(x) if isinstance(x, (dict, list)) else ('' if x is None else x) 
                               for x in d]
                    return d

                where_clause = clean_none_values(where_clause)
            
            results = collection.query(
                query_embeddings=query_embeddings,
                n_results=n_results + offset,  # Get extra results for offset
                where=where_clause
            )
            
            # Apply offset to results
            if offset > 0 and offset < len(results['ids'][0]):
                for key in results:
                    if isinstance(results[key], list) and results[key]:
                        results[key][0] = results[key][0][offset:offset + n_results]
            
            logger.info(
                "Search completed in collection %s [results=%d, offset=%d]",
                collection_name,
                len(results['ids'][0]),
                offset
            )
            return results
            
        except Exception as e:
            logger.error(
                "Failed to search in collection %s: %s",
                collection_name,
                str(e)
            )
            raise StudyIndexerError(
                message="Search operation failed",
                code="SEARCH_ERROR"
            )
    
    def count_matches(
        self,
        collection_name: str,
        query_embeddings: List[List[float]],
        where: Optional[Dict[str, Any]] = None
    ) -> int:
        """Count total matches for a query"""
        try:
            collection = self.get_or_create_collection(collection_name)
            
            # Prepare where clause
            where_clause = where if where else {}
            
            # If using $and or $or operators, ensure they have at least two conditions
            if "$and" in where_clause and len(where_clause["$and"]) < 2:
                where_clause = where_clause["$and"][0] if where_clause["$and"] else {}
            if "$or" in where_clause and len(where_clause["$or"]) < 2:
                where_clause = where_clause["$or"][0] if where_clause["$or"] else {}
            
            # Get maximum possible results to count total matches
            results = collection.query(
                query_embeddings=query_embeddings,
                n_results=10000,  # Large number to get all matches
                where=where_clause
            )
            return len(results['ids'][0])
            
        except Exception as e:
            logger.error(
                "Failed to count matches in collection %s: %s",
                collection_name,
                str(e)
            )
            raise StudyIndexerError(
                message="Failed to count matches",
                code="COUNT_ERROR"
            )
    
    def delete_documents(
        self,
        collection_name: str,
        ids: Optional[List[str]] = None,
        where: Optional[Dict[str, Any]] = None
    ) -> None:
        """Delete documents from a collection"""
        try:
            collection = self.get_or_create_collection(collection_name)
            if ids:
                collection.delete(ids=ids)
            elif where:
                collection.delete(where=where)
            logger.info(
                "Deleted documents from collection %s [ids=%s, where=%s]",
                collection_name,
                ids,
                where
            )
        except Exception as e:
            logger.error(
                "Failed to delete documents from collection %s: %s",
                collection_name,
                str(e)
            )
            raise StudyIndexerError(
                message="Failed to delete documents",
                code="DELETE_ERROR"
            )
    
    async def get_collection_stats(self, collection_name: str) -> Dict[str, Any]:
        """Get statistics for a collection"""
        try:
            collection = self.get_or_create_collection(collection_name)
            count = collection.count()
            return {
                "document_count": count,
                "name": collection_name,
                "metadata": collection.metadata
            }
        except Exception as e:
            logger.error(f"Failed to get stats for collection {collection_name}: {str(e)}")
            return {
                "document_count": 0,
                "name": collection_name,
                "metadata": {}
            }
    
    async def list_collections(self) -> List[Dict[str, Any]]:
        """List all available collections with stats"""
        try:
            collections = self.client.list_collections()
            result = []
            
            for collection in collections:
                try:
                    stats = await self.get_collection_stats(collection.name)
                    result.append({
                        "name": collection.name,
                        "document_count": stats.get("document_count", 0),
                        "metadata": collection.metadata
                    })
                except Exception as e:
                    logger.warning(f"Failed to get stats for collection {collection.name}: {str(e)}")
                    result.append({
                        "name": collection.name,
                        "document_count": 0,
                        "metadata": collection.metadata
                    })
            
            return result
        except Exception as e:
            logger.error(f"Failed to list collections: {str(e)}")
            raise StudyIndexerError(
                message="Failed to list collections",
                code="LIST_ERROR"
            ) 