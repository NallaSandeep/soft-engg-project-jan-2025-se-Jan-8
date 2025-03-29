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
        
    def add_course_content_sync(self, course_content: Union[Dict[str, Any], CourseContent]) -> str:
        """Synchronous version of add_course_content"""
        if not self._initialized:
            self.initialize_sync()
            
        # Convert to dict if CourseContent object
        if isinstance(course_content, CourseContent):
            course_data = course_content.dict()
        else:
            course_data = course_content
            
        # Transform data format if needed
        course_data = self._transform_course_data(course_data)
            
        # Extract course info
        course_info = course_data.get("course_info", {})
        if not course_info:
            raise ValueError("Course data must contain course information")
            
        course_id = course_info.get("course_id")
        if not course_id:
            # Generate a default ID if none provided
            course_id = str(int(datetime.now().timestamp()))
            logger.warning(f"No course_id provided, generated default: {course_id}")
            course_info["course_id"] = course_id
            course_data["course_info"] = course_info
            
        # Ensure course_id is a string
        course_id_str = str(course_id)
        
        # Create a combined text for embedding that captures the essence of the course
        title = course_info.get("title", "")
        description = course_info.get("description", "")
        
        # Get topics
        topics = course_data.get("topics", [])
        topic_texts = [topic.get("name", "") for topic in topics]
        
        # Get concepts covered
        concepts_covered = course_data.get("concepts_covered", [])
        concepts_not_covered = course_data.get("concepts_not_covered", [])
        
        # Get weeks data
        weeks = course_data.get("weeks", [])
        week_texts = []
        for week in weeks:
            week_title = week.get("title", "")
            week_description = week.get("description", "")
            week_texts.append(f"{week_title}: {week_description}")
        
        # Combine all text for embedding
        combined_text = f"COURSE: {title}\nDESCRIPTION: {description}\n"
        
        if topic_texts:
            combined_text += "TOPICS: " + ", ".join(topic_texts) + "\n"
            
        if concepts_covered:
            combined_text += "CONCEPTS COVERED: " + ", ".join(concepts_covered) + "\n"
            
        if concepts_not_covered:
            combined_text += "CONCEPTS NOT COVERED: " + ", ".join(concepts_not_covered) + "\n"
            
        if week_texts:
            combined_text += "WEEKS: " + " | ".join(week_texts)
        
        # Generate embedding
        embedding = self.embedder.generate_embedding(combined_text)
        
        # Store the full course content as a JSON string in the document
        document = json.dumps(course_data)
        
        # Prepare metadata
        metadata = {
            "course_id": course_id_str,
            "code": course_info.get("code", ""),
            "title": title,
            "description": description[:1000] if description else "",  # Truncate for metadata limits
            "department": course_info.get("department", ""),
            "credits": str(course_info.get("credits", 0)),
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "week_count": str(len(weeks)) if weeks else "0",
            "topic_count": str(len(topics)) if topics else "0",
        }
        
        # Store in ChromaDB
        ids = self.chroma.add_documents_sync(
            collection_name=self.collection_name,
            documents=[document],
            metadatas=[metadata],
            ids=[course_id_str],
            embeddings=[embedding]
        )
        
        logger.info(f"Added course content for {title} (ID: {course_id_str})")
        return course_id_str
    
    async def add_course_content(self, course_content: Union[Dict[str, Any], CourseContent]) -> str:
        """Async wrapper for add_course_content_sync"""
        return self.add_course_content_sync(course_content)
        
    def get_course_content_sync(self, course_id: Union[int, str]) -> Optional[CourseContent]:
        """Synchronous version of get_course_content"""
        if not self._initialized:
            self.initialize_sync()
            
        course_id_str = str(course_id)
        
        try:
            # Try direct lookup first
            result = self.chroma.get_sync(
                collection_name=self.collection_name,
                ids=[course_id_str]
            )
            
            # If not found and looks like a course code (contains letters)
            if (not result.ids or len(result.ids) == 0) and any(c.isalpha() for c in course_id_str):
                # Try searching by code field in metadata
                search_results = self.chroma.search_sync(
                    collection_name=self.collection_name,
                    query="",
                    n_results=1,
                    where={"code": course_id_str}
                )
                
                if search_results.ids and len(search_results.ids) > 0:
                    # Get full document using the found ID
                    result = self.chroma.get_sync(
                        collection_name=self.collection_name,
                        ids=[search_results.ids[0]]
                    )
                    logger.info(f"Found course with code {course_id_str}, ID: {search_results.ids[0]}")
            
            if not result.documents or len(result.documents) == 0:
                logger.warning(f"Course content with ID {course_id} not found")
                return None
                
            # Parse the document JSON
            try:
                course_data = json.loads(result.documents[0])
                
                # Transform data to ensure it has the right structure
                course_data = self._transform_course_data(course_data)
                
                # Return as CourseContent object
                return CourseContent(**course_data)
            except json.JSONDecodeError:
                logger.error(f"Error parsing course content JSON for ID {course_id}")
                return None
        except Exception as e:
            logger.error(f"Error retrieving course content: {str(e)}")
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
        
        try:
            # Delete the course from ChromaDB
            self.chroma.delete_sync(
                collection_name=self.collection_name,
                ids=[course_id_str]
            )
            
            logger.info(f"Deleted course content with ID: {course_id_str}")
            return True
        except Exception as e:
            logger.error(f"Error deleting course content: {str(e)}")
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
    
    def search_courses_sync(self, query: str, limit: int = 10, course_ids: List[str] = None) -> List[Dict[str, Any]]:
        """
        Search for course content matching the query string
        
        This is the core RAG retrieval functionality for StudyAI. It returns specific 
        content chunks (lectures, topics, week content) that match the query, not just 
        course metadata. This allows StudyAI to use these content chunks for retrieval-augmented
        generation.
        
        Args:
            query: The search query string
            limit: Maximum number of results to return
            course_ids: Optional list of course IDs to filter the search results
            
        Returns:
            List of content chunks with their metadata, relevance scores, and source information
        """
        if not self._initialized:
            self.initialize_sync()
            
        try:
            # Generate embedding for the query
            query_embedding = self.embedder.generate_embedding(query)
            
            # Prepare the where clause for filtering by course IDs if provided
            where_clause = None
            if course_ids:
                # Convert all IDs to strings for consistency
                course_ids = [str(cid) for cid in course_ids]
                where_clause = {"course_id": {"$in": course_ids}}
            
            # Search for matching documents
            results = self.chroma.search_sync(
                collection_name=self.collection_name,
                query_embeddings=[query_embedding],
                where=where_clause,
                n_results=limit
            )
            
            if not results.ids:
                return []
                
            # Process results to extract content chunks
            content_chunks = []
            for i, doc_id in enumerate(results.ids):
                try:
                    # Extract document and metadata
                    doc_content = json.loads(results.documents[i])
                    metadata = results.metadatas[i]
                    
                    # Convert distance to similarity score (higher is better)
                    similarity = max(0.0, min(1.0, 1.0 - 0.5 * results.distances[i]))
                    
                    # Extract course info for source reference
                    course_info = doc_content.get("course_info", {})
                    if not course_info and "course" in doc_content:
                        course_info = doc_content.get("course", {})
                        
                    # Basic course information
                    course_data = {
                        "course_id": metadata.get("course_id"),
                        "code": metadata.get("code", ""),
                        "title": metadata.get("title", ""),
                        "department": metadata.get("department", ""),
                        "match_score": similarity
                    }
                    
                    # Extract relevant content chunks based on query
                    chunks = self._extract_relevant_chunks(doc_content, query)
                    
                    # Add source information and chunks to result
                    content_chunks.append({
                        "source_course": course_data,
                        "content_chunks": chunks,
                        "score": similarity
                    })
                except json.JSONDecodeError:
                    logger.error(f"Error parsing document JSON for ID {doc_id}")
                except Exception as e:
                    logger.error(f"Error processing search result: {str(e)}")
                
            return content_chunks
        except Exception as e:
            logger.error(f"Error searching courses: {str(e)}")
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