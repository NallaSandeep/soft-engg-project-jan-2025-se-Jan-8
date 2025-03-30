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
from typing import List, Dict, Any, Optional, Union
from datetime import datetime

from ..models.course_selector import CourseInfo, CourseTopic, CourseContent, WeekOverview
from .chroma import ChromaService
from .embeddings import EmbeddingService

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
        """Synchronous version of initialize"""
        if self._initialized:
            return True
            
        try:
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
            return True
        except Exception as e:
            logger.error(f"Failed to initialize CourseContent service: {str(e)}")
            return False
    
    async def initialize(self) -> bool:
        """Async wrapper for initialize_sync"""
        return self.initialize_sync()
        
    def add_course_content_sync(self, course_data: Dict[str, Any]) -> Union[int, str]:
        """Synchronous version of add_course_content"""
        if not self._initialized:
            self.initialize_sync()
            
        try:
            # Validate course data has the right structure
            if "course" not in course_data:
                logger.error("Invalid course data - missing 'course' key")
                raise ValueError("Invalid course data format - missing 'course' key")
                
            course_info = course_data["course"]
            if not course_info:
                logger.error("Empty course information")
                raise ValueError("Course information is empty")
                
            # Extract key course metadata
            course_id = course_info.get("course_id")
            if not course_id:
                logger.warning("Course ID missing, will generate a new one")
                course_id = str(uuid.uuid4())
                course_info["course_id"] = course_id
                
            # Get course code and title for logging/identification
            course_code = course_info.get("code", "Unknown")
            course_title = course_info.get("title", "Unknown")
            
            logger.info(f"Adding/updating course: ID={course_id}, Code={course_code}, Title={course_title}")
            
            # Check if a course with this code already exists
            try:
                search_results = self.chroma.search_sync(
                    collection_name=self.collection_name,
                    query="",
                    n_results=1,
                    where={"code": course_code}
                )
                
                if search_results.ids and len(search_results.ids) > 0:
                    existing_id = search_results.ids[0]
                    existing_metadata = search_results.metadatas[0] if search_results.metadatas else {}
                    logger.warning(f"Course with code {course_code} already exists with ID {existing_id}, metadata: {existing_metadata}")
            except Exception as e:
                logger.error(f"Error checking for existing course: {str(e)}")
            
            # Prepare metadata and store the course document
            metadata = {
                "course_id": course_id,
                "code": course_code,
                "title": course_title,
                "department": course_info.get("department", "Computer Science"),
                "added_on": datetime.now().isoformat()
            }
            
            logger.info(f"Adding to ChromaDB with metadata: {metadata}")
            
            # Convert course data to a string for storage
            course_json = json.dumps(course_data)
            
            # Add document to ChromaDB
            result_ids = self.chroma.add_documents_sync(
                collection_name=self.collection_name,
                documents=[course_json],
                metadatas=[metadata],
                ids=[str(course_id)]
            )
            
            logger.info(f"Course added with IDs: {result_ids}")
            
            return course_id
        except Exception as e:
            logger.error(f"Error adding course content: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            raise
    
    async def add_course_content(self, course_content: Union[Dict[str, Any], CourseContent]) -> str:
        """Async wrapper for add_course_content_sync"""
        return self.add_course_content_sync(course_content)
        
    def get_course_content_sync(self, course_id: Union[int, str]) -> Optional[CourseContent]:
        """Synchronous version of get_course_content"""
        if not self._initialized:
            self.initialize_sync()
            
        try:
            # Convert to string for consistency
            course_id_str = str(course_id)
            logger.info(f"Getting course content for ID/code: {course_id_str}")
            
            # First try direct lookup by ID
            try:
                direct_results = self.chroma.get_sync(
                    collection_name=self.collection_name,
                    ids=[course_id_str]
                )
                
                if direct_results.ids and len(direct_results.ids) > 0:
                    logger.info(f"Found course with direct ID lookup: {course_id_str}")
                    metadata = direct_results.metadatas[0] if direct_results.metadatas else {}
                    document = direct_results.documents[0] if direct_results.documents else None
                    
                    if document:
                        try:
                            course_data = json.loads(document)
                            return self._build_course_content(course_data)
                        except json.JSONDecodeError:
                            logger.error(f"Error parsing JSON for course ID {course_id_str}")
                    else:
                        logger.warning(f"No document content found for course ID {course_id_str}")
            except Exception as e:
                logger.error(f"Error in direct ID lookup: {str(e)}")
            
            # If direct lookup fails, try search by code or other means
            search_params = {}
            
            # Check if course_id might be a course code (contains letters)
            if any(c.isalpha() for c in course_id_str):
                logger.info(f"Trying to find course by code: {course_id_str}")
                search_params["where"] = {"code": course_id_str}
            # If it's numeric, try both as string and int
            elif course_id_str.isdigit():
                numeric_id = int(course_id_str)
                logger.info(f"Trying to find course by numeric ID: {numeric_id}")
                search_params["where"] = {"$or": [
                    {"course_id": numeric_id},
                    {"course_id": course_id_str}
                ]}
            else:
                # Last resort - try with empty query
                logger.info(f"Using fallback search with no filter for ID: {course_id_str}")
            
            # Search with empty query to find by metadata filter
            search_results = self.chroma.search_sync(
                collection_name=self.collection_name,
                query="",
                n_results=1,
                **search_params
            )
            
            if search_results.ids and len(search_results.ids) > 0:
                doc_id = search_results.ids[0]
                logger.info(f"Found course via search, actual ID: {doc_id}")
                
                # Get full document by ID
                found_results = self.chroma.get_sync(
                    collection_name=self.collection_name,
                    ids=[doc_id]
                )
                
                if found_results.ids and len(found_results.ids) > 0:
                    document = found_results.documents[0] if found_results.documents else None
                    
                    if document:
                        try:
                            course_data = json.loads(document)
                            return self._build_course_content(course_data)
                        except json.JSONDecodeError:
                            logger.error(f"Error parsing JSON for found course ID {doc_id}")
                    else:
                        logger.warning(f"No document content found for course ID {doc_id}")
            
            logger.warning(f"Course with ID/code {course_id_str} not found")
            return None
        except Exception as e:
            logger.error(f"Error getting course content: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
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
        """Synchronous version of list_courses"""
        if not self._initialized:
            self.initialize_sync()
            
        try:
            # Get all course documents with pagination
            result = self.chroma.get_collection_docs_sync(
                collection_name=self.collection_name,
                limit=limit,
                offset=offset
            )
            
            if not result.ids:
                return []
                
            # Extract basic info from metadata
            courses = []
            for i, doc_id in enumerate(result.ids):
                metadata = result.metadatas[i]
                courses.append({
                    "course_id": metadata.get("course_id"),
                    "code": metadata.get("code", ""),
                    "title": metadata.get("title", ""),
                    "department": metadata.get("department", ""),
                    "credits": int(metadata.get("credits", 0)),
                    "week_count": int(metadata.get("week_count", 0)),
                    "created_at": metadata.get("created_at")
                })
                
            return courses
        except Exception as e:
            logger.error(f"Error listing courses: {str(e)}")
            return []
    
    async def list_courses(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Async wrapper for list_courses_sync"""
        return self.list_courses_sync(limit, offset)
    
    def search_courses_sync(
        self, 
        query: str = "",
        limit: int = 10,
        course_ids: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Synchronous version of search_courses"""
        if not self._initialized:
            self.initialize_sync()
            
        try:
            # Generate embedding for query
            query_embedding = None
            if query and len(query.strip()) > 0:
                logger.info(f"Generating embedding for query: '{query}'")
                query_embedding = self.embedder.generate_embedding(query.strip())
            
            # Set up filter if course_ids are provided
            where_clause = None
            if course_ids and len(course_ids) > 0:
                # Simply filter by course code - this is the most reliable method
                logger.info(f"Filtering search by course_ids: {course_ids}")
                where_clause = {"code": {"$in": course_ids}}
                logger.info(f"Using where clause: {where_clause}")
            
            # Execute search
            logger.info(f"Calling ChromaDB search with: query='{query}', embedding={'Yes' if query_embedding else 'No'}, where={where_clause}")
            
            # Basic parameters
            search_params = {
                "collection_name": self.collection_name,
                "n_results": limit
            }
            
            # Add where clause if provided
            if where_clause:
                search_params["where"] = where_clause
                
            # Use embedding if available, otherwise use the text query
            if query_embedding:
                search_params["query"] = ""  # Must be empty when using embedding
                search_params["query_embedding"] = query_embedding
            else:
                search_params["query"] = query
            
            # Execute search
            search_results = self.chroma.search_sync(**search_params)
                
            if not search_results.ids or len(search_results.ids) == 0:
                logger.info(f"No results found for query: '{query}'")
                return []
            
            logger.info(f"Found {len(search_results.ids)} results")
            
            # Process results
            results = []
            processed_courses = set()
            
            for i, doc_id in enumerate(search_results.ids):
                try:
                    metadata = search_results.metadatas[i]
                    document = search_results.documents[i] if hasattr(search_results, 'documents') and search_results.documents else None
                    
                    # Get course ID and code from metadata
                    course_id = metadata.get("course_id", doc_id)
                    course_code = metadata.get("code", "Unknown")
                    
                    # Skip if we've already processed this course
                    if course_code in processed_courses:
                        continue
                        
                    processed_courses.add(course_code)
                    
                    # Try to parse the document to get course data
                    course_data = None
                    if document:
                        try:
                            json_data = json.loads(document)
                            course_data = self._build_course_content(json_data)
                        except:
                            logger.warning(f"Could not parse document for course {course_code}")
                    
                    # If failed, fall back to get_course_content_sync
                    if not course_data:
                        course_data = self.get_course_content_sync(course_code)
                        
                    if not course_data:
                        logger.warning(f"Could not retrieve data for course {course_code}")
                        continue
                    
                    # Extract content chunks
                    content_chunks = self._extract_content_chunks(course_data)
                    
                    # Calculate score
                    score = 1.0 - min(1.0, search_results.distances[i])
                    
                    # Build result according to API spec format
                    source_course = {
                        "code": course_data.course.code,
                        "title": course_data.course.title,
                        "match_score": score
                    }
                    
                    results.append({
                        "source_course": source_course,
                        "content_chunks": content_chunks,
                        "score": score
                    })
                    
                    logger.info(f"Added course {course_code} to results with {len(content_chunks)} chunks")
                except Exception as e:
                    logger.error(f"Error processing search result: {str(e)}")
                    import traceback
                    logger.error(traceback.format_exc())
            
            logger.info(f"Returning {len(results)} courses with content")
            return results
        except Exception as e:
            logger.error(f"Error in search_courses_sync: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return []
    
    def _extract_relevant_chunks(self, doc_content: Dict[str, Any], query: str) -> List[Dict[str, Any]]:
        """
        Extract content chunks from the document that are most relevant to the query
        
        This extracts lectures, topics, and week content that matches the query
        for use in RAG applications.
        """
        chunks = []
        
        # Extract weeks content
        if "weeks" in doc_content and doc_content["weeks"]:
            for week in doc_content["weeks"]:
                week_chunk = {
                    "type": "week",
                    "week_number": week.get("week_number"),
                    "title": week.get("title"),
                    "description": week.get("description"),
                    "topics": week.get("topics", [])
                }
                chunks.append(week_chunk)
                
        # Extract lecture content
        if "lectures" in doc_content and doc_content["lectures"]:
            for lecture in doc_content["lectures"]:
                # Include the most relevant parts of the lecture for RAG
                lecture_chunk = {
                    "type": "lecture",
                    "title": lecture.get("title"),
                    "description": lecture.get("description"),
                    "content": lecture.get("content", lecture.get("content_transcript", "")),
                    "week_number": lecture.get("week")
                }
                chunks.append(lecture_chunk)
                
        # Extract topic content
        if "topics" in doc_content and doc_content["topics"]:
            for topic in doc_content["topics"]:
                topic_chunk = {
                    "type": "topic",
                    "name": topic.get("name"),
                    "description": topic.get("description")
                }
                chunks.append(topic_chunk)
                
        # Extract assignment content if available
        if "assignments" in doc_content and doc_content["assignments"]:
            for assignment in doc_content["assignments"]:
                assignment_chunk = {
                    "type": "assignment",
                    "title": assignment.get("title"),
                    "description": assignment.get("description"),
                    "due_date": assignment.get("due_date")
                }
                chunks.append(assignment_chunk)
                
        return chunks
    
    async def search_courses(self, query: str, limit: int = 10, course_ids: List[str] = None) -> List[Dict[str, Any]]:
        """Async wrapper for search_courses_sync"""
        return self.search_courses_sync(query, limit, course_ids)

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