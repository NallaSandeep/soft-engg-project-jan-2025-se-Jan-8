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
from datetime import datetime

# Use the root logger instead of a specialized one
logger = logging.getLogger()

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
    
    @staticmethod
    def enable_debug_logging():
        """Enable debug logging for ChromaDB-related operations"""
        # Set up more verbose logging for this module
        module_logger = logging.getLogger('app.services.chroma')
        module_logger.setLevel(logging.DEBUG)
        
        # Also enable debug logging for ChromaDB client if possible
        try:
            chroma_logger = logging.getLogger('chromadb')
            chroma_logger.setLevel(logging.DEBUG)
        except Exception as e:
            logger.warning(f"Failed to enable ChromaDB debug logging: {str(e)}")
            
        logger.info("Enabled debug logging for ChromaDB operations")
    
    def __init__(self):
        """Initialize ChromaDB client"""
        if hasattr(self, '_initialized') and self._initialized:
            return
            
        try:
            # Enable debug logging
            self.enable_debug_logging()
            
            logger.info("Initializing ChromaDB client with HTTP connection")
            self._connect()
            
            # Verify connection is working
            try:
                self._client.heartbeat()
                logger.info("ChromaDB client initialized successfully")
                self._initialized = True
            except Exception as e:
                logger.error(f"ChromaDB connection test failed after initialization: {str(e)}")
                raise
        except Exception as e:
            logger.error("Failed to initialize ChromaDB client: %s", str(e))
            raise StudyIndexerError(
                message="Failed to initialize vector database",
                code="DB_INIT_ERROR"
            )
    
    def _connect(self):
        """Connect to ChromaDB server"""
        import chromadb
        self._client = chromadb.HttpClient(
            host=settings.CHROMA_CONNECT_HOST,
            port=settings.CHROMA_PORT
        )
        # Test connection
        try:
            self._client.heartbeat()
        except Exception as e:
            logger.error("ChromaDB connection test failed: %s", str(e))
            raise
    
    def _ensure_connection(self, force_reconnect=False):
        """Ensure connection is active, reconnect if needed"""
        if force_reconnect or not self._client:
            logger.debug("Forcing reconnection to ChromaDB")
            self._connect()
            if not self._client:
                logger.error("Failed to establish connection to ChromaDB - client is None")
                raise StudyIndexerError(
                    message="Failed to establish connection to ChromaDB - client is None",
                    code="CONNECTION_ERROR"
                )

        for attempt in range(3):
            try:
                self._client.heartbeat()
                logger.debug("ChromaDB connection is healthy")
                return
            except Exception as e:
                logger.exception(f"Connection attempt {attempt + 1} failed: {str(e)}")
                if attempt < 2:
                    sleep_time = 0.5 * (2 ** attempt)
                    logger.debug(f"Retrying connection after {sleep_time} seconds")
                    time.sleep(sleep_time)
                    self._connect()
                else:
                    raise StudyIndexerError(
                        message="Failed to establish connection to ChromaDB after retries",
                        code="CONNECTION_ERROR"
                    )
    
    async def get_or_create_collection(
        self,
        name: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Get or create a collection"""
        max_retries = 3
        retry_count = 0
        backoff_time = 0.5
        
        while retry_count < max_retries:
            try:
                # Ensure connection is active
                self._ensure_connection()
                
                # Ensure metadata is not empty
                default_metadata = {
                    "description": f"Collection for {name}",
                    "created_by": "StudyIndexer",
                    "version": settings.VERSION,
                    "created_at": datetime.utcnow().isoformat()
                }
                
                # Merge provided metadata with defaults
                collection_metadata = default_metadata.copy()
                if metadata:
                    collection_metadata.update(metadata)
                
                # Try to get existing collection first
                try:
                    logger.debug(f"Attempting to get existing collection: {name}")
                    collection = self._client.get_collection(name=name)
                    logger.debug(f"Found existing collection: {name}")
                    return collection
                except Exception as e:
                    # Collection doesn't exist, create it
                    if "does not exist" in str(e) or "not found" in str(e).lower():
                        logger.info(f"Collection {name} not found, creating new collection")
                        try:
                            # Add a small delay before creating collection to avoid connection reset
                            time.sleep(0.5)
                            collection = self._client.create_collection(
                                name=name,
                                metadata=collection_metadata
                            )
                            logger.info(f"Created new collection: {name}")
                            return collection
                        except Exception as create_error:
                            # If creation fails due to collection already existing, try to get it again
                            if "already exists" in str(create_error).lower():
                                logger.warning(f"Collection {name} already exists, retrieving it")
                                collection = self._client.get_collection(name=name)
                                return collection
                            else:
                                raise create_error
                    else:
                        # Some other error occurred
                        raise e
                    
            except Exception as e:
                retry_count += 1
                error_str = str(e)
                
                # Check for connection errors
                if "Broken pipe" in error_str or "Connection reset" in error_str or "Connection refused" in error_str:
                    logger.warning(
                        "Connection error during get_or_create_collection, retrying (%d/%d): %s",
                        retry_count,
                        max_retries,
                        error_str
                    )
                    
                    # Implement exponential backoff
                    if retry_count < max_retries:
                        logger.info(f"Waiting {backoff_time} seconds before retry...")
                        time.sleep(backoff_time)
                        backoff_time *= 2
                        
                        # Force reconnect
                        try:
                            self._ensure_connection(force_reconnect=True)
                        except Exception as reconnect_error:
                            logger.error(f"Failed to reconnect: {str(reconnect_error)}")
                else:
                    # Not a connection error, don't retry
                    logger.error(f"Error getting or creating collection {name}: {error_str}")
                    raise StudyIndexerError(
                        message=f"Failed to get or create collection {name}: {error_str}",
                        code="COLLECTION_ERROR"
                    )
        
        # If we got here, all retries failed
        logger.error(f"All {max_retries} attempts to get or create collection {name} failed")
        raise StudyIndexerError(
            message=f"Failed to get or create collection {name} after {max_retries} attempts",
            code="COLLECTION_ERROR"
        )
    
    def get_or_create_collection_sync(
        self,
        name: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Get or create a collection (synchronous version)"""
        max_retries = 3
        retry_count = 0
        backoff_time = 0.5
        
        while retry_count < max_retries:
            try:
                # Ensure connection is active
                self._ensure_connection()
                
                # Ensure metadata is not empty
                default_metadata = {
                    "description": f"Collection for {name}",
                    "created_by": "StudyIndexer",
                    "version": settings.VERSION,
                    "created_at": datetime.utcnow().isoformat()
                }
                
                # Merge provided metadata with defaults
                collection_metadata = default_metadata.copy()
                if metadata:
                    collection_metadata.update(metadata)
                
                # Try to get existing collection first
                try:
                    logger.debug(f"Attempting to get existing collection: {name}")
                    collection = self._client.get_collection(name=name)
                    logger.debug(f"Found existing collection: {name}")
                    return collection
                except Exception as e:
                    # Collection doesn't exist, create it
                    if "does not exist" in str(e) or "not found" in str(e).lower():
                        logger.info(f"Collection {name} not found, creating new collection")
                        try:
                            # Add a small delay before creating collection to avoid connection reset
                            time.sleep(0.5)
                            collection = self._client.create_collection(
                                name=name,
                                metadata=collection_metadata
                            )
                            logger.info(f"Created new collection: {name}")
                            return collection
                        except Exception as create_error:
                            # If creation fails due to collection already existing, try to get it again
                            if "already exists" in str(create_error).lower():
                                logger.warning(f"Collection {name} already exists, retrieving it")
                                collection = self._client.get_collection(name=name)
                                return collection
                            else:
                                raise create_error
                    else:
                        # Some other error occurred
                        raise e
                    
            except Exception as e:
                retry_count += 1
                error_str = str(e)
                
                # Check for connection errors
                if "Broken pipe" in error_str or "Connection reset" in error_str or "Connection refused" in error_str:
                    logger.warning(
                        "Connection error during get_or_create_collection_sync, retrying (%d/%d): %s",
                        retry_count,
                        max_retries,
                        error_str
                    )
                    
                    # Implement exponential backoff
                    if retry_count < max_retries:
                        logger.info(f"Waiting {backoff_time} seconds before retry...")
                        time.sleep(backoff_time)
                        backoff_time *= 2
                        
                        # Force reconnect
                        try:
                            self._ensure_connection(force_reconnect=True)
                        except Exception as reconnect_error:
                            logger.error(f"Failed to reconnect: {str(reconnect_error)}")
                else:
                    # Not a connection error, don't retry
                    logger.error(f"Error getting or creating collection {name}: {error_str}")
                    raise StudyIndexerError(
                        message=f"Failed to get or create collection {name}: {error_str}",
                        code="COLLECTION_ERROR"
                    )
        
        # If we got here, all retries failed
        logger.error(f"All {max_retries} attempts to get or create collection {name} failed")
        raise StudyIndexerError(
            message=f"Failed to get or create collection {name} after {max_retries} attempts",
            code="COLLECTION_ERROR"
        )
    
    async def add_documents(
        self,
        collection_name: str,
        documents: List[str],
        embeddings: List[List[float]],
        metadatas: List[Dict[str, Any]],
        ids: List[str]
    ) -> None:
        """Add documents to a collection"""
        try:
            collection = await self.get_or_create_collection(collection_name)
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
    
    async def update_metadata(
        self,
        collection_name: str,
        where: Dict[str, Any],
        metadata: Dict[str, Any]
    ) -> None:
        """Update metadata for documents matching the where clause"""
        try:
            collection = await self.get_or_create_collection(collection_name)
            
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
    
    async def search(
        self,
        collection_name: str,
        query_embeddings: List[List[float]],
        n_results: int = 10,
        offset: int = 0,
        where: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Search for similar documents with pagination"""
        self._ensure_connection(force_reconnect=True)
        logger.debug(f"Starting search in collection '{collection_name}' with embeddings: {query_embeddings}, n_results: {n_results}, offset: {offset}, filters: {where}")

        for attempt in range(7):
            try:
                collection = await self.get_or_create_collection(collection_name)
                results = collection.query(
                    query_embeddings=query_embeddings,
                    n_results=n_results + offset,
                    where=where
                )
                logger.debug(f"Search successful on attempt {attempt + 1}")
                return results

            except Exception as e:
                logger.exception(f"Search attempt {attempt + 1} failed due to exception: {str(e)}")
                if attempt < 6:
                    sleep_time = 0.5 * (2 ** attempt)
                    logger.debug(f"Retrying search after {sleep_time} seconds")
                    time.sleep(sleep_time)
                    self._ensure_connection(force_reconnect=True)
                else:
                    raise StudyIndexerError(
                        message=f"Search operation failed after retries: {str(e)}",
                        code="SEARCH_ERROR"
                    )
    
    async def count_matches(
        self,
        collection_name: str,
        query_embeddings: List[List[float]],
        where: Optional[Dict[str, Any]] = None
    ) -> int:
        """Count total matches for a query"""
        try:
            collection = await self.get_or_create_collection(collection_name)
            
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
    
    async def delete_documents(
        self,
        collection_name: str,
        ids: Optional[List[str]] = None,
        where: Optional[Dict[str, Any]] = None
    ) -> None:
        """Delete documents from a collection"""
        try:
            collection = await self.get_or_create_collection(collection_name)
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
    
    async def list_collections(self) -> List[Dict[str, Any]]:
        """List all collections with their stats"""
        try:
            # Force a fresh connection to avoid stale connection issues
            self._ensure_connection(force_reconnect=True)
            
            # Get all collections - in v0.6.0+ this returns only names
            logger.info("Listing ChromaDB collections...")
            collections_list = self._client.list_collections()
            logger.info(f"Found {len(collections_list)} collections")
            
            result = []
            
            # Handle different versions of ChromaDB
            # In v0.6.0+, list_collections returns a list of collection names (strings)
            if collections_list and isinstance(collections_list, list):
                if collections_list and isinstance(collections_list[0], str):
                    # v0.6.0+ format - list of strings
                    logger.info("Using ChromaDB v0.6.3 collection listing format (list of strings)")
                    for collection_name in collections_list:
                        try:
                            logger.debug(f"Getting collection: {collection_name}")
                            collection = self._client.get_collection(collection_name)
                            count = collection.count()
                            
                            # Get metadata if available
                            metadata = {}
                            try:
                                if hasattr(collection, '_metadata'):
                                    metadata = collection._metadata
                                elif hasattr(collection, 'metadata'):
                                    metadata = collection.metadata
                            except Exception as meta_err:
                                logger.warning(f"Could not get metadata for {collection_name}: {str(meta_err)}")
                            
                            result.append({
                                "name": collection_name,
                                "document_count": count,
                                "metadata": metadata
                            })
                            logger.debug(f"Added collection {collection_name} with {count} documents")
                        except Exception as e:
                            logger.warning(f"Failed to get stats for collection {collection_name}: {str(e)}")
                            # Include collection with zero count
                            result.append({
                                "name": collection_name,
                                "document_count": 0,
                                "metadata": {}
                            })
                elif collections_list and hasattr(collections_list[0], 'name'):
                    # Pre v0.6.0 format - list of collection objects
                    logger.info("Using pre-v0.6.0 collection listing format (list of objects)")
                    for collection_info in collections_list:
                        try:
                            collection_name = collection_info.name
                            collection = self._client.get_collection(collection_name)
                            count = collection.count()
                            
                            result.append({
                                "name": collection_name,
                                "document_count": count,
                                "metadata": collection_info.metadata if hasattr(collection_info, 'metadata') else {}
                            })
                        except Exception as e:
                            logger.warning(f"Failed to get stats for collection {collection_info.name}: {str(e)}")
                            # Include collection with zero count
                            result.append({
                                "name": collection_info.name,
                                "document_count": 0,
                                "metadata": collection_info.metadata if hasattr(collection_info, 'metadata') else {}
                            })
                else:
                    # Unknown format
                    logger.warning(f"Unknown collection list format: {type(collections_list[0])}")
                    # Try to handle it generically
                    for item in collections_list:
                        if isinstance(item, str):
                            name = item
                        elif hasattr(item, 'name'):
                            name = item.name
                        else:
                            name = str(item)
                        
                        result.append({
                            "name": name,
                            "document_count": 0,
                            "metadata": {}
                        })
            
            logger.info(f"Successfully processed {len(result)} collections")
            return result
        except Exception as e:
            logger.error(f"Failed to list collections: {str(e)}")
            raise StudyIndexerError(
                message=f"Failed to list collections: {str(e)}",
                code="LIST_ERROR"
            )
    
    async def get_collection_stats(self, collection_name: str) -> Dict[str, Any]:
        """Get statistics for a collection"""
        try:
            collection = await self.get_or_create_collection(collection_name)
            count = collection.count()
            return {
                "document_count": count,
                "name": collection_name,
                "metadata": {}
            }
        except Exception as e:
            logger.error(f"Failed to get stats for collection {collection_name}: {str(e)}")
            return {
                "document_count": 0,
                "name": collection_name,
                "metadata": {}
            }
    
    def add_documents_sync(
        self,
        collection_name: str,
        documents: List[str],
        embeddings: List[List[float]],
        metadatas: List[Dict[str, Any]],
        ids: List[str]
    ) -> None:
        """Add documents to a collection (synchronous version)"""
        try:
            collection = self.get_or_create_collection_sync(collection_name)
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
            
    def search_sync(
        self,
        collection_name: str,
        query_embeddings: List[List[float]],
        n_results: int = 10,
        offset: int = 0,
        where: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Search for documents in a collection (synchronous version)"""
        try:
            collection = self.get_or_create_collection_sync(collection_name)
            
            # Perform search
            results = collection.query(
                query_embeddings=query_embeddings,
                n_results=n_results,
                where=where
            )
            
            # Apply offset if needed
            if offset > 0 and results and 'ids' in results:
                for key in results:
                    if isinstance(results[key], list):
                        results[key] = results[key][offset:]
            
            return results
        except Exception as e:
            logger.error(
                "Failed to search collection %s: %s",
                collection_name,
                str(e)
            )
            raise StudyIndexerError(
                message="Failed to search documents",
                code="SEARCH_ERROR"
            )
            
    def delete_documents_sync(
        self,
        collection_name: str,
        ids: Optional[List[str]] = None,
        where: Optional[Dict[str, Any]] = None
    ) -> None:
        """Delete documents from a collection (synchronous version)"""
        try:
            collection = self.get_or_create_collection_sync(collection_name)
            
            # Delete documents
            collection.delete(
                ids=ids,
                where=where
            )
            
            logger.info(
                "Deleted documents from collection %s (ids: %s, where: %s)",
                collection_name,
                ids if ids else "None",
                where if where else "None"
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