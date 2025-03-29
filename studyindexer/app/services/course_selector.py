"""
CourseSelector service for matching queries to relevant courses
This service helps identify which courses from a student's subscribed courses
are relevant to their query.

PROJECT GOALS:
------------
The StudyIndexer module serves as a RAG (Retrieval Augmented Generation) data source for StudyAI.
It consists of two main components:

1. StudySelector (This Service): Helps identify which courses contain information relevant to a query
   - Primary function: Find courses matching a query from a student's subscribed courses
   - Returns: Matching courses with topics, relevance scores, and week information
   - Purpose: Help students find which courses to focus on for specific topics

2. CourseContent: Provides actual content chunks for RAG applications
   - Primary function: Retrieve specific content (lectures, topics, etc.) matching a query
   - Returns: Content chunks with source information for use in RAG by StudyAI
   
The StudySelector complements CourseContent by providing a "course-level" search
that helps narrow down which courses to draw content from, while CourseContent provides 
the detailed content for RAG applications.

Important note on IDs:
- course_id: A local numeric identifier for the course in our system
- code: The course code used in StudyHub (e.g., "CS101") which serves as the common 
  identifier across systems. When integrating with StudyHub, use the code field.
"""
import os
import json
import time
import logging
from typing import List, Dict, Any, Optional, Tuple, Union
from datetime import datetime
import asyncio

from ..models.course_selector import (
    CourseInfo,
    CourseSelectorQuery,
    CourseMatchResult
)
from .chroma import ChromaService
from .embeddings import EmbeddingService

logger = logging.getLogger(__name__)

class CourseSelectorService:
    """Service for matching queries to relevant courses"""
    
    _instance = None
    
    def __new__(cls):
        """Singleton pattern to ensure only one instance is created"""
        if cls._instance is None:
            cls._instance = super(CourseSelectorService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the CourseSelector service"""
        if getattr(self, '_initialized', False):
            return
            
        # Initialize dependencies
        self.chroma = ChromaService()
        self.embedder = EmbeddingService()
        
        # Set collection name for course data
        self.collection_name = "course-selector"
        
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
                metadata={"description": "Course content for finding relevant courses"}
            )
            
            self._initialized = True
            return True
        except Exception as e:
            logger.error(f"Failed to initialize CourseSelector service: {str(e)}")
            return False
    
    async def initialize(self) -> bool:
        """Async version of initialize for API use"""
        return self.initialize_sync()
    
    def index_course_sync(self, course_data: Dict[str, Any]) -> str:
        """
        Index a course for semantic search
        
        Args:
            course_data: Dictionary containing course information with the following structure:
                - course: CourseInfo object or dict with course details
                - weeks: Optional list of week information
                
        Returns:
            The course_id as a string
        """
        if not self._initialized:
            self.initialize_sync()
            
        course_info = course_data.get("course", {})
        
        # Handle course_id - generate a default if not provided
        course_id = course_info.get("course_id")
        if not course_id:
            # Generate a timestamp-based ID if none provided
            course_id = str(int(time.time()))
            logger.warning(f"No course_id provided, generated default: {course_id}")
            course_info["course_id"] = course_id
            course_data["course"] = course_info
            
        # Convert course_id to string if it's not already
        course_id = str(course_id)
            
        # Create combined text for embedding
        combined_text = self._create_course_embedding_text(course_data)
        
        # Generate embedding
        embedding = self.embedder.generate_embedding(combined_text)
        
        # Extract concepts and summary
        concepts = self._extract_concepts(course_data)
        llm_summary = course_info.get("LLM_Summary", {})
        summary = llm_summary.get("summary", "")
        
        # Check for required fields, use defaults for missing ones
        code = course_info.get("code", f"COURSE{course_id}")
        title = course_info.get("title", "Untitled Course")
        description = course_info.get("description", "")
        department = course_info.get("department", "General")
        credits = str(course_info.get("credits", 0))
        
        # Prepare metadata
        metadata = {
            "course_id": course_id,
            "code": code,
            "title": title,
            "description": description[:1000],  # Truncate for metadata limits
            "department": department,
            "credits": credits,
            "concepts_covered": ",".join(concepts),
            "summary": summary[:1000],  # Truncate for metadata limits
            "indexed_at": datetime.utcnow().isoformat()
        }
        
        # Store in ChromaDB
        self.chroma.add_documents_sync(
            collection_name=self.collection_name,
            documents=[combined_text],
            metadatas=[metadata],
            ids=[course_id],
            embeddings=[embedding]
        )
        
        logger.info(f"Indexed course {metadata['title']} (ID: {course_id})")
        return course_id
    
    async def index_course(self, course_data: Dict[str, Any]) -> str:
        """Async version of index_course for API use"""
        return self.index_course_sync(course_data)
    
    async def bulk_index_courses_from_files(self, file_paths: List[str]) -> Dict[str, Any]:
        """Index multiple courses from JSON files"""
        results = {
            "success": True,
            "total_indexed": 0,
            "failed": [],
            "indexed": []
        }
        
        for file_path in file_paths:
            try:
                with open(file_path, 'r') as f:
                    course_data = json.load(f)
                
                course_id = self.index_course_sync(course_data)
                results["indexed"].append({
                    "file": file_path,
                    "course_id": course_id
                })
                results["total_indexed"] += 1
            except Exception as e:
                results["failed"].append({
                    "file": file_path,
                    "error": str(e)
                })
                
        if results["failed"]:
            results["success"] = False
            
        return results
    
    async def get_course(self, course_id: int) -> Dict[str, Any]:
        """Get course details by ID"""
        if not self._initialized:
            self.initialize_sync()
            
        # Convert course_id to string for ChromaDB
        str_id = str(course_id)
        
        # Using the get method to retrieve course by ID
        result = self.chroma.get_sync(
            collection_name=self.collection_name,
            ids=[str_id]
        )
        
        if not result or not result.ids:
            return None
            
        # Return the metadata as course info
        return result.metadatas[0]
    
    def select_courses_sync(self, search_query: CourseSelectorQuery) -> Tuple[int, List[CourseMatchResult], float]:
        """Find relevant courses based on a search query and subscribed courses"""
        if not self._initialized:
            self.initialize_sync()
            
        start_time = time.time()
        
        # Filter courses by subscribed_courses
        str_course_ids = [str(cid) for cid in search_query.subscribed_courses]
        where_clause = {
            "$or": [{"course_id": cid} for cid in str_course_ids]
        }
        
        # Generate embedding for query
        search_text = search_query.query if search_query.query else ""
        
        # If empty query and min_score is 0, just return all matching courses
        if not search_text and search_query.min_score == 0:
            results = self.chroma.search_sync(
                collection_name=self.collection_name,
                query="",
                n_results=search_query.limit,
                where=where_clause
            )
            return self._process_search_results(results, start_time)
            
        # For semantic search, generate embedding
        query_embedding = self.embedder.generate_embedding(search_text)
        
        # Search collection
        results = self.chroma.search_sync(
            collection_name=self.collection_name,
            query="",
            query_embedding=query_embedding,
            n_results=search_query.limit,
            where=where_clause
        )
        
        return self._process_search_results(results, start_time)
    
    async def select_courses(self, search_query: CourseSelectorQuery) -> Tuple[int, List[CourseMatchResult], float]:
        """Async version of select_courses for API use"""
        # Direct call to sync version and return its result
        return self.select_courses_sync(search_query)
    
    def _create_course_embedding_text(self, course_data: Dict[str, Any]) -> str:
        """Create text for embedding from course data"""
        course_info = course_data.get("course", {})
        llm_summary = course_info.get("LLM_Summary", {})
        
        # Combine course information
        text_parts = [
            f"COURSE: {course_info.get('title', '')}",
            f"DESCRIPTION: {course_info.get('description', '')}",
            f"DEPARTMENT: {course_info.get('department', '')}"
        ]
        
        # Add concepts from LLM_Summary
        concepts_covered = llm_summary.get("concepts_covered", [])
        if concepts_covered:
            text_parts.append(f"CONCEPTS: {', '.join(concepts_covered)}")
            
        # Add summary from LLM_Summary
        summary = llm_summary.get("summary", "")
        if summary:
            text_parts.append(f"SUMMARY: {summary}")
            
        # Add weekly content
        weeks = course_data.get("weeks", [])
        week_texts = []
        for week in weeks:
            week_text = f"Week {week.get('order')}: {week.get('title')}"
            week_texts.append(week_text)
        
        if week_texts:
            text_parts.append("WEEKLY CONTENT: " + " | ".join(week_texts))
            
        return "\n".join(text_parts)
    
    def _extract_concepts(self, course_data: Dict[str, Any]) -> List[str]:
        """Extract concepts from course data"""
        course_info = course_data.get("course", {})
        llm_summary = course_info.get("LLM_Summary", {})
        
        # Get concepts from LLM_Summary
        concepts = set(llm_summary.get("concepts_covered", []))
        
        # Add concepts from lectures if available
        for lecture in course_data.get("lectures", []):
            lecture_summary = lecture.get("LLM_Summary", {})
            concepts.update(lecture_summary.get("concepts_covered", []))
                
        return list(concepts)
    
    def _process_search_results(
        self, 
        results: Any, 
        start_time: float
    ) -> Tuple[int, List[CourseMatchResult], float]:
        """Process search results into CourseMatchResult objects"""
        course_results = []
        
        for doc, metadata, distance in zip(results.documents, results.metadatas, results.distances):
            # Convert distance to similarity score
            similarity = max(0.0, min(1.0, 1.0 - 0.5 * distance))
            
            # Extract concepts and clean them up
            concepts = []
            if metadata.get("concepts_covered"):
                # Split by comma and clean each topic
                raw_concepts = metadata.get("concepts_covered", "").split(",")
                concepts = [concept.strip() for concept in raw_concepts if concept.strip()]
            
            # Create result object
            course_result = CourseMatchResult(
                course_id=int(metadata.get("course_id", "0")),
                code=metadata.get("code", ""),
                title=metadata.get("title", ""),
                description=metadata.get("description", ""),
                department=metadata.get("department", ""),
                credits=int(metadata.get("credits", "0")),
                score=similarity,
                matched_topics=concepts,
                weeks=[]  # We can add relevant weeks later if needed
            )
            course_results.append(course_result)
        
        query_time_ms = (time.time() - start_time) * 1000
        return len(course_results), course_results, query_time_ms

    async def list_all_courses(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        List all courses in the database with complete information.
        
        This method returns all indexed courses, useful for exploration and verification
        of data integrity.
        
        Args:
            limit: Maximum number of courses to return
            offset: Number of courses to skip
            
        Returns:
            List of course metadata dictionaries
        """
        if not self._initialized:
            self.initialize_sync()
            
        try:
            # Get all documents from the collection (with pagination)
            result = self.chroma.get_collection_docs_sync(
                collection_name=self.collection_name,
                limit=limit,
                offset=offset
            )
            
            if not result or not result.ids:
                return []
                
            # Format the results
            courses = []
            for i, course_id in enumerate(result.ids):
                metadata = result.metadatas[i]
                # Convert fields to proper types
                if "credits" in metadata:
                    metadata["credits"] = int(metadata["credits"])
                    
                # Add the document text (which contains the course description)
                if result.documents and len(result.documents) > i:
                    metadata["full_text"] = result.documents[i]
                    
                courses.append(metadata)
                
            return courses
        except Exception as e:
            logger.error(f"Error listing courses: {str(e)}")
            return [] 