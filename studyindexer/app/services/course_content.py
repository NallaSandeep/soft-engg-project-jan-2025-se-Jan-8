"""
CourseContent service for managing course content
This service manages the storage, retrieval, and management of course content.

PROJECT GOALS:
------------
The StudyIndexer module serves as a RAG (Retrieval Augmented Generation) data source for StudyAI.
It consists of two main components:

1. StudySelector: Helps identify which courses contain information relevant to a query
   - Primary function: Find courses matching a query from a student's subscribed courses
   - Returns: Matching courses with topics, relevance scores, and week information

2. CourseContent: Provides actual content chunks for RAG applications
   - Primary function: Retrieve specific content (lectures, topics, etc.) matching a query
   - Returns: Content chunks with source information for use in RAG by StudyAI
   
The entire system bridges StudyHub course data with StudyAI, enabling AI-powered
responses that leverage course-specific content. This service ensures that:
   - Course IDs match between StudyHub and StudyAI
   - Content is properly vectorized for semantic search
   - Retrieved content includes proper source attribution
   - Results are formatted for direct use in RAG applications
"""
import os
import json
import logging
import uuid
import time
import re
from typing import List, Dict, Any, Optional, Union
from datetime import datetime

from ..models.course_selector import CourseInfo, CourseTopic, CourseContent, WeekOverview
from .chroma import ChromaService
from .embeddings import EmbeddingService
from app.services.embeddings import TextChunker

logger = logging.getLogger(__name__)

