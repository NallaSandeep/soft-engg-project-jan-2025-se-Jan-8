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
import math  # Import math module at the top level
from typing import List, Dict, Any, Optional, Union, Set
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
            
            # Extract acronyms and synonyms early
            acronyms = course_info.get("acronyms", {})
            synonyms = course_info.get("synonyms", {})
            acronyms_json = json.dumps(acronyms if acronyms else {})
            synonyms_json = json.dumps(synonyms if synonyms else {})
            logger.info(f"Prepared acronyms/synonyms JSON for course {course_code}")
            
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
                "course_concepts": ", ".join(course_info.get("LLM_Summary", {}).get("concepts_covered", [])),
                "acronyms_json": acronyms_json,  # Add serialized acronyms
                "synonyms_json": synonyms_json   # Add serialized synonyms
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
                    "duration_minutes": lecture.get("duration_minutes", 0),
                    "acronyms_json": acronyms_json,  # Add serialized acronyms
                    "synonyms_json": synonyms_json   # Add serialized synonyms
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
        course_ids: Optional[List[str]] = None,
        min_score: float = 0.01,
        exact_match_boost: float = 0.1,
        phrase_match_boost: float = 0.15,
        description_threshold: float = 0.05,
        metadata_expansion_limit: int = 20,
        expansion_query_limit: int = 3
    ) -> dict:
        """
        Search for course content by query, incorporating query expansion using
        acronyms and synonyms found in the metadata of initially retrieved chunks.
        """
        try:
            logger.info(f"DEBUG: Search called with query='{query}', limit={limit}, course_ids={course_ids}, min_score={min_score}")
            
            if not query or not query.strip():
                logger.warning("DEBUG: Empty query provided, returning empty results")
                return {"content_chunks": [], "total_count": 0, "query": query, "limit": limit}
            
            # 1. Lowercase and Normalize Query
            original_query_lower = query.lower()
            # Keep normalization for consistency? Or rely on embeddings? Let's keep it for now.
            normalized_query_lower = self._normalize_query(original_query_lower) 
            logger.info(f"DEBUG: Normalized query: '{normalized_query_lower}'")
            
            # Prepare filter based on course_ids
            filter_dict = {}
            safe_course_ids = []
            if course_ids:
                # Ensure course_ids are strings if they aren't already
                safe_course_ids = [str(cid) for cid in course_ids if cid] # Filter out empty/None IDs
                if safe_course_ids:
                    logger.info(f"DEBUG: Using course filter: {{'course_code': {{\'$in\': safe_course_ids}}}}\"")
                    # Assuming 'course_code' is the metadata field to filter on
                    filter_dict = {"course_code": {"$in": safe_course_ids}}
                else:
                    logger.warning("DEBUG: course_ids provided but were empty after validation.")
                    course_ids = None # Treat as no filter if validation results in empty list
            
            # Get collections (both needed now)
            content_collection = self.chroma.get_or_create_collection_sync(self.collection_name)
            selector_collection_name = "course-selector" # Assuming this is the name
            selector_collection = self.chroma.get_or_create_collection_sync(selector_collection_name)
            logger.info(f"DEBUG: Using collections: {self.collection_name}, {selector_collection_name}")

            # --- Query Expansion Logic ---
            aggregated_acronyms: Dict[str, str] = {}
            aggregated_synonyms: Dict[str, List[str]] = {}

            # --- Refined Metadata Gathering ---           
            if safe_course_ids: # If specific courses are targeted
                logger.info(f"DEBUG: Fetching metadata directly from {selector_collection_name} for courses: {safe_course_ids}")
                try:
                    # Use the get method of ChromaService which handles fetching by ID (course code)
                    selector_results = self.chroma.get_sync(
                        collection_name=selector_collection_name,
                        ids=safe_course_ids, # Fetch metadata for specified course codes
                        include=['metadatas'] # Only fetch metadata
                    )
                    
                    if selector_results and selector_results.metadatas:
                        logger.info(f"DEBUG: Got metadata from {len(selector_results.metadatas)} entries in {selector_collection_name}")
                        # --- Log retrieved metadata --- BEGIN
                        for i, metadata in enumerate(selector_results.metadatas):
                            if not metadata: continue
                            course_code = metadata.get('course_code', 'N/A')
                            acr_json = metadata.get('acronyms_json', '{}')
                            syn_json = metadata.get('synonyms_json', '{}')
                            logger.info(f"DEBUG: Metadata for {course_code} [Entry {i}]: AcronymsJSON=\"{acr_json}\", SynonymsJSON=\"{syn_json}\"")
                        # --- Log retrieved metadata --- END
                        for metadata in selector_results.metadatas:
                            if not metadata: continue
                            # Parse Acronyms (using same logic as before)
                            try:
                                acronyms_json = metadata.get("acronyms_json", '{}')
                                if acronyms_json and acronyms_json != '{}':
                                    acronyms = json.loads(acronyms_json)
                                    if isinstance(acronyms, dict):
                                        for k, v in acronyms.items():
                                            if k and v and k not in aggregated_acronyms:
                                                aggregated_acronyms[k.lower()] = str(v).lower()
                            except Exception as e:
                                logger.warning(f"DEBUG: Error parsing acronyms_json from course-selector metadata {metadata.get('code', '?')}: {e}")

                            # Parse Synonyms (using same logic as before)
                            try:
                                synonyms_json = metadata.get("synonyms_json", '{}')
                                if synonyms_json and synonyms_json != '{}':
                                    synonyms = json.loads(synonyms_json)
                                    if isinstance(synonyms, dict):
                                        for k, v_list in synonyms.items():
                                            if k and isinstance(v_list, list):
                                                lower_k = k.lower()
                                                lower_v_list = [str(v).lower() for v in v_list if v]
                                                if lower_k not in aggregated_synonyms:
                                                    aggregated_synonyms[lower_k] = []
                                                for syn in lower_v_list:
                                                     if syn not in aggregated_synonyms[lower_k]:
                                                         aggregated_synonyms[lower_k].append(syn)
                            except Exception as e:
                                logger.warning(f"DEBUG: Error parsing synonyms_json from course-selector metadata {metadata.get('code', '?')}: {e}")
                    else:
                        logger.warning(f"DEBUG: No results or metadata found in {selector_collection_name} for IDs: {safe_course_ids}")

                except Exception as e:
                    logger.error(f"DEBUG: Failed to fetch metadata from {selector_collection_name}: {e}", exc_info=True)
                    # Continue without metadata if selector fetch fails, fallback handled below

            # Fallback or If NO course_ids were provided: Use initial search on course-content
            if not aggregated_acronyms and not aggregated_synonyms and not safe_course_ids:
                logger.info(f"DEBUG: No course filter or metadata found from {selector_collection_name}. Performing initial search on {self.collection_name} for metadata.")
                try:
                    initial_results = self.chroma.search_sync(
                    collection_name=self.collection_name,
                        query=normalized_query_lower,
                        n_results=metadata_expansion_limit, # Fetch results for metadata
                        where=filter_dict, # Will be empty if no course_ids
                        include=['metadatas'] # Only need metadata
                    )

                    if initial_results and initial_results.metadatas:
                        logger.info(f"DEBUG: Extracting metadata from {len(initial_results.metadatas)} initial {self.collection_name} results.")
                        for metadata in initial_results.metadatas:
                            if not metadata: continue
                            # Parse Acronyms (same logic)
                            try:
                                acronyms_json = metadata.get("acronyms_json", '{}')
                                if acronyms_json and acronyms_json != '{}':
                                    acronyms = json.loads(acronyms_json)
                                    if isinstance(acronyms, dict):
                                        for k, v in acronyms.items():
                                            if k and v and k not in aggregated_acronyms:
                                                aggregated_acronyms[k.lower()] = str(v).lower()
                            except Exception as e:
                                logger.warning(f"DEBUG: Error parsing acronyms_json from course-content metadata: {e}")
                            # Parse Synonyms (same logic)
                            try:
                                synonyms_json = metadata.get("synonyms_json", '{}')
                                if synonyms_json and synonyms_json != '{}':
                                    synonyms = json.loads(synonyms_json)
                                    if isinstance(synonyms, dict):
                                        for k, v_list in synonyms.items():
                                            if k and isinstance(v_list, list):
                                                lower_k = k.lower()
                                                lower_v_list = [str(v).lower() for v in v_list if v]
                                                if lower_k not in aggregated_synonyms:
                                                    aggregated_synonyms[lower_k] = []
                                                for syn in lower_v_list:
                                                     if syn not in aggregated_synonyms[lower_k]:
                                                         aggregated_synonyms[lower_k].append(syn)
                            except Exception as e:
                                logger.warning(f"DEBUG: Error parsing synonyms_json from course-content metadata: {e}")
                except Exception as e:
                    logger.error(f"DEBUG: Initial search on {self.collection_name} failed: {e}", exc_info=True)
                    # Proceed without expansion if initial search fails

            logger.info(f"DEBUG: Aggregated {len(aggregated_acronyms)} unique acronyms and {len(aggregated_synonyms)} synonym keys for expansion.")
            if aggregated_acronyms or aggregated_synonyms:
                logger.debug(f"DEBUG: Using Acronyms: {aggregated_acronyms}")
                logger.debug(f"DEBUG: Using Synonyms: {aggregated_synonyms}")
            
            # --- Expansion Term Generation ---
            expansion_terms: Set[str] = set()
            query_tokens = normalized_query_lower.split()

            for token in query_tokens:
                # Acronym Key -> Full Form
                if token in aggregated_acronyms:
                    expansion_terms.add(aggregated_acronyms[token])
                
                # Synonym Key -> Synonyms List
                if token in aggregated_synonyms:
                    expansion_terms.update(aggregated_synonyms[token])

                # Acronym Value (Full Form) -> Acronym Key
                for acr_key, acr_val in aggregated_acronyms.items():
                    if token == acr_val:
                        expansion_terms.add(acr_key)

                # Synonym Value -> Synonym Key
                for syn_key, syn_list in aggregated_synonyms.items():
                    if token in syn_list:
                        expansion_terms.add(syn_key)

            # Remove original query tokens from expansion terms to avoid redundancy
            expansion_terms.difference_update(query_tokens)
            logger.info(f"DEBUG: Found {len(expansion_terms)} potential expansion terms: {expansion_terms}")

            # Initialize the all_search_results dictionary
            all_search_results = {}
            
            # Perform the main search
            main_results = self.chroma.search_sync(
                collection_name=self.collection_name,
                query=normalized_query_lower,
                n_results=limit * 2,  # Get more results than needed to account for filtering
                where=filter_dict,
                include=['metadatas', 'documents', 'distances']
            )
            
            if main_results and main_results.ids:
                logger.info(f"DEBUG: Raw search returned {len(main_results.ids)} results")
                for i, (result_id, metadata, document, distance) in enumerate(
                    zip(main_results.ids, main_results.metadatas, main_results.documents, main_results.distances)
                ):
                    # Calculate a score that works for distances > 1.0
                    # For distances > 1.0, use an exponential decay function
                    if distance <= 1.0:
                        score = 1.0 - distance
                    else:
                        # Use exp(-x) to map large distances to small positive scores
                        # For large distances like 1.65, score ≈ 0.19
                        score = math.exp(-distance)
                    
                    # Log the first few results with more precision on the score
                    if i < 5:
                        logger.info(f"DEBUG: Result {i}: ID={result_id}, distance={distance}, score={score:.8f}, min_score={min_score}")
                    
                    if result_id not in all_search_results:
                        # Very low threshold to capture any remotely relevant results
                        effective_min_score = 0.00001  # Extremely low threshold
                        
                        if score >= effective_min_score:
                            all_search_results[result_id] = {
                                'id': result_id,
                                'metadata': metadata,
                                'content': document,
                                'relevance_score': score
                            }
                        elif i < 5:  # Only log the first few filtered results
                            logger.info(f"DEBUG: Result {i} filtered out due to low score: {score:.8f} < {effective_min_score}")

            # --- Final Ranking and Limiting ---
            logger.info(f"DEBUG: Total results before final sorting: {len(all_search_results)}")
            
            # 8. Sort by relevance score in descending order
            sorted_results = sorted(
                all_search_results.values(), 
                key=lambda x: x['relevance_score'], 
                reverse=True
            )
            
            # 9. Limit the number of results
            final_results = sorted_results[:limit]
            
            logger.info(f"DEBUG: Final results count: {len(final_results)} for original query: '{query}'")
            
            # Log first few results for inspection
            if final_results:
                 logger.info("DEBUG: Top 3 final results:")
                 for i, res in enumerate(final_results[:3]):
                     logger.info(f"DEBUG: Rank {i+1}: ID={res.get('id')}, Score={res.get('relevance_score'):.4f}, Type={res.get('metadata', {}).get('content_type')}, Title={res.get('metadata', {}).get('lecture_title', res.get('metadata', {}).get('course_title', 'N/A'))}")
            
            return {
                "content_chunks": final_results, # Return the list of result dicts
                "total_count": len(final_results),
                "query": query, # Return original user query
                "limit": limit
            }
            
        except Exception as e:
            logger.error(f"Error searching courses: {str(e)}", exc_info=True) # Log full traceback
            # Return empty structure on error
            return {"content_chunks": [], "total_count": 0, "query": query, "limit": limit}

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
        course_ids: Optional[List[str]] = None,
        min_score: float = 0.01,
        exact_match_boost: float = 0.1,
        phrase_match_boost: float = 0.15,
        description_threshold: float = 0.05,
        metadata_expansion_limit: int = 20,
        expansion_query_limit: int = 3
    ) -> List[Dict[str, Any]]:
        """Async wrapper for search_courses_sync with query expansion"""
        # The sync function now returns a dictionary, not just the list of chunks.
        # Adjust the return type or how the API layer handles this.
        # For now, let's assume the API layer expects the dictionary.
        result_dict = self.search_courses_sync(
            query=query, 
            limit=limit, 
            course_ids=course_ids,
            min_score=min_score,
            exact_match_boost=exact_match_boost,
            phrase_match_boost=phrase_match_boost,
            description_threshold=description_threshold,
            metadata_expansion_limit=metadata_expansion_limit,
            expansion_query_limit=expansion_query_limit
        ) 
        # If the API absolutely needs just the list: return result_dict.get("content_chunks", [])
        # But it's better practice to return the full dictionary with context.
        return result_dict # Return the dictionary 