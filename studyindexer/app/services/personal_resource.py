"""
PersonalResource service for StudyIndexerNew

This service handles personal resource management and search operations for students
organizing and finding their notes, files, and other personal study materials.

Core Functionality:
- Indexing personal resources for efficient retrieval
- Searching across personal resources using vector similarity
- Managing personal resource metadata
- Supporting multiple content types (text, file, url)
"""
import logging
import os
import time
import json
import uuid
from typing import List, Dict, Any, Optional, Tuple, Union
from datetime import datetime
import asyncio
import concurrent.futures

from ..models.personal_resource import (
    PersonalResource,
    PersonalResourceInfo,
    ResourceFile,
    ResourceType,
    PersonalResourceSearchQuery,
    PersonalResourceSearchResult
)
from .chroma import ChromaService
from .embeddings import EmbeddingService, TextChunker

logger = logging.getLogger(__name__)

class PersonalResourceService:
    """Service for managing and searching personal resources"""
    
    _instance = None
    
    def __new__(cls):
        """Singleton pattern to ensure only one instance is created"""
        if cls._instance is None:
            cls._instance = super(PersonalResourceService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the PersonalResource service"""
        if getattr(self, '_initialized', False):
            return
            
        # Initialize dependencies
        self.chroma = ChromaService()
        self.embedder = EmbeddingService()
        self.chunker = TextChunker(chunk_size=1000, chunk_overlap=200)
        
        # Set collection name for personal resource data
        self.collection_name = "personal-resources"
        
        # Cache for resource metadata
        self.resource_cache = {}
        
        # Initialize the collection
        self.initialize_sync()
        
    def initialize_sync(self) -> bool:
        """Initialize the service and ensure the collection exists"""
        if self._initialized:
            return True
            
        try:
            # Create or get the collection
            self.collection = self.chroma.get_or_create_collection_sync(
                name=self.collection_name,
                metadata={"description": "Personal resources for students"}
            )
            
            self._initialized = True
            return True
        except Exception as e:
            logger.error(f"Failed to initialize PersonalResource service: {str(e)}")
            return False
    
    async def initialize(self) -> bool:
        """Async version of initialize for API use"""
        return self.initialize_sync()
    
    def add_resource_sync(self, resource_data: Dict[str, Any]) -> int:
        """
        Index a personal resource for semantic search
        
        Args:
            resource_data: Dictionary containing resource information with the following structure:
                - resource: PersonalResourceInfo object or dict with resource details
                - files: List of ResourceFile objects or dicts
                
        Returns:
            The resource_id as an integer
        """
        if not self._initialized:
            self.initialize_sync()
            
        resource_info = resource_data.get("resource", {})
        files = resource_data.get("files", [])
        
        # Validate resource_id
        resource_id = resource_info.get("id")
        if not resource_id:
            raise ValueError("Resource ID is required")
            
        # Convert to string for Chroma
        str_resource_id = str(resource_id)
        
        # Process files to generate embeddings
        for file_index, file in enumerate(files):
            # Generate a document ID that combines resource_id and file_id
            file_id = file.get("id")
            if not file_id:
                raise ValueError(f"File ID is required for file {file_index}")
                
            document_id = f"{str_resource_id}_{file_id}"
            
            # Create combined text for embedding based on file type
            if file.get("type") == "text":
                # For text resources, use the content directly
                content = file.get("content", "")
                if not content:
                    continue  # Skip empty content
                    
                # Index the text content
                self._index_text_content(
                    document_id=document_id,
                    content=content,
                    resource_id=resource_id,
                    file_id=file_id,
                    file_name=file.get("name", ""),
                    resource_info=resource_info
                )
                    
            elif file.get("type") == "url":
                # For URLs, use the URL as the content
                url = file.get("content", "")
                if not url:
                    continue
                    
                # Add some context around the URL
                content = f"URL: {url}\nName: {file.get('name', '')}"
                
                # Index the URL content
                self._index_text_content(
                    document_id=document_id,
                    content=content,
                    resource_id=resource_id,
                    file_id=file_id,
                    file_name=file.get("name", ""),
                    resource_info=resource_info
                )
                
            elif file.get("type") == "file" and file.get("file_type", "").startswith("text/"):
                # For text-based files, use the content if available
                content = file.get("content", "")
                if not content:
                    continue
                    
                # Index the file content
                self._index_text_content(
                    document_id=document_id,
                    content=content,
                    resource_id=resource_id,
                    file_id=file_id,
                    file_name=file.get("name", ""),
                    resource_info=resource_info
                )
                
            # For binary files, we could implement extraction later
            # For now, we'll just index the file name and metadata
            elif file.get("type") == "file":
                # Basic metadata indexing for file
                content = f"File: {file.get('name', '')}\nType: {file.get('file_type', '')}"
                
                # Index the file metadata
                self._index_text_content(
                    document_id=document_id,
                    content=content,
                    resource_id=resource_id,
                    file_id=file_id,
                    file_name=file.get("name", ""),
                    resource_info=resource_info
                )
        
        # Cache the resource metadata for quick retrieval
        self.resource_cache[str_resource_id] = {
            "resource": resource_info,
            "files": {str(f.get("id")): f for f in files}
        }
        
        logger.info(f"Indexed personal resource {resource_id} with {len(files)} files")
        return resource_id
    
    def _index_text_content(
        self, 
        document_id: str,
        content: str,
        resource_id: int,
        file_id: int,
        file_name: str,
        resource_info: Dict[str, Any]
    ) -> None:
        """Index text content for a resource file"""
        # Clean up content
        if not content or not content.strip():
            return
            
        # Prepare metadata
        metadata = {
            "resource_id": str(resource_id),
            "file_id": str(file_id),
            "file_name": file_name,
            "user_id": str(resource_info.get("user_id")),
            "course_id": str(resource_info.get("course_id")),
            "resource_name": resource_info.get("name", ""),
            "resource_description": resource_info.get("description", ""),
            "indexed_at": datetime.utcnow().isoformat()
        }
        
        # Generate embedding
        embedding = self.embedder.generate_embedding(content)
        
        # Store in ChromaDB
        self.chroma.add_documents_sync(
            collection_name=self.collection_name,
            documents=[content],
            metadatas=[metadata],
            ids=[document_id],
            embeddings=[embedding]
        )
    
    async def add_resource(self, resource_data: Dict[str, Any]) -> int:
        """Async version of add_resource for API use"""
        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as pool:
            return await loop.run_in_executor(
                pool, self.add_resource_sync, resource_data
            )
    
    def get_resource_sync(self, resource_id: int) -> Optional[Dict[str, Any]]:
        """Get resource with all its files by ID"""
        if not self._initialized:
            self.initialize_sync()
            
        # Convert to string for ChromaDB
        str_resource_id = str(resource_id)
        
        # Check cache first
        if str_resource_id in self.resource_cache:
            return self.resource_cache[str_resource_id]
            
        # Query ChromaDB for documents with this resource_id
        where_clause = {"resource_id": str_resource_id}
        
        # Fetch all documents for this resource
        results = self.chroma.search_sync(
            collection_name=self.collection_name,
            query="",  # Empty query to match all
            n_results=100,  # Assuming no more than 100 files per resource
            where=where_clause
        )
        
        if not results or not results.ids:
            return None
            
        # Reconstruct resource and files from the results
        resource_info = None
        files = {}
        
        for metadata in results.metadatas:
            # Get resource info from the first metadata entry
            if not resource_info:
                resource_info = {
                    "id": int(metadata.get("resource_id")),
                    "user_id": int(metadata.get("user_id")),
                    "course_id": int(metadata.get("course_id")),
                    "name": metadata.get("resource_name"),
                    "description": metadata.get("resource_description")
                }
                
            # Get file info
            file_id = int(metadata.get("file_id"))
            if file_id not in files:
                files[file_id] = {
                    "id": file_id,
                    "resource_id": int(metadata.get("resource_id")),
                    "name": metadata.get("file_name"),
                    # Other fields would normally be retrieved from the database
                }
        
        if not resource_info:
            return None
            
        # Structure the response
        result = {
            "resource": resource_info,
            "files": list(files.values())
        }
        
        # Cache for future use
        self.resource_cache[str_resource_id] = result
        
        return result
    
    async def get_resource(self, resource_id: int) -> Optional[Dict[str, Any]]:
        """Async version of get_resource for API use"""
        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as pool:
            return await loop.run_in_executor(
                pool, self.get_resource_sync, resource_id
            )
    
    def update_resource_sync(self, resource_id: int, resource_data: Dict[str, Any]) -> bool:
        """Update resource and its files"""
        if not self._initialized:
            self.initialize_sync()
            
        # First delete the existing resource
        deleted = self.delete_resource_sync(resource_id)
        if not deleted:
            logger.warning(f"Resource {resource_id} not found for update")
            return False
            
        # Then add it again with the updated data
        try:
            self.add_resource_sync(resource_data)
            return True
        except Exception as e:
            logger.error(f"Error updating resource {resource_id}: {str(e)}")
            return False
    
    async def update_resource(self, resource_id: int, resource_data: Dict[str, Any]) -> bool:
        """Async version of update_resource for API use"""
        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as pool:
            return await loop.run_in_executor(
                pool, self.update_resource_sync, resource_id, resource_data
            )
    
    def delete_resource_sync(self, resource_id: int) -> bool:
        """Delete resource and all its files"""
        if not self._initialized:
            self.initialize_sync()
            
        # Convert to string for ChromaDB
        str_resource_id = str(resource_id)
        
        # Find documents to delete
        where_clause = {"resource_id": str_resource_id}
        
        # Delete documents from ChromaDB
        try:
            self.chroma.delete_sync(
                collection_name=self.collection_name,
                where=where_clause
            )
            
            # Remove from cache
            if str_resource_id in self.resource_cache:
                del self.resource_cache[str_resource_id]
                
            return True
        except Exception as e:
            logger.error(f"Error deleting resource {resource_id}: {str(e)}")
            return False
    
    async def delete_resource(self, resource_id: int) -> bool:
        """Async version of delete_resource for API use"""
        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as pool:
            return await loop.run_in_executor(
                pool, self.delete_resource_sync, resource_id
            )
    
    def list_resources_sync(
        self, 
        student_id: int, 
        course_id: Optional[int] = None,
        limit: int = 100, 
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """List resources for a student, optionally filtered by course"""
        if not self._initialized:
            self.initialize_sync()
            
        # Prepare filter
        where_clause = {"user_id": str(student_id)}
        if course_id is not None:
            where_clause["course_id"] = str(course_id)
        
        # Query ChromaDB
        results = self.chroma.search_sync(
            collection_name=self.collection_name,
            query="",  # Empty query to match all
            n_results=limit,
            where=where_clause
        )
        
        if not results or not results.ids:
            return []
            
        # Group by resource_id to get unique resources
        resources = {}
        for i, metadata in enumerate(results.metadatas):
            resource_id = int(metadata.get("resource_id"))
            if resource_id not in resources:
                resources[resource_id] = {
                    "id": resource_id,
                    "user_id": int(metadata.get("user_id")),
                    "course_id": int(metadata.get("course_id")),
                    "name": metadata.get("resource_name"),
                    "description": metadata.get("resource_description")
                }
        
        # Return list of resources
        return list(resources.values())
    
    async def list_resources(
        self, 
        student_id: int, 
        course_id: Optional[int] = None,
        limit: int = 100, 
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Async version of list_resources for API use"""
        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as pool:
            return await loop.run_in_executor(
                pool, self.list_resources_sync, student_id, course_id, limit, offset
            )
    
    def search_resources_sync(
        self, 
        search_query: PersonalResourceSearchQuery
    ) -> Tuple[int, List[PersonalResourceSearchResult], float]:
        """
        Search personal resources
        
        Args:
            search_query: PersonalResourceSearchQuery object with search parameters
                
        Returns:
            Tuple of (total_results, results, query_time_ms)
        """
        if not self._initialized:
            self.initialize_sync()
            
        start_time = time.time()
        
        # Build filter
        where_clause = {"user_id": str(search_query.student_id)}
        
        # Add course filter if specified
        if search_query.course_ids:
            where_clause["$or"] = [{"course_id": str(cid)} for cid in search_query.course_ids]
            
        # Add resource filter if specified
        if search_query.personal_resource_ids:
            where_clause["$or"] = where_clause.get("$or", []) + [
                {"resource_id": str(rid)} for rid in search_query.personal_resource_ids
            ]
        
        # Generate embedding for query
        search_text = search_query.query
        query_embedding = self.embedder.generate_embedding(search_text)
        
        # Search collection
        results = self.chroma.search_sync(
            collection_name=self.collection_name,
            query="",
            query_embedding=query_embedding,
            n_results=search_query.limit,
            where=where_clause
        )
        
        # Process results
        search_results = []
        for doc, metadata, distance in zip(results.documents, results.metadatas, results.distances):
            # Convert distance to similarity score
            similarity = max(0.0, min(1.0, 1.0 - 0.5 * distance))
            
            # Apply min_score filter
            if similarity < search_query.min_score:
                continue
                
            # Get context for the content match
            content_context = self._extract_relevant_context(doc, search_text)
            
            # Create result object
            result = PersonalResourceSearchResult(
                resource_id=int(metadata.get("resource_id")),
                title=metadata.get("resource_name", ""),
                description=metadata.get("resource_description", ""),
                content=content_context,
                type=metadata.get("file_type", "text"),
                course_id=int(metadata.get("course_id")),
                score=similarity,
                file_id=int(metadata.get("file_id"))
            )
            search_results.append(result)
        
        query_time_ms = (time.time() - start_time) * 1000
        return len(search_results), search_results, query_time_ms
    
    def _extract_relevant_context(self, text: str, query: str, context_size: int = 200) -> str:
        """Extract relevant context around a query match in text"""
        if not text or not query:
            return text
            
        # Try to find query in text
        lower_text = text.lower()
        lower_query = query.lower()
        
        if lower_query in lower_text:
            pos = lower_text.find(lower_query)
            start = max(0, pos - context_size)
            end = min(len(text), pos + len(query) + context_size)
            
            # Add ellipsis if we're not at the beginning or end
            prefix = "..." if start > 0 else ""
            suffix = "..." if end < len(text) else ""
            
            return f"{prefix}{text[start:end]}{suffix}"
        
        # If query not found directly, just return first part of the text
        return text[:min(len(text), 400)] + ("..." if len(text) > 400 else "")
    
    async def search_resources(
        self,
        query: str,
        student_id: int,
        resource_ids: Optional[List[str]] = None,
        limit: int = 10
    ):
        """
        Search personal resources for a given student

        Args:
            query: The search query text
            student_id: ID of the student whose resources to search
            resource_ids: Optional list of specific resource IDs to filter by
            limit: Maximum number of results to return

        Returns:
            Tuple of (total_results, results, query_time_ms)
        """
        start_time = time.time()
        
        # Initialize if not already initialized
        if not self._initialized:
            await self.initialize_sync()
        
        # Prepare filters - always filter by student_id
        filters = {"student_id": student_id}
        
        # Add resource_ids filter if provided
        if resource_ids and len(resource_ids) > 0:
            filters["$id"] = {"$in": resource_ids}
            
        try:
            # Get embeddings for query
            query_embedding = self.embedder.generate_embedding(query)
            
            # Search in ChromaDB
            results = self.chroma.search_sync(
                collection_name=self.collection_name,
                query="",
                query_embedding=query_embedding,
                n_results=limit,
                where=filters
            )
            
            # Format results
            formatted_results = []
            if results.ids:  # Check if any results were found
                for i in range(len(results.ids[0])):
                    resource_id = results.ids[0][i]
                    metadata = results.metadatas[0][i]
                    document = results.documents[0][i]
                    distance = results.distances[0][i]
                    
                    # Convert distance to similarity score (ChromaDB returns distance)
                    similarity = 1.0 - min(distance, 1.0)
                    
                    formatted_results.append(
                        PersonalResourceSearchResult(
                            id=resource_id,
                            title=metadata.get("resource_name", "Unknown"),
                            content=document,
                            url=metadata.get("resource_description", ""),
                            resource_type=metadata.get("file_type", ""),
                            student_id=metadata.get("user_id"),
                            course_id=metadata.get("course_id", ""),
                            score=similarity
                        )
                    )
            
            # Sort by score (highest first)
            formatted_results.sort(key=lambda x: x.score, reverse=True)
            
            end_time = time.time()
            query_time_ms = int((end_time - start_time) * 1000)
            
            return len(formatted_results), formatted_results, query_time_ms
            
        except Exception as e:
            logger.error(f"Error searching personal resources: {str(e)}")
            raise 