class CourseContentService:
    """Service for managing course content"""
    
    _instance = None
    
    def __new__(cls):
        """Singleton pattern to ensure only one instance is created"""
        if cls._instance is None:
            cls._instance = super(CourseContentService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the CourseContent service"""
        if getattr(self, '_initialized', False):
            return
            
        # Initialize dependencies
        self.chroma = ChromaService()
        self.embedder = EmbeddingService()
        
        # Set collection name for course content data
        self.collection_name = "course-content"
        
        # Flag for initialization status
        self._initialized = False
        
    def initialize_sync(self) -> bool:
        """Initialize the service and ensure the collection exists"""
        if self._initialized:
            logger.info("CourseContent service already initialized")
            return True
            
        try:
            logger.info("Initializing CourseContent service...")
            logger.info(f"Creating/getting collection: {self.collection_name}")
            
            # Create or get the collection
            collection = self.chroma.get_or_create_collection_sync(
                name=self.collection_name,
                metadata={"description": "Course content for managing detailed course information"}
            )
            
            # Use get() with no IDs to get all documents
            result = collection.get()
            count = len(result.get("ids", [])) if result else 0
            logger.info(f"Course content collection initialized with {count} entries")
            
            self._initialized = True
            logger.info("CourseContent service initialization complete")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize CourseContent service: {str(e)}")
            return False
    
    async def initialize(self) -> bool:
        """Async wrapper for initialize_sync"""
        return self.initialize_sync()
        
    def add_course_content_sync(self, course_data: Dict[str, Any]) -> Union[int, str]:
        """
        Add course content to ChromaDB with chunked lecture content for better RAG
        
        This method:
        1. Extracts course, week, and lecture information
        2. Chunks lecture content into smaller segments for better search
        3. Stores both course metadata and individual content chunks
        
        Args:
            course_data: Dictionary containing course information
                
        Returns:
            The course ID
        """
        if not self._initialized:
            self.initialize_sync()
            
        try:
            # Extract course info
            course_info = course_data.get("course", {})
            course_id = str(course_info.get("course_id", ""))
            course_code = course_info.get("code", "")
            course_title = course_info.get("title", "")
            
            if not course_id:
                course_id = str(uuid.uuid4())
                
            # Get lectures and weeks
            lectures = course_data.get("lectures", [])
            weeks = course_data.get("weeks", [])
            
            # Build week lookup map for faster access
            week_map = {}
            for week in weeks:
                week_id = str(week.get("week_id", ""))
                if week_id:
                    week_map[week_id] = week
            
            # Initialize chunker
            chunker = TextChunker(chunk_size=500, chunk_overlap=100)
            
            # Process each lecture
            chunks_added = 0
            
            # First, store the course overview as a document
            overview_metadata = {
                "course_id": course_id,
                "course_code": course_code,
                "course_title": course_title,
                "content_type": "course_description",
                "description": course_info.get("description", ""),
                "department": course_info.get("department", ""),
                "credits": course_info.get("credits", 0),
                "course_summary": course_info.get("LLM_Summary", {}).get("summary", ""),
                "course_concepts": ", ".join(course_info.get("LLM_Summary", {}).get("concepts_covered", []))
            }
            
            self.chroma.add_documents_sync(
                    collection_name=self.collection_name,
                documents=[course_info.get("description", "")],
                metadatas=[overview_metadata],
                ids=[f"course_{course_id}"]
            )
            
            # Process each lecture for detailed content chunks
            for lecture in lectures:
                # Extract lecture content (transcript or extract)
                content = lecture.get("content_transcript") or lecture.get("content_extract", "")
                if not content:
                    continue
                    
                # Get lecture metadata
                lecture_id = str(lecture.get("lecture_id", ""))
                week_id = str(lecture.get("week_id", ""))
                lecture_title = lecture.get("title", "")
                
                # Get week info from the map
                week_info = week_map.get(week_id, {})
                week_title = week_info.get("title", "")
                week_number = week_info.get("order", "")
                
                # Create metadata for chunks
            metadata = {
                "course_id": course_id,
                    "course_code": course_code,
                    "course_title": course_title,
                    "week_id": week_id,
                    "week_title": week_title,
                    "week_number": week_number,
                    "lecture_id": lecture_id,
                    "lecture_title": lecture_title,
                    "content_type": "lecture_chunk",
                    "resource_type": lecture.get("resource_type", ""),
                    "course_description": course_info.get("description", ""),
                    "course_summary": course_info.get("LLM_Summary", {}).get("summary", ""),
                    "course_concepts": ", ".join(course_info.get("LLM_Summary", {}).get("concepts_covered", [])),
                    "week_summary": week_info.get("LLM_Summary", {}).get("summary", ""),
                    "week_concepts": ", ".join(week_info.get("LLM_Summary", {}).get("concepts_covered", [])),
                    "keywords": ", ".join(lecture.get("keywords", [])),
                    "duration_minutes": lecture.get("duration_minutes", 0)
                }
            
            # Chunk the content
            content_chunks = chunker.chunk_text(content, metadata)
            
            # Generate chunk IDs and index in ChromaDB
            for idx, chunk in enumerate(content_chunks):
                chunk_id = f"{course_id}_{lecture_id}_{idx}"
                chunk_content = chunk["content"]
                chunk_metadata = chunk["metadata"]
                
                # Add to ChromaDB
                self.chroma.add_documents_sync(
                collection_name=self.collection_name,
                    documents=[chunk_content],
                    metadatas=[chunk_metadata],
                    ids=[chunk_id]
                )
                chunks_added += 1
            
            logger.info(f"Added course {course_code} with {chunks_added} content chunks")
            return course_id
            
        except Exception as e:
            logger.error(f"Error adding course content: {str(e)}")
            raise
    
    def _delete_course_chunks(self, course_code: str) -> bool:
        """
        Delete all chunks for a specific course
        
        Args:
            course_code: The course code to delete chunks for
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Search for chunks with this course code
            results = self.chroma.search_sync(
                collection_name=self.collection_name,
                query="",
                n_results=1000,  # Large number to get all chunks
                where={"code": course_code}
            )
            
            if results.ids and len(results.ids) > 0:
                # Delete all found documents
                self.chroma.delete_sync(
                    collection_name=self.collection_name,
                    ids=results.ids
                )
                logger.info(f"Deleted {len(results.ids)} chunks for course {course_code}")
                return True
            else:
                logger.info(f"No chunks found for course {course_code}")
                return True
        except Exception as e:
            logger.error(f"Error deleting chunks for course {course_code}: {str(e)}")
            return False
    
    async def add_course_content(self, course_content: Union[Dict[str, Any], CourseContent]) -> str:
        """Async wrapper for add_course_content_sync"""
        return self.add_course_content_sync(course_content)
        
    def get_course_content_sync(self, course_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a course and its content by ID or course code
        
        Args:
            course_id: Course ID or course code
            
        Returns:
            Course content as a dictionary or None if not found
        """
        if not self._initialized:
            self.initialize_sync()
            
        try:
            logger.info(f"DEBUG: get_course_content_sync called with course_id={course_id}")
            
            # First, try to find course by ID
            logger.info(f"DEBUG: Trying to find course by ID: {course_id}")
            results = self.chroma.search_sync(
                    collection_name=self.collection_name,
                query="",  # Empty query to get all results
                n_results=1,
                where={"course_id": course_id}
            )
            
            logger.info(f"DEBUG: ID search returned {len(results.ids) if results and results.ids else 0} results")
            
            # If not found by ID, try to find by course code
            if not results.ids:
                logger.info(f"DEBUG: Course not found by ID, trying by course_code: {course_id}")
                results = self.chroma.search_sync(
                    collection_name=self.collection_name,
                    query="",  # Empty query to get all results
                    n_results=1,
                    where={"course_code": course_id}
                )
                logger.info(f"DEBUG: course_code search returned {len(results.ids) if results and results.ids else 0} results")
                
            # Try a less restrictive query with contains if still not found
            if not results.ids:
                logger.info(f"DEBUG: Course not found by exact match, trying broader query")
                # Dump all collection documents to see what's there
                all_docs = self.chroma.get_collection_docs_sync(
                    collection_name=self.collection_name,
                    limit=100,
                    offset=0,
                    include_metadata=True
                )
                logger.info(f"DEBUG: Found {len(all_docs.ids) if all_docs and all_docs.ids else 0} total documents in collection")
                logger.info("DEBUG: Checking first 5 documents for course codes:")
                for i, doc_id in enumerate(all_docs.ids[:5] if all_docs and all_docs.ids else []):
                    logger.info(f"DEBUG: Doc {i} - Metadata: {all_docs.metadatas[i]}")
                
                # Try a less strict query that looks for course_code containing the course_id
                for field in ["course_code", "code"]:
                    found = False
                    logger.info(f"DEBUG: Scanning collection for documents with {field}={course_id}")
                    for i, metadata in enumerate(all_docs.metadatas if all_docs and all_docs.metadatas else []):
                        if field in metadata and metadata[field] == course_id:
                            logger.info(f"DEBUG: Found match in document {i} with {field}={course_id}")
                            results = type('obj', (object,), {
                                'ids': [all_docs.ids[i]],
                                'metadatas': [all_docs.metadatas[i]]
                            })
                            found = True
                            break
                    if found:
                        break
                
            if not results.ids:
                logger.warning(f"Course with ID or code {course_id} not found")
                return None
                
            # Found course, now get all its content
            course_code = results.metadatas[0].get("course_code", "")
            if not course_code:
                logger.error(f"Course {course_id} found but has no course_code")
                logger.info(f"DEBUG: Found course metadata: {results.metadatas[0]}")
                
                # Try alternate fields
                for field in ["code", "course_code"]:
                    if field in results.metadatas[0]:
                        course_code = results.metadatas[0][field]
                        logger.info(f"DEBUG: Found course_code in alternate field {field}: {course_code}")
                        break
                        
                if not course_code:
                    # If we still don't have a course code, use the course_id as the code
                    course_code = course_id
                    logger.info(f"DEBUG: Using course_id as course_code: {course_code}")
                
            logger.info(f"DEBUG: Found course_code: {course_code}, retrieving all content")
                
            # Retrieve all course content by course code - use both course_code and code fields
            # Since we can't do OR conditions, we'll need to do separate searches
            logger.info(f"DEBUG: Querying for all content with course_code={course_code}")
            
            # Search by course_code
            all_results_by_code = self.chroma.search_sync(
                collection_name=self.collection_name,
                query="",  # Empty query to get all results 
                n_results=1000,  # Get all content chunks
                where={"course_code": course_code}
            )
            
            # Search by code field
            all_results_by_alt_code = self.chroma.search_sync(
                collection_name=self.collection_name,
                query="",  # Empty query to get all results
                n_results=1000,  # Get all content chunks
                where={"code": course_code}
            )
            
            # Search by course_id
            all_results_by_id = self.chroma.search_sync(
                    collection_name=self.collection_name,
                query="",  # Empty query to get all results
                n_results=1000,  # Get all content chunks
                where={"course_id": course_code}  # Use course_code as it might be the ID
            )
            
            # Combine results (might have duplicates but we'll handle that)
            all_ids = []
            all_metadatas = []
            all_documents = []
            
            # Helper function to add results while avoiding duplicates
            def add_results(results):
                if not results or not results.ids:
                    return
                for i, doc_id in enumerate(results.ids):
                    if doc_id not in all_ids:  # Only add if not already present
                        all_ids.append(doc_id)
                        all_metadatas.append(results.metadatas[i])
                        all_documents.append(results.documents[i])
            
            # Add results from all searches, avoiding duplicates
            add_results(all_results_by_code)
            add_results(all_results_by_alt_code)
            add_results(all_results_by_id)
            
            logger.info(f"DEBUG: Found total of {len(all_ids)} unique documents across all searches")
            
            if not all_ids:
                logger.warning(f"No content found for course {course_code}")
                return None
                
            # Extract course metadata from the first result
            course_metadata = None
            course_description = ""
            lectures = []
            weeks = []
            
            # Process each document based on its type
            lecture_count = 0
            week_count = 0
            
            for i, doc_id in enumerate(all_ids):
                metadata = all_metadatas[i]
                content = all_documents[i]
                content_type = metadata.get("content_type", "")
                
                logger.info(f"DEBUG: Processing document {i}, type={content_type}")
                
                if content_type == "course_description":
                    # Found course overview
                    logger.info(f"DEBUG: Found course description")
                    course_metadata = {
                        "course_id": metadata.get("course_id", ""),
                        "code": metadata.get("course_code", ""),
                        "title": metadata.get("course_title", ""),
                        "description": content,
                        "department": metadata.get("department", ""),
                        "credits": metadata.get("credits", 0),
                        "summary": metadata.get("course_summary", ""),
                        "concepts": metadata.get("course_concepts", "")
                    }
                    course_description = content
                    logger.info(f"DEBUG: Found course description with summary length {len(metadata.get('course_summary', ''))}")
                
                elif content_type == "lecture_chunk":
                    # Construct lecture information
                    lecture_id = metadata.get("lecture_id", "")
                    week_id = metadata.get("week_id", "")
                    
                    logger.info(f"DEBUG: Found lecture chunk - lecture_id={lecture_id}, week_id={week_id}")
                    
                    # Check if we've already processed this lecture
                    existing_lecture = next((l for l in lectures if l.get("lecture_id") == lecture_id), None)
                    
                    if not existing_lecture:
                        # Create new lecture
                        lecture = {
                            "lecture_id": lecture_id,
                            "week_id": week_id,
                            "title": metadata.get("lecture_title", ""),
                            "content_extract": content[:1000],  # Use first chunk as extract
                            "content_transcript": content,
                            "resource_type": metadata.get("resource_type", ""),
                            "keywords": metadata.get("keywords", ""),
                            "duration_minutes": metadata.get("duration_minutes", 0),
                            "course_summary": metadata.get("course_summary", ""),
                            "week_summary": metadata.get("week_summary", ""),
                            "course_concepts": metadata.get("course_concepts", ""),
                            "week_concepts": metadata.get("week_concepts", "")
                        }
                        lectures.append(lecture)
                        lecture_count += 1
                        logger.info(f"DEBUG: Added new lecture: {lecture['title']} with {len(content)} chars")
                    else:
                        # Append content to existing lecture
                        existing_lecture["content_transcript"] += "\n\n" + content
                        # Update metadata if not already present
                        for field in ["keywords", "duration_minutes", "course_summary", "week_summary", 
                                    "course_concepts", "week_concepts"]:
                            if field not in existing_lecture and field in metadata:
                                existing_lecture[field] = metadata[field]
                        logger.info(f"DEBUG: Appended to existing lecture: {existing_lecture['title']}, now {len(existing_lecture['content_transcript'])} chars")
                    
                    # Check if we need to add this week
                    if week_id:
                        existing_week = next((w for w in weeks if w.get("week_id") == week_id), None)
                        if not existing_week:
                            week = {
                                "week_id": week_id,
                                "title": metadata.get("week_title", ""),
                                "order": metadata.get("week_number", 0),
                                "summary": metadata.get("week_summary", ""),
                                "concepts": metadata.get("week_concepts", "")
                            }
                            weeks.append(week)
                            week_count += 1
                            logger.info(f"DEBUG: Added new week: {week['title']} with summary length {len(week['summary'])}")
            
            logger.info(f"DEBUG: Processed {lecture_count} unique lectures and {week_count} unique weeks")
            
            # If no course metadata was found but we have content, create a placeholder
            if not course_metadata and lectures:
                logger.info(f"DEBUG: No course metadata found, creating placeholder from lecture metadata")
                first_metadata = all_metadatas[0]
                course_metadata = {
                    "course_id": first_metadata.get("course_id", ""),
                    "code": first_metadata.get("course_code", ""),
                    "title": first_metadata.get("course_title", ""),
                    "description": course_description,
                    "department": "",
                    "credits": 0,
                    "summary": first_metadata.get("course_summary", ""),
                    "concepts": first_metadata.get("course_concepts", "")
                }
                logger.info(f"DEBUG: Created placeholder course metadata: {course_metadata}")
            
            # Construct final course content structure
            if course_metadata:
                result = {
                    "course": course_metadata,
                    "weeks": weeks,
                    "lectures": lectures
                }
                logger.info(f"DEBUG: Returning complete course content with {len(lectures)} lectures and {len(weeks)} weeks")
                return result
            
            logger.warning(f"DEBUG: Could not construct course content, returning None")
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving course content for {course_id}: {str(e)}")
            import traceback
            logger.error(f"DEBUG: Full traceback: {traceback.format_exc()}")
            return None
    
    async def get_course_content(self, course_id: Union[int, str]) -> Optional[CourseContent]:
        """Async wrapper for get_course_content_sync"""
        return self.get_course_content_sync(course_id)
        
    def update_course_content_sync(self, course_id: Union[int, str], course_content: Union[Dict[str, Any], CourseContent]) -> bool:
        """Synchronous version of update_course_content"""
        if not self._initialized:
            self.initialize_sync()
            
        course_id_str = str(course_id)
        
        try:
            # Convert to dict if CourseContent object
            if isinstance(course_content, CourseContent):
                course_data = course_content.dict()
            else:
                course_data = course_content
                
            # Check if the course exists
            existing = self.get_course_content_sync(course_id)
            if not existing:
                logger.warning(f"Course content with ID {course_id} not found for update")
                return False
                
            # Ensure course_id in the content matches the provided ID
            course_info = course_data.get("course_info", {})
            course_info["course_id"] = course_id_str
            course_data["course_info"] = course_info
            
            # Delete the existing course content
            self.delete_course_content_sync(course_id)
            
            # Add the updated course content
            self.add_course_content_sync(course_data)
            
            logger.info(f"Updated course content for ID: {course_id_str}")
            return True
        except Exception as e:
            logger.error(f"Error updating course content: {str(e)}")
            return False
            
    async def update_course_content(self, course_id: Union[int, str], course_content: Union[Dict[str, Any], CourseContent]) -> bool:
        """Async wrapper for update_course_content_sync"""
        return self.update_course_content_sync(course_id, course_content)
    
    def delete_course_content_sync(self, course_id: Union[int, str]) -> bool:
        """Synchronous version of delete_course_content"""
        if not self._initialized:
            self.initialize_sync()
            
        course_id_str = str(course_id)
        logger.info(f"Attempting to delete course with ID: {course_id_str}")
        
        try:
            # First check if the course exists using get method
            result = self.chroma.get_sync(
                collection_name=self.collection_name,
                ids=[course_id_str]
            )
            
            if not result.ids or len(result.ids) == 0:
                logger.warning(f"Course with ID {course_id_str} not found using direct lookup")
                
                # Try searching by code if the ID might be a course code
                if any(c.isalpha() for c in course_id_str):
                    search_results = self.chroma.search_sync(
                        collection_name=self.collection_name,
                        query="",
                        n_results=1,
                        where={"code": course_id_str}
                    )
                    
                    if search_results.ids and len(search_results.ids) > 0:
                        actual_id = search_results.ids[0]
                        logger.info(f"Found course with code {course_id_str}, actual ID: {actual_id}")
                        course_id_str = actual_id
                    else:
                        logger.warning(f"Course with code {course_id_str} not found for deletion")
                        return False
                else:
                    logger.warning(f"Course with ID {course_id_str} not found for deletion")
                    return False
            else:
                logger.info(f"Found course with ID {course_id_str} for deletion")
            
            # Delete the course from ChromaDB
            logger.info(f"Deleting course with ID: {course_id_str}")
            delete_result = self.chroma.delete_sync(
                collection_name=self.collection_name,
                ids=[course_id_str]
            )
            
            # Log delete result
            logger.info(f"Delete operation result: {delete_result}")
            
            # Verify deletion was successful
            verification = self.chroma.get_sync(
                collection_name=self.collection_name,
                ids=[course_id_str]
            )
            
            if verification.ids and len(verification.ids) > 0:
                logger.error(f"Deletion failed - course {course_id_str} still exists")
                return False
            
            logger.info(f"Successfully deleted course with ID: {course_id_str}")
            return True
        except Exception as e:
            logger.error(f"Error deleting course content: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    async def delete_course_content(self, course_id: Union[int, str]) -> bool:
        """Async wrapper for delete_course_content_sync"""
        return self.delete_course_content_sync(course_id)
    
    def list_courses_sync(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """List all course content with pagination"""
        if not self._initialized:
            logger.info("Service not initialized, initializing now...")
            self.initialize_sync()
            
        try:
            logger.info(f"DEBUG: List courses called with limit={limit}, offset={offset}")
            
            # First try with content_type filter
            logger.info("DEBUG: Trying to query with content_type=course_description")
            results = self.chroma.get_collection_docs_sync(
                collection_name=self.collection_name,
                limit=limit,
                offset=offset,
                include_metadata=True
            )
            
            logger.info(f"DEBUG: Initial query returned {len(results.ids if results.ids else [])} results")
            
            # If no results, try a broader query to find any course data
            if not results.ids or len(results.ids) == 0:
                logger.warning("No course descriptions found with content_type filter, trying broader query")
                logger.info("DEBUG: Trying broader query with no filters")
                results = self.chroma.get_collection_docs_sync(
                    collection_name=self.collection_name,
                    limit=1000,  # Get all and we'll filter
                    offset=0,
                    include_metadata=True
                )
                
                logger.info(f"DEBUG: Broader query returned {len(results.ids if results.ids else [])} results")
                
                # Find any entries that have course_code
                filtered_ids = []
                filtered_documents = []
                filtered_metadatas = []
                seen_courses = set()
                
                # Dump all metadata for debugging
                logger.info("DEBUG: Dumping metadata from first 5 results:")
                for i, doc_id in enumerate(results.ids[:5] if results.ids else []):
                    logger.info(f"DEBUG: Result {i} - ID: {doc_id}, Metadata: {results.metadatas[i]}")
                
                for i, doc_id in enumerate(results.ids if results.ids else []):
                    metadata = results.metadatas[i]
                    course_code = metadata.get("course_code", "")
                    
                    # Skip if no course code or already processed this course
                    if not course_code or course_code in seen_courses:
                        continue
                        
                    logger.info(f"DEBUG: Found course with code {course_code}")
                    seen_courses.add(course_code)
                    filtered_ids.append(doc_id)
                    filtered_documents.append(results.documents[i] if i < len(results.documents) else "")
                    filtered_metadatas.append(metadata)
                    
                    # Only collect up to the limit
                    if len(filtered_ids) >= limit:
                        break
                        
                # Replace results with filtered version
                # Create a new object to mimic ChromaDB result structure
                class FilteredResults:
                    def __init__(self, ids, documents, metadatas):
                        self.ids = ids
                        self.documents = documents
                        self.metadatas = metadatas
                        
                results = FilteredResults(filtered_ids, filtered_documents, filtered_metadatas)
                logger.info(f"DEBUG: After filtering, found {len(results.ids if results.ids else [])} unique courses")
            
            if not results.ids:
                logger.warning("No course data found at all")
                return []
                
            # Extract course info from metadata
            courses = []
            for i, doc_id in enumerate(results.ids):
                metadata = results.metadatas[i]
                content = results.documents[i] if i < len(results.documents) else ""
                
                # Build course info
                course = {
                    "course_id": metadata.get("course_id", ""),
                    "code": metadata.get("course_code", ""),
                    "title": metadata.get("course_title", ""),
                    "department": metadata.get("department", ""),
                    "credits": metadata.get("credits", 0),
                    "description": content,
                    "created_at": metadata.get("created_at", None)
                }
                courses.append(course)
                logger.info(f"DEBUG: Added course {course['code'] or course['course_id']} to result list")
                
            logger.info(f"DEBUG: Returning {len(courses)} courses")
            return courses
        except Exception as e:
            logger.error(f"Error listing courses: {str(e)}")
            import traceback
            logger.error(f"DEBUG: Full traceback: {traceback.format_exc()}")
            return []
    
    async def list_courses(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Async wrapper for list_courses_sync"""
        return self.list_courses_sync(limit, offset)
    
    def _normalize_query(self, query: str) -> str:
        """
        Normalize a query string by replacing hyphens, underscores, and special characters with spaces.
        
        Args:
            query: The query string to normalize
            
        Returns:
            Normalized query string
        """
        # Replace common separators with spaces
        normalized = query.replace('-', ' ').replace('_', ' ')
        
        # Remove extra spaces
        normalized = ' '.join(normalized.split())
        
        return normalized
    
    def search_courses_sync(
        self, 
        query: str, 
        limit: int = 10,
        course_ids: list = None,
        min_score: float = 0.01,
        exact_match_boost: float = 0.1,
        phrase_match_boost: float = 0.15,
        description_threshold: float = 0.05
    ) -> dict:
        """
        Search for course content by query.
        """
        try:
            logger.info(f"DEBUG: Search called with query='{query}', limit={limit}, course_ids={course_ids}, min_score={min_score}")
            
            if not query or not query.strip():
                logger.warning("DEBUG: Empty query provided, returning empty results")
                return {"content_chunks": [], "total_count": 0, "query": query, "limit": limit}
            
            # Prepare filter based on course_ids
            filter_dict = {}
            if course_ids:
                logger.info(f"DEBUG: Using course filter: {{'course_code': {{'$in': {course_ids}}}}}")
                filter_dict = {"course_code": {"$in": course_ids}}
            
            # Normalize the query by replacing hyphens with spaces, etc.
            normalized_query = self._normalize_query(query)
            logger.info(f"DEBUG: Normalized query: '{normalized_query}'")
            
            # List to store all expanded versions of the query
            expanded_queries = [normalized_query]
            
            # Check if the query is short and likely an acronym (e.g., "RDBMS")
            if len(normalized_query.split()) == 1 and len(normalized_query) <= 10 and normalized_query.isupper():
                logger.info(f"DEBUG: Detected potential acronym: {normalized_query}")
                
                # Dictionary of common database-related acronyms and their expansions
                acronyms = {
                    "RDBMS": "relational database management system",
                    "SQL": "structured query language",
                    "DDL": "data definition language",
                    "DML": "data manipulation language",
                    "DCL": "data control language",
                    "TCL": "transaction control language",
                    "ER": "entity relationship",
                    "ACID": "atomicity consistency isolation durability",
                    "DBMS": "database management system",
                    "1NF": "first normal form",
                    "2NF": "second normal form", 
                    "3NF": "third normal form",
                    "BCNF": "boyce codd normal form"
                }
                
                # Add the expanded acronym to the list of queries to search
                if normalized_query in acronyms:
                    expanded_query = acronyms[normalized_query]
                    logger.info(f"DEBUG: Added expansion: '{normalized_query}' → '{expanded_query}'")
                    expanded_queries.append(normalized_query)  # Keep the original acronym
                    expanded_queries.append(expanded_query)
            
            # Special handling for normal forms - check for patterns
            normalization_patterns = {
                r"(?i)first\s+normal\s+form": ["1NF", "first normal form"],
                r"(?i)second\s+normal\s+form": ["2NF", "second normal form"],
                r"(?i)third\s+normal\s+form": ["3NF", "third normal form"],
                r"(?i)boyce\s+codd\s+normal\s+form": ["BCNF", "boyce codd normal form"],
                r"(?i)fourth\s+normal\s+form": ["4NF", "fourth normal form"],
                r"(?i)fifth\s+normal\s+form": ["5NF", "fifth normal form"],
                r"(?i)1nf": ["first normal form", "1NF"],
                r"(?i)2nf": ["second normal form", "2NF"],
                r"(?i)3nf": ["third normal form", "3NF"],
                r"(?i)bcnf": ["boyce codd normal form", "BCNF"],
                r"(?i)4nf": ["fourth normal form", "4NF"],
                r"(?i)5nf": ["fifth normal form", "5NF"]
            }
            
            # Check if the query matches any normalization pattern
            for pattern, expansions in normalization_patterns.items():
                if re.search(pattern, normalized_query):
                    logger.info(f"DEBUG: Detected normalization form pattern: {pattern}")
                    for expansion in expansions:
                        if expansion not in expanded_queries:
                            logger.info(f"DEBUG: Added normalization expansion: '{expansion}'")
                            expanded_queries.append(expansion)
            
            # Special handling for phrases containing "normal form"
            if "normal form" in normalized_query.lower():
                logger.info("DEBUG: Query contains 'normal form', adding specific normalization expansions")
                normal_form_expansions = ["1NF", "2NF", "3NF", "BCNF", "first normal form", "second normal form", "third normal form", "boyce codd normal form"]
                for expansion in normal_form_expansions:
                    if expansion not in expanded_queries:
                        expanded_queries.append(expansion)
            
            logger.info(f"DEBUG: All expanded queries: {expanded_queries}")
            
            # Get collection info
            collection = self.chroma.get_or_create_collection_sync(self.collection_name)
            logger.info(f"DEBUG: Using collection: {self.collection_name}")
            
            # Process each expanded query
            all_results = []
            
            for expanded_query in set(expanded_queries):
                logger.info(f"DEBUG: Searching with expanded query: '{expanded_query}'")
                
                # Search using the expanded query
                results = self.chroma.search_sync(
                    collection_name=self.collection_name,
                    query=expanded_query,
                    n_results=50,  # Get more results initially for filtering
                    where=filter_dict
                )
                
                if not results or not results.ids or not results.ids:
                        continue
                        
                result_ids = results.ids
                result_distances = results.distances
                result_metadatas = results.metadatas
                result_documents = results.documents
                
                logger.info(f"DEBUG: Search for '{expanded_query}' found {len(result_ids)} initial results")
                
                if len(result_ids) > 0:
                    logger.info("DEBUG: Sample results for '{expanded_query}':")
                    for i in range(min(3, len(result_ids))):
                        # Convert distance to a relevance score (1 - distance, as lower distance = higher relevance)
                        # Clamp between 0 and 1
                        score = max(0, min(1, 1 - result_distances[i]))
                        logger.info(f"DEBUG: Result {i}: ID={result_ids[i]}, score={score:.4f}, metadata={result_metadatas[i]}")
                
                # Process results
                for i in range(len(result_ids)):
                    doc_id = result_ids[i]
                    distance = result_distances[i]
                    metadata = result_metadatas[i]
                    document = result_documents[i]
                    
                    # Calculate relevance score (1 - distance, as lower distance = higher relevance)
                    # Clamp between 0 and 1
                    score = max(0, min(1, 1 - distance))
                    
                    # Skip low scoring results
                    if score < min_score:
                        logger.info(f"DEBUG: Skipping result {i} with score {score:.4f} < min_score {min_score}")
                        continue
                    
                    content_type = metadata.get('content_type', '')
                    
                    # For course descriptions, only include them if they meet a higher relevance threshold
                    if content_type == 'course_description' and score < description_threshold:
                        continue
                    
                    # Apply exact match and term match boosting
                    boosted_score = score
                    
                    # Check for term matches in the document text
                    query_terms = set(expanded_query.lower().split())
                    doc_text = document.lower()
                    
                    # Only consider terms with at least 2 characters
                    matching_terms = [term for term in query_terms if len(term) >= 2 and term in doc_text]
                    
                    if matching_terms:
                        logger.info(f"DEBUG: Term match: '{', '.join(matching_terms)}' in result {i}")
                        # Boost based on number of matching terms
                        term_boost = exact_match_boost * len(matching_terms)
                        boosted_score += term_boost
                        logger.info(f"DEBUG: Term boost: +{term_boost:.4f} for {len(matching_terms)} matches, new score: {boosted_score:.4f}")
                    
                    # Check for acronym match
                    if expanded_query.isupper() and expanded_query in document:
                        logger.info(f"DEBUG: Acronym boost: +0.2 for exact match of {expanded_query}, new score: {boosted_score + 0.2:.4f}")
                        boosted_score += 0.2  # Significant boost for exact acronym match
                    
                    # Check for exact phrase match
                    if expanded_query.lower() in doc_text:
                        logger.info(f"DEBUG: Phrase boost: +{phrase_match_boost} for exact phrase match, new score: {boosted_score + phrase_match_boost:.4f}")
                        boosted_score += phrase_match_boost
                    
                    # For normalization forms (like "first normal form", "1NF"), check for specific matches
                    for pattern, _ in normalization_patterns.items():
                        if re.search(pattern, expanded_query, re.IGNORECASE) and any(re.search(pattern, doc_text, re.IGNORECASE) for pattern in normalization_patterns.keys()):
                            logger.info(f"DEBUG: Normalization form boost: +0.25 for matching normalization concept, new score: {boosted_score + 0.25:.4f}")
                            boosted_score += 0.25  # Higher boost for database normalization concepts
                            break
                    
                    # NEW BOOST CHECKS FOR ADDITIONAL METADATA FIELDS
                    # Check for matches in keywords (highest boost because most specific)
                    if "keywords" in metadata and metadata["keywords"]:
                        keywords_lower = metadata["keywords"].lower()
                        if expanded_query.lower() in keywords_lower:
                            logger.info(f"DEBUG: Keywords exact match boost: +0.3 for '{expanded_query}', new score: {boosted_score + 0.3:.4f}")
                            boosted_score += 0.3
                        else:
                            # Check for individual terms in keywords
                            matching_keywords = [term for term in query_terms if len(term) >= 2 and term in keywords_lower]
                            if matching_keywords:
                                keyword_boost = 0.15 * len(matching_keywords)
                                logger.info(f"DEBUG: Keywords term match boost: +{keyword_boost:.4f} for {len(matching_keywords)} terms, new score: {boosted_score + keyword_boost:.4f}")
                                boosted_score += keyword_boost
                    
                    # Check for matches in course concepts and week concepts
                    for concept_field in ["course_concepts", "week_concepts"]:
                        if concept_field in metadata and metadata[concept_field]:
                            concepts_lower = metadata[concept_field].lower()
                            if expanded_query.lower() in concepts_lower:
                                logger.info(f"DEBUG: {concept_field} match boost: +0.2 for '{expanded_query}', new score: {boosted_score + 0.2:.4f}")
                                boosted_score += 0.2
                                break  # Only boost once for concepts
                            else:
                                # Check for individual terms in concepts
                                matching_concepts = [term for term in query_terms if len(term) >= 2 and term in concepts_lower]
                                if matching_concepts:
                                    concept_boost = 0.1 * len(matching_concepts)
                                    logger.info(f"DEBUG: {concept_field} term match boost: +{concept_boost:.4f}, new score: {boosted_score + concept_boost:.4f}")
                                    boosted_score += concept_boost
                                    break  # Only boost once for concepts
                    
                    # Check for matches in course summary and week summary
                    for summary_field in ["course_summary", "week_summary"]:
                        if summary_field in metadata and metadata[summary_field]:
                            summary_lower = metadata[summary_field].lower()
                            if expanded_query.lower() in summary_lower:
                                logger.info(f"DEBUG: {summary_field} match boost: +0.1 for '{expanded_query}', new score: {boosted_score + 0.1:.4f}")
                                boosted_score += 0.1
                                break  # Only boost once for summaries
                            else:
                                # Check for individual terms in summaries
                                matching_summary_terms = [term for term in query_terms if len(term) >= 2 and term in summary_lower]
                                if matching_summary_terms:
                                    summary_boost = 0.05 * len(matching_summary_terms)
                                    logger.info(f"DEBUG: {summary_field} term match boost: +{summary_boost:.4f}, new score: {boosted_score + summary_boost:.4f}")
                                    boosted_score += summary_boost
                                    break  # Only boost once for summaries
                    
                    # Prepare the result with the boosted score
                    if content_type == 'course_description':
                        result = {
                            'type': 'course_description',
                            'title': metadata.get('course_title', ''),
                            'content': document,
                            'relevance_score': round(boosted_score, 2),
                            'course_code': metadata.get('course_code', ''),
                            'course_summary': metadata.get('course_summary', ''),
                            'course_concepts': metadata.get('course_concepts', '')
                        }
                    elif content_type == 'lecture_chunk':
                        result = {
                            'type': 'lecture_content',
                            'title': metadata.get('lecture_title', ''),
                            'content': document,
                            'relevance_score': round(boosted_score, 2),
                            'course_code': metadata.get('course_code', ''),
                            'course_title': metadata.get('course_title', ''),
                            'week_title': metadata.get('week_title', ''),
                            'week_number': metadata.get('week_number', ''),
                            'lecture_id': metadata.get('lecture_id', ''),
                            'resource_type': metadata.get('resource_type', ''),
                            'keywords': metadata.get('keywords', ''),
                            'course_summary': metadata.get('course_summary', ''),
                            'week_summary': metadata.get('week_summary', '')
                        }
                    else:
                        continue  # Skip unknown content types
                    
                    # Create a unique key for deduplication
                    chunk_key = f"{metadata.get('course_code', '')}__{metadata.get('lecture_id', '')}__{metadata.get('chunk_index', '')}"
                    result['chunk_key'] = chunk_key
                    
                    all_results.append(result)
            
            logger.info(f"DEBUG: Total results before deduplication: {len(all_results)}")
            
            # Deduplicate results by chunk_key and sort by relevance score
            unique_results = {}
            for result in all_results:
                chunk_key = result.pop('chunk_key', None)  # Remove the key from the result dict
                if chunk_key not in unique_results or result['relevance_score'] > unique_results[chunk_key]['relevance_score']:
                    unique_results[chunk_key] = result
            
            # Sort by relevance score in descending order
            sorted_results = sorted(
                unique_results.values(), 
                key=lambda x: x['relevance_score'], 
                reverse=True
            )
            
            # Limit the number of results
            final_results = sorted_results[:limit]
            
            logger.info(f"DEBUG: Final results: {len(final_results)} unique content chunks for query: '{query}'")
            
            if not final_results:
                logger.warning("DEBUG: No results found for any expanded queries")
                
                # Try a broader search without filters as a fallback
                broader_results = self.chroma.search_sync(
                    collection_name=self.collection_name,
                    query=normalized_query,
                    n_results=5,  # Just get a few results
                )
                
                if broader_results and broader_results.ids and len(broader_results.ids) > 0:
                    logger.info(f"DEBUG: Broader search (no filters) found {len(broader_results.ids)} results")
                    first_score = 1 - broader_results.distances[0] if broader_results.distances else 0
                    logger.info(f"DEBUG: First result score: {first_score:.4f}")
                    if broader_results.metadatas:
                        logger.info(f"DEBUG: First result metadata: {broader_results.metadatas[0]}")
            
            return {
                "content_chunks": final_results,
                "total_count": len(final_results),
                "query": query,
                "limit": limit
            }
            
        except Exception as e:
            logger.error(f"Error searching courses: {str(e)}", exc_info=True)
            return {"content_chunks": [], "total_count": 0, "query": query, "limit": limit}

    def _extract_content_chunks_from_course(self, course_data: Dict[str, Any], query: str) -> List[Dict[str, Any]]:
        """
        Extract and score content chunks from a course document
        
        This handles backward compatibility with the old storage format where
        entire course documents were stored instead of individual chunks.
        
        Args:
            course_data: The course data dictionary
            query: The search query to score chunks against
            
        Returns:
            List of extracted content chunks
        """
        try:
            logger.info(f"Extracting chunks from course data for query: '{query}'")
            
            # Extract content based on query relevance
            content_chunks = []
            query_terms = query.lower().split()
            
            # Extract lecture content from weeks
            if "weeks" in course_data and course_data["weeks"]:
                for week in course_data["weeks"]:
                    week_title = week.get("title", "")
                    week_number = week.get("number", 0)
                    
                    # Extract lectures from week
                    if "lectures" in week and week["lectures"]:
                        for lecture in week["lectures"]:
                            lecture_title = lecture.get("title", "")
                            
                            # Score the lecture title for relevance
                            title_score = 0
                            for term in query_terms:
                                if term in lecture_title.lower():
                                    title_score += 0.1
                            
                            # Get lecture content
                            lecture_content = lecture.get("content", "")
                            if not lecture_content:
                                continue
                            
                            # Find paragraphs containing query terms
                            paragraphs = lecture_content.split("\n\n")
                            for paragraph in paragraphs:
                                if not paragraph.strip():
                                    continue
                                    
                                # Calculate paragraph score
                                paragraph_score = 0
                                paragraph_lower = paragraph.lower()
                                for term in query_terms:
                                    if term in paragraph_lower:
                                        paragraph_score += 0.05
                                        
                                # Skip paragraphs with no relevance
                                if paragraph_score == 0 and title_score == 0:
                                    continue
                                
                                # Create content chunk
                                chunk = {
                                    "type": "lecture_paragraph",
                                    "title": lecture_title,
                                    "content": paragraph,
                                    "week_number": week_number,
                                    "relevance_score": title_score + paragraph_score
                                }
                                content_chunks.append(chunk)
            
            # If no lecture content found, try course description
            if not content_chunks and "description" in course_data:
                description = course_data["description"]
                description_score = 0
                
                for term in query_terms:
                    if term in description.lower():
                        description_score += 0.05
                        
                if description_score > 0:
                    chunk = {
                        "type": "course_description",
                        "title": course_data.get("title", ""),
                        "content": description,
                        "relevance_score": description_score
                    }
                    content_chunks.append(chunk)
            
            # Add course summary if available
            if "LLM_Summary" in course_data and content_chunks:
                summary = course_data["LLM_Summary"].get("summary", "")
                if summary:
                    chunk = {
                        "type": "course_summary",
                        "title": f"Summary: {course_data.get('title', '')}",
                        "content": summary,
                        "relevance_score": 0.4  # Give summary a decent score
                    }
                    content_chunks.append(chunk)
            
            # Sort by relevance
            content_chunks.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
            
            return content_chunks
            
        except Exception as e:
            logger.error(f"Error extracting content chunks: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return []

    def _transform_course_data(self, course_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform incoming course data to ensure it has the required structure
        
        This method handles different data formats, making sure they're compatible 
        with our internal data model, especially handling differences between
        'course' and 'course_info' fields
        """
        # Create a new dict to avoid modifying the original
        transformed_data = course_data.copy()
        
        # Handle course/course_info field inconsistency
        if "course" in transformed_data and "course_info" not in transformed_data:
            # Sample files like se-compact.json use 'course', API expects 'course_info'
            transformed_data["course_info"] = transformed_data["course"]
        elif "course_info" in transformed_data and "course" not in transformed_data:
            # In case we need the reverse transformation
            transformed_data["course"] = transformed_data["course_info"]
        
        # Ensure course_id exists and is numeric
        if "course_info" in transformed_data and transformed_data["course_info"]:
            course_info = transformed_data["course_info"]
            
            # If course_id is missing but code exists, use code as ID
            if "course_id" not in course_info and "code" in course_info:
                course_info["course_id"] = course_info["code"]
                logger.warning(f"Course ID missing, using code {course_info['code']} as ID")
            elif "course_id" not in course_info:
                # Generate a timestamp-based ID if no course_id or code
                course_info["course_id"] = str(int(datetime.now().timestamp()))
                logger.warning(f"Generated course ID: {course_info['course_id']}")
                
            # Ensure consistent ID format (prefer numeric, fallback to string)
            if "course_id" in course_info:
                # Store original ID for reference
                original_id = course_info["course_id"]
                # Consistent string representation
                course_info["course_id"] = str(original_id)
        
        # Handle weeks data format
        if "weeks" in transformed_data:
            weeks = transformed_data["weeks"]
            for i, week in enumerate(weeks):
                # Convert week_id to week_number if needed
                if "week_id" in week and "week_number" not in week:
                    week["week_number"] = week.get("week_id")
                # Rename 'order' to 'week_number' if needed
                if "order" in week and "week_number" not in week:
                    week["week_number"] = week.get("order")
                # Ensure description exists
                if "description" not in week:
                    week["description"] = f"Week {week.get('week_number', i+1)} content"
                    
                # Clean up week structure
                if "course_id" in week:
                    del week["course_id"]  # Remove redundant course_id from week
            
        # Handle lectures if present (from sample files)
        if "lectures" in transformed_data and transformed_data["lectures"]:
            for lecture in transformed_data["lectures"]:
                # Clean up fields we don't need
                if "week_id" in lecture:
                    # Just keep the reference, not the full object
                    lecture["week"] = lecture.get("week_id")
                
                # Ensure all lectures have descriptions
                if "description" not in lecture and "content_transcript" in lecture:
                    lecture["description"] = lecture.get("content_transcript", "")[:500]
                elif "description" not in lecture and "content_extract" in lecture:
                    lecture["description"] = lecture.get("content_extract", "")[:500]
                elif "description" not in lecture:
                    lecture["description"] = lecture.get("title", "Lecture")
            
        return transformed_data 

    def _extract_content_chunks(self, course_data: Union[CourseContent, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extract content chunks from a course for search results
        
        Args:
            course_data: The CourseContent object or dictionary
            
        Returns:
            List of content chunks for search results
        """
        chunks = []
        
        # Handle both CourseContent objects and dictionaries
        is_course_dict = isinstance(course_data, dict)
        
        # Add weeks
        weeks = course_data.get('weeks', []) if is_course_dict else course_data.weeks or []
        for week in weeks:
            is_dict = isinstance(week, dict)
            week_data = {
                "type": "week",
                "week_number": week.get('week_number', 0) if is_dict else week.week_number,
                "title": week.get('title', '') if is_dict else week.title,
                "description": week.get('description', '') if is_dict else week.description,
                "topics": week.get('topics', []) if is_dict else (week.topics if hasattr(week, "topics") else [])
            }
            chunks.append(week_data)
        
        # Add lectures
        lectures = course_data.get('lectures', []) if is_course_dict else course_data.lectures or []
        for lecture in lectures:
            is_dict = isinstance(lecture, dict)
            lecture_data = {
                "type": "lecture",
                "title": lecture.get('title', '') if is_dict else lecture.title,
                "description": lecture.get('content_transcript', '') if is_dict else (lecture.content_transcript or ''),
                "content": lecture.get('content_transcript', '') if is_dict else (lecture.content_transcript or ''),
                "week_number": lecture.get('week', 0) if is_dict else lecture.week
            }
            chunks.append(lecture_data)
        
        # Add assignments
        assignments = course_data.get('assignments', []) if is_course_dict else course_data.assignments or []
        for assignment in assignments:
            is_dict = isinstance(assignment, dict)
            assignment_data = {
                "type": "assignment",
                "title": assignment.get('title', '') if is_dict else assignment.title,
                "description": assignment.get('description', '') if is_dict else assignment.description,
                "due_date": assignment.get('due_date', '') if is_dict else assignment.due_date
            }
            chunks.append(assignment_data)
        
        return chunks

    def _build_course_content(self, course_data: Dict[str, Any]) -> CourseContent:
        """
        Build a CourseContent object from raw course data
        
        Args:
            course_data: Raw course data from ChromaDB
            
        Returns:
            CourseContent object
        """
        # Transform data to ensure it has the right structure
        course_data = self._transform_course_data(course_data)
        
        # Return as CourseContent object
        return CourseContent(**course_data) 

    async def search_courses(
        self, 
        query: str, 
        limit: int = 10, 
        course_ids: List[str] = None,
        min_score: float = 0.01,
        exact_match_boost: float = 0.1,
        phrase_match_boost: float = 0.15,
        description_threshold: float = 0.05
    ) -> List[Dict[str, Any]]:
        """Async wrapper for search_courses_sync with full parameter support"""
        return self.search_courses_sync(
            query=query, 
            limit=limit, 
            course_ids=course_ids,
            min_score=min_score,
            exact_match_boost=exact_match_boost,
            phrase_match_boost=phrase_match_boost,
            description_threshold=description_threshold
        ) 