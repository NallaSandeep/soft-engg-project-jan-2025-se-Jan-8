"""
ChromaDB service for managing vector database collections
"""
import os
import chromadb
from chromadb.config import Settings
from chromadb.api.models.Collection import Collection
from typing import List, Dict, Any, Optional, Tuple, Union
from .embeddings import EmbeddingService, ChromaEmbeddingFunction
import logging
import asyncio
import concurrent.futures
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class ChromadbResult(BaseModel):
    """Class to hold search results from ChromaDB in a structured way"""
    ids: List[str]
    documents: List[str]
    metadatas: List[Dict[str, Any]]
    distances: List[float]
    embeddings: Optional[List[List[float]]] = None


class ChromaService:
    """Service for managing interactions with ChromaDB"""
    
    _instance = None
    
    def __new__(cls):
        """Singleton pattern to ensure only one client is created"""
        if cls._instance is None:
            cls._instance = super(ChromaService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the ChromaDB client"""
        if getattr(self, '_initialized', False):
            logger.info("ChromaDB service already initialized")
            return
            
        # Configure ChromaDB settings
        self.persistent_dir = os.environ.get("CHROMA_PERSISTENCE_DIR", "./data/chroma")
        os.makedirs(self.persistent_dir, exist_ok=True)
        logger.info(f"Using ChromaDB persistence directory: {self.persistent_dir}")
        
        # Initialize embedding service
        logger.info("Initializing embedding service...")
        self.embedding_service = EmbeddingService()
        self.embedding_function = ChromaEmbeddingFunction(self.embedding_service)
        
        try:
            # Initialize client with new API format
            logger.info("Initializing ChromaDB HTTP client...")
            self.client = chromadb.HttpClient(
                host="127.0.0.1",
                port=int(os.environ.get("CHROMA_PORT", "8000"))
            )
            self._initialized = True
            self.collections = {}  # Cache for collections
            logger.info("ChromaDB initialized successfully with HTTP client")
        except Exception as e:
            logger.error(f"Error initializing ChromaDB: {str(e)}")
            self.client = None
            self._initialized = False
            raise
    
    # Synchronous wrapper methods
    def get_or_create_collection_sync(self, name: str, metadata: Optional[Dict[str, Any]] = None) -> Collection:
        """Synchronous wrapper for get_or_create_collection"""
        try:
            if not self._initialized or self.client is None:
                raise ValueError("ChromaDB client not initialized")
                
            # Use cached collection if available
            if name in self.collections:
                logger.info(f"Using cached collection: {name}")
                return self.collections[name]
                
            # Create or get collection directly
            logger.info(f"Creating/getting collection: {name}")
            collection = self.client.get_or_create_collection(
                name=name,
                metadata=metadata,
                embedding_function=self.embedding_function
            )
            
            # Cache the collection
            self.collections[name] = collection
            logger.info(f"Collection {name} created/retrieved successfully")
            return collection
        except Exception as e:
            logger.error(f"Error in get_or_create_collection_sync: {str(e)}")
            raise
            
    def add_documents_sync(
        self, 
        collection_name: str,
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None,
        embeddings: Optional[List[List[float]]] = None
    ) -> List[str]:
        """Synchronous wrapper for add_documents"""
        try:
            if not self._initialized or self.client is None:
                raise ValueError("ChromaDB client not initialized")
                
            logger.info(f"Adding {len(documents)} documents to collection {collection_name}")
            collection = self.get_or_create_collection_sync(collection_name)
            
            # Generate IDs if not provided
            if ids is None:
                ids = [f"doc_{i}" for i in range(len(documents))]
                
            # Add documents directly
            collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids,
                embeddings=embeddings
            )
            
            logger.info(f"Successfully added {len(documents)} documents to collection {collection_name}")
            return ids
        except Exception as e:
            logger.error(f"Error in add_documents_sync: {str(e)}")
            raise
            
    def search_sync(
        self,
        collection_name: str,
        query: str,
        n_results: int = 10,
        where: Optional[Dict[str, Any]] = None,
        query_embedding: Optional[List[float]] = None,
        include: Optional[List[str]] = None
    ) -> ChromadbResult:
        """Synchronous wrapper for search"""
        try:
            if not self._initialized or self.client is None:
                raise ValueError("ChromaDB client not initialized")
                
            logger.info(f"Searching collection {collection_name} with query: '{query}'")
            if where:
                logger.info(f"Using filter: {where}")
                
            collection = self.get_or_create_collection_sync(collection_name)
            
            # Prepare query parameters
            query_params = {
                "n_results": n_results
            }
            
            # Add where filter if provided
            if where is not None:
                query_params["where"] = where

            # Add include parameter if provided
            if include is not None:
                query_params["include"] = include
            else:
                # Default include values if not specified
                query_params["include"] = ["metadatas", "documents", "distances"]
            
            # Determine which query method to use
            if query_embedding is not None:
                logger.info("Using embedding-based search")
                # Use embedding search
                query_params["query_embeddings"] = [query_embedding]
            elif query and len(query.strip()) > 0:
                logger.info("Using text-based search")
                # Use text search if no embedding but valid query text
                query_params["query_texts"] = [query]
            else:
                logger.info("Using empty query fallback")
                # Emergency fallback - use empty query
                query_params["query_texts"] = [""]
                
            try:
                # Execute query directly
                logger.info(f"Executing search with parameters: {query_params}")
                result = collection.query(**query_params)
                logger.info(f"Search returned {len(result.get('ids',[[]])[0]) if result.get('ids') else 0} results")
            except Exception as e:
                # Provide detailed error for debugging
                raise Exception(f"ChromaDB query failed: {str(e)} with params: {query_params}")
                
            # Check if result is None or missing expected keys
            if result is None or not isinstance(result, dict):
                logger.error("ChromaDB query returned None or unexpected type")
                # Return an empty result to prevent downstream errors
                return ChromadbResult(ids=[], documents=[], metadatas=[], distances=[])

            # Process results, handling potential missing keys or None values gracefully
            # Always expect 'ids' to be present in a valid non-error response
            ids_list = result.get("ids")
            ids = ids_list[0] if ids_list and isinstance(ids_list, list) and len(ids_list) > 0 else []
            num_results = len(ids)

            # Safely get other fields based on potential inclusion
            distances_list = result.get("distances")
            distances = distances_list[0] if distances_list and isinstance(distances_list, list) and len(distances_list) > 0 else ([0.0] * num_results)
            
            metadatas_list = result.get("metadatas")
            metadatas = metadatas_list[0] if metadatas_list and isinstance(metadatas_list, list) and len(metadatas_list) > 0 else ([{}] * num_results)
            
            documents_list = result.get("documents")
            documents = documents_list[0] if documents_list and isinstance(documents_list, list) and len(documents_list) > 0 else ([""] * num_results)
            
            embeddings_list = result.get("embeddings")
            embeddings = embeddings_list[0] if embeddings_list and isinstance(embeddings_list, list) and len(embeddings_list) > 0 else None

            # Ensure all mandatory lists have the same length as ids, providing defaults if necessary
            distances = distances if len(distances) == num_results else ([0.0] * num_results)
            metadatas = metadatas if len(metadatas) == num_results else ([{}] * num_results)
            documents = documents if len(documents) == num_results else ([""] * num_results)
            # Embeddings are optional
            embeddings = embeddings if embeddings and len(embeddings) == num_results else None

            return ChromadbResult(
                ids=ids,
                distances=distances,
                metadatas=metadatas,
                documents=documents,
                embeddings=embeddings
            )
        except Exception as e:
            logger.error(f"Error in search_sync: {str(e)}")
            raise
            
    def get_sync(
        self,
        collection_name: str,
        ids: List[str],
        include: Optional[List[str]] = None
    ) -> ChromadbResult:
        """Synchronous wrapper for get"""
        try:
            if not self._initialized or self.client is None:
                raise ValueError("ChromaDB client not initialized")
                
            collection = self.get_or_create_collection_sync(collection_name)
            
            # Determine default include if not provided
            if include is None:
                include = ["metadatas", "documents"]  # Default to metadatas and documents
            
            # Get documents directly using the include parameter
            result = collection.get(ids=ids, include=include)
                
            # Process the result safely, handling potentially missing keys
            if result is None or not isinstance(result, dict):
                logger.error("ChromaDB get returned None or unexpected type")
                return ChromadbResult(ids=[], documents=[], metadatas=[], distances=[])

            result_ids = result.get("ids")
            ids_list = result_ids if result_ids and isinstance(result_ids, list) else []
            num_results = len(ids_list)
            
            # Safely get other fields based on what was included
            metadatas_list = result.get("metadatas")
            metadatas = metadatas_list if metadatas_list and isinstance(metadatas_list, list) else ([{}] * num_results)
            
            documents_list = result.get("documents")
            documents = documents_list if documents_list and isinstance(documents_list, list) else ([""] * num_results)
            
            embeddings_list = result.get("embeddings")
            embeddings = embeddings_list[0] if embeddings_list and isinstance(embeddings_list, list) and len(embeddings_list) > 0 and embeddings_list[0] is not None else None # get can return [None]
            
            # Ensure lists have the correct length
            metadatas = metadatas if len(metadatas) == num_results else ([{}] * num_results)
            documents = documents if len(documents) == num_results else ([""] * num_results)
            embeddings = embeddings if embeddings and len(embeddings) == num_results else None

            return ChromadbResult(
                ids=ids_list,
                documents=documents,
                metadatas=metadatas,
                distances=[0.0] * num_results,  # get doesn't return distances
                embeddings=embeddings
            )
        except Exception as e:
            logger.error(f"Error in get_sync: {str(e)}")
            raise
    
    async def get_or_create_collection(self, name: str, metadata: Optional[Dict[str, Any]] = None) -> Collection:
        """Get an existing collection or create it if it doesn't exist"""
        if not self._initialized or self.client is None:
            raise ValueError("ChromaDB client not initialized")
            
        # Use cached collection if available
        if name in self.collections:
            return self.collections[name]
            
        # This operation is blocking, run it in a thread pool
        with concurrent.futures.ThreadPoolExecutor() as executor:
            loop = asyncio.get_event_loop()
            collection = await loop.run_in_executor(
                executor, 
                lambda: self.client.get_or_create_collection(
                    name=name,
                    metadata=metadata,
                    embedding_function=self.embedding_function
                )
            )
            
        # Cache the collection
        self.collections[name] = collection
        return collection
    
    async def get_collection_info(self, name: str) -> Dict[str, Any]:
        """Get information about a collection"""
        if not self._initialized or self.client is None:
            raise ValueError("ChromaDB client not initialized")
            
        collection = await self.get_or_create_collection(name)
        
        # This operation is blocking, run it in a thread pool
        with concurrent.futures.ThreadPoolExecutor() as executor:
            loop = asyncio.get_event_loop()
            
            # Get collection count
            count = await loop.run_in_executor(
                executor,
                lambda: len(collection.get()["ids"]) if collection.get()["ids"] else 0
            )
            
            # Get collection metadata
            metadata = await loop.run_in_executor(
                executor,
                lambda: collection.metadata
            )
            
        return {
            "name": name,
            "count": count,
            "metadata": metadata
        }
    
    async def add_documents(
        self, 
        collection_name: str,
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None,
        embeddings: Optional[List[List[float]]] = None
    ) -> List[str]:
        """Add documents to a collection"""
        if not self._initialized or self.client is None:
            raise ValueError("ChromaDB client not initialized")
            
        collection = await self.get_or_create_collection(collection_name)
        
        # Generate IDs if not provided
        if ids is None:
            ids = [f"doc_{i}" for i in range(len(documents))]
            
        # Run in a thread pool
        with concurrent.futures.ThreadPoolExecutor() as executor:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                executor,
                lambda: collection.add(
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids,
                    embeddings=embeddings
                )
            )
            
        return ids
    
    async def search(
        self,
        collection_name: str,
        query: str,
        n_results: int = 10,
        where: Optional[Dict[str, Any]] = None,
        query_embedding: Optional[List[float]] = None,
        include: Optional[List[str]] = None
    ) -> ChromadbResult:
        """Search for documents in a collection"""
        if not self._initialized or self.client is None:
            raise ValueError("ChromaDB client not initialized")
            
        collection = await self.get_or_create_collection(collection_name)
        
        # Basic query parameters
        query_params = {
            "n_results": n_results
        }
        
        # Add where filter if provided
        if where is not None:
            query_params["where"] = where

        # Add include parameter if provided
        if include is not None:
            query_params["include"] = include
        else:
            # Default include values if not specified
            query_params["include"] = ["metadatas", "documents", "distances"]
        
        # Determine which query method to use - prefer embeddings if available
        if query_embedding is not None:
            # Use embedding search
            query_params["query_embeddings"] = [query_embedding]
        elif query and len(query.strip()) > 0:
            # Use text search if no embedding but valid query text
            query_params["query_texts"] = [query]
        else:
            # Emergency fallback - use empty query
            query_params["query_texts"] = [""]
            
        try:
            # Run in a thread pool
            with concurrent.futures.ThreadPoolExecutor() as executor:
                loop = asyncio.get_event_loop()
                logger.debug(f"Executing async ChromaDB query with params: {query_params}")
                result = await loop.run_in_executor(
                    executor,
                    lambda: collection.query(**query_params)
                )
        except Exception as e:
            # Provide detailed error for debugging
            raise Exception(f"ChromaDB query failed: {str(e)} with params: {query_params}")

        # Check if result is None or missing expected keys
        if result is None or not isinstance(result, dict):
            logger.error("Async ChromaDB query returned None or unexpected type")
            # Return an empty result to prevent downstream errors
            return ChromadbResult(ids=[], documents=[], metadatas=[], distances=[])
            
        # Process results, handling potential missing keys or None values gracefully
        ids_list = result.get("ids")
        ids = ids_list[0] if ids_list and isinstance(ids_list, list) and len(ids_list) > 0 else []
        num_results = len(ids)

        # Safely get other fields based on potential inclusion
        distances_list = result.get("distances")
        distances = distances_list[0] if distances_list and isinstance(distances_list, list) and len(distances_list) > 0 else ([0.0] * num_results)
        
        metadatas_list = result.get("metadatas")
        metadatas = metadatas_list[0] if metadatas_list and isinstance(metadatas_list, list) and len(metadatas_list) > 0 else ([{}] * num_results)
        
        documents_list = result.get("documents")
        documents = documents_list[0] if documents_list and isinstance(documents_list, list) and len(documents_list) > 0 else ([""] * num_results)
        
        embeddings_list = result.get("embeddings")
        embeddings = embeddings_list[0] if embeddings_list and isinstance(embeddings_list, list) and len(embeddings_list) > 0 else None

        # Ensure all mandatory lists have the same length as ids, providing defaults if necessary
        distances = distances if len(distances) == num_results else ([0.0] * num_results)
        metadatas = metadatas if len(metadatas) == num_results else ([{}] * num_results)
        documents = documents if len(documents) == num_results else ([""] * num_results)
        # Embeddings are optional
        embeddings = embeddings if embeddings and len(embeddings) == num_results else None

        return ChromadbResult(
            ids=ids,
            distances=distances,
            metadatas=metadatas,
            documents=documents,
            embeddings=embeddings
        )
    
    async def update(
        self,
        collection_name: str,
        ids: List[str],
        documents: Optional[List[str]] = None,
        metadatas: Optional[List[Dict[str, Any]]] = None,
        embeddings: Optional[List[List[float]]] = None
    ) -> None:
        """Update documents in a collection"""
        if not self._initialized or self.client is None:
            raise ValueError("ChromaDB client not initialized")
            
        collection = await self.get_or_create_collection(collection_name)
        
        # Run in a thread pool
        with concurrent.futures.ThreadPoolExecutor() as executor:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                executor,
                lambda: collection.update(
                    ids=ids,
                    documents=documents,
                    metadatas=metadatas,
                    embeddings=embeddings
                )
            )
    
    async def delete(
        self,
        collection_name: str,
        ids: Optional[List[str]] = None,
        where: Optional[Dict[str, Any]] = None
    ) -> None:
        """Delete documents from a collection"""
        if not self._initialized or self.client is None:
            raise ValueError("ChromaDB client not initialized")
            
        collection = await self.get_or_create_collection(collection_name)
        
        # Run in a thread pool
        with concurrent.futures.ThreadPoolExecutor() as executor:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                executor,
                lambda: collection.delete(
                    ids=ids,
                    where=where
                )
            )
    
    async def get_metadata_keys(self, collection_name: str, key: str) -> List[str]:
        """Get all unique values for a metadata key in a collection"""
        if not self._initialized or self.client is None:
            raise ValueError("ChromaDB client not initialized")
            
        # Get all documents with their metadata
        collection = await self.get_or_create_collection(collection_name)
        
        # Run in a thread pool
        with concurrent.futures.ThreadPoolExecutor() as executor:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                executor,
                lambda: collection.get(
                    limit=10000  # Set a reasonable limit
                )
            )
            
        # Extract unique values for the specified key
        values = set()
        if "metadatas" in result and result["metadatas"]:
            for metadata in result["metadatas"]:
                if metadata and key in metadata:
                    values.add(metadata[key])
                    
        return list(values)
    
    def get_collection_docs_sync(
        self,
        collection_name: str,
        limit: int = 100,
        offset: int = 0,
        include_metadata: bool = True,
        include_values: bool = False
    ) -> ChromadbResult:
        """Get all documents from a collection with pagination"""
        try:
            if not self._initialized or self.client is None:
                raise ValueError("ChromaDB client not initialized")
                
            collection = self.get_or_create_collection_sync(collection_name)
            
            # Use get() with no ids to get all documents, then handle pagination manually
            result = collection.get()
            
            if not result or not result.get("ids"):
                return ChromadbResult(
                    ids=[],
                    documents=[],
                    metadatas=[],
                    distances=[]
                )
            
            # Apply pagination
            total_docs = len(result["ids"])
            end_idx = min(offset + limit, total_docs)
            
            if offset >= total_docs:
                # Empty result if offset is beyond available documents
                return ChromadbResult(
                    ids=[],
                    documents=[],
                    metadatas=[],
                    distances=[]
                )
            
            # Extract paginated results
            paginated_ids = result["ids"][offset:end_idx]
            paginated_documents = result["documents"][offset:end_idx] if "documents" in result else []
            paginated_metadatas = result["metadatas"][offset:end_idx] if "metadatas" in result else []
            
            return ChromadbResult(
                ids=paginated_ids,
                documents=paginated_documents,
                metadatas=paginated_metadatas,
                distances=[0.0] * len(paginated_ids)  # Placeholder for distances
            )
        except Exception as e:
            logger.error(f"Error in get_collection_docs_sync: {str(e)}")
            raise 

    def delete_sync(
        self,
        collection_name: str,
        ids: Optional[List[str]] = None,
        where: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Synchronous wrapper for delete"""
        try:
            if not self._initialized or self.client is None:
                raise ValueError("ChromaDB client not initialized")
                
            collection = self.get_or_create_collection_sync(collection_name)
            
            # Can delete by IDs or by filter
            if ids:
                collection.delete(ids=ids)
            elif where:
                collection.delete(where=where)
            else:
                raise ValueError("Either IDs or where filter must be provided")
                
            return True
        except Exception as e:
            logger.error(f"Error in delete_sync: {str(e)}")
            raise 

    def delete_collection_sync(self, collection_name: str) -> bool:
        """Delete an entire collection synchronously"""
        try:
            if not self._initialized or self.client is None:
                raise ValueError("ChromaDB client not initialized")
                
            # Delete collection
            self.client.delete_collection(name=collection_name)
            
            # Remove from cache if exists
            if collection_name in self.collections:
                del self.collections[collection_name]
                
            return True
        except Exception as e:
            logger.error(f"Error deleting collection {collection_name}: {str(e)}")
            return False
            
    async def delete_collection(self, collection_name: str) -> bool:
        """Async wrapper for delete_collection_sync"""
        with concurrent.futures.ThreadPoolExecutor() as executor:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                executor,
                self.delete_collection_sync,
                collection_name
            )
            
    def reset_all_sync(self) -> bool:
        """Delete all collections and reset ChromaDB state synchronously"""
        try:
            if not self._initialized or self.client is None:
                raise ValueError("ChromaDB client not initialized")
                
            # Get list of all collections
            collections = self.client.list_collections()
            
            # Delete each collection
            for collection in collections:
                try:
                    self.delete_collection_sync(collection.name)
                except Exception as e:
                    logger.error(f"Error deleting collection {collection.name}: {str(e)}")
                    
            # Clear collection cache
            self.collections = {}
            
            return True
        except Exception as e:
            logger.error(f"Error resetting ChromaDB: {str(e)}")
            return False
            
    async def reset_all(self) -> bool:
        """Async wrapper for reset_all_sync"""
        with concurrent.futures.ThreadPoolExecutor() as executor:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                executor,
                self.reset_all_sync
            ) 