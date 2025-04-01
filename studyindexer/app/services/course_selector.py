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
        """
        if not self._initialized:
            self.initialize_sync()
            
        logger.info("Starting course indexing process...")
        course_info = course_data.get("course", {})
        
        # Get the course code - this is the main identifier between systems
        code = course_info.get("code")
        if not code:
            logger.error("Course code is required for indexing")
            raise ValueError("Course code is required for indexing")
            
        logger.info(f"Processing course with code: {code}")
        
        # Get or generate course_id (secondary identifier)
        course_id = course_info.get("course_id")
        if not course_id:
            # Generate a timestamp-based ID if none provided
            course_id = str(int(time.time()))
            logger.warning(f"No course_id provided for course {code}, generated default: {course_id}")
            course_info["course_id"] = course_id
            course_data["course"] = course_info
            
        # Convert course_id to string if it's not already
        course_id = str(course_id)
        logger.info(f"Using course_id: {course_id}")
            
        # Create combined text for embedding
        logger.info("Creating combined text for embedding...")
        combined_text = self._create_course_embedding_text(course_data)
        logger.info(f"Created combined text of length: {len(combined_text)}")
        
        # Generate embedding
        logger.info("Generating embedding...")
        embedding = self.embedder.generate_embedding(combined_text)
        logger.info("Embedding generated successfully")
        
        # Extract concepts with our improved method
        logger.info("Extracting concepts...")
        concepts = self._extract_concepts(course_data)
        logger.info(f"Extracted {len(concepts)} concepts for course {code}: {concepts}")
        
        # Check for required fields, use defaults for missing ones
        title = course_info.get("title", "Untitled Course")
        description = course_info.get("description", "")
        department = course_info.get("department", "General")
        credits = course_info.get("credits", 0)
        
        logger.info("Building metadata for ChromaDB...")
        # Ensure all values are safe for ChromaDB metadata
        safe_metadata = {}
        
        # Explicitly convert each field to its string representation and ensure no None values
        safe_metadata["code"] = str(code) if code is not None else ""
        safe_metadata["course_id"] = str(course_id) if course_id is not None else ""
        safe_metadata["title"] = str(title) if title is not None else "Untitled Course"
        
        # Truncate description if needed and ensure it's a string
        if description is not None:
            desc_str = str(description)
            safe_metadata["description"] = desc_str[:1000] if len(desc_str) > 1000 else desc_str
        else:
            safe_metadata["description"] = ""
            
        safe_metadata["department"] = str(department) if department is not None else "General"
        safe_metadata["credits"] = str(credits) if credits is not None else "0"
        
        # Handle concepts - this is critical for the matched_topics in search results
        if concepts:
            # Join concepts into a comma-separated string for ChromaDB metadata
            safe_metadata["concepts_covered"] = ",".join([str(c) for c in concepts if c is not None])
            logger.info(f"Concepts saved to metadata: {safe_metadata['concepts_covered']}")
        else:
            safe_metadata["concepts_covered"] = ""
            logger.warning(f"No concepts found for course {code}")
            
        # Add timestamp
        safe_metadata["added_on"] = datetime.utcnow().isoformat()
        
        # Verify no None values remain before adding to ChromaDB
        for key, value in safe_metadata.items():
            if value is None:
                safe_metadata[key] = ""  # Final safety check
                logger.warning(f"Found None value for {key} in course {code}, replacing with empty string")
        
        # Store in ChromaDB - use code as the document ID to ensure uniqueness
        try:
            # Check if course already exists
            logger.info(f"Checking if course {code} already exists...")
            existing = self.chroma.get_sync(
                collection_name=self.collection_name,
                ids=[code]
            )
            
            if existing and existing.ids:
                # Delete existing entry to update it
                logger.info(f"Course {code} already exists in ChromaDB, updating...")
                self.chroma.delete_sync(
                    collection_name=self.collection_name,
                    ids=[code]
                )
            
            # Add the new/updated document
            logger.info(f"Adding/updating course {code} in ChromaDB...")
            self.chroma.add_documents_sync(
                collection_name=self.collection_name,
                documents=[combined_text],
                metadatas=[safe_metadata],
                ids=[code],  # Use code as document ID instead of course_id
                embeddings=[embedding]
            )
            
            logger.info(f"Successfully indexed course {title} (Code: {code}) with {len(concepts)} concepts")
        except Exception as e:
            logger.error(f"Error in add_documents_sync: {str(e)}")
            logger.error(f"Metadata that caused the error: {safe_metadata}")
            raise
        
        return code
    
    async def index_course(self, course_data: Dict[str, Any]) -> str:
        """Async version of index_course for API use"""
        return self.index_course_sync(course_data)
    
    async def bulk_index_courses_from_files(self, file_paths: List[str]) -> Dict[str, Any]:
        """Index multiple courses from JSON files"""
        results = {
            "success": True,
            "total_indexed": 0,
            "failed": [],
            "indexed": [],
            "course_codes": []  # Using codes instead of IDs
        }
        
        for file_path in file_paths:
            try:
                with open(file_path, 'r') as f:
                    course_data = json.load(f)
                
                course_code = self.index_course_sync(course_data)
                results["indexed"].append({
                    "file": file_path,
                    "course_code": course_code
                })
                results["course_codes"].append(course_code)
                results["total_indexed"] += 1
            except Exception as e:
                results["failed"].append({
                    "file": file_path,
                    "error": str(e)
                })
                
        if results["failed"]:
            results["success"] = False
            
        return results
    
    async def get_course(self, course_code: str) -> Dict[str, Any]:
        """Get course details by code"""
        if not self._initialized:
            self.initialize_sync()
            
        # Using the get method to retrieve course by code
        result = self.chroma.get_sync(
            collection_name=self.collection_name,
            ids=[course_code]
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
        
        # Filter courses by subscribed_courses (using code instead of course_id)
        # Adjust logic to handle single or multiple course codes
        if len(search_query.subscribed_courses) > 1:
            where_clause = {
                "$or": [{"code": code} for code in search_query.subscribed_courses]
            }
        else:
            where_clause = {"code": search_query.subscribed_courses[0]}
        
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
            return self._process_search_results(results, start_time, search_text)
            
        # For semantic search, generate embedding
        query_embedding = self.embedder.generate_embedding(search_text)
        
        # Search collection with a higher n_results to allow more potential matches
        # We'll filter by min_score later
        results = self.chroma.search_sync(
            collection_name=self.collection_name,
            query="",
            query_embedding=query_embedding,
            n_results=max(50, search_query.limit * 2),  # Retrieve more results to allow for filtering
            where=where_clause
        )
        
        # Process results and get data
        total, course_results, query_time = self._process_search_results(results, start_time, search_text)
        
        # If we got no results and the query is relatively specific, try a fallback approach
        if not course_results and len(search_text.split()) > 1:
            # Try again with just the course codes without semantic search
            fallback_results = self.chroma.get_sync(
                collection_name=self.collection_name,
                ids=search_query.subscribed_courses
            )
            
            if fallback_results and fallback_results.ids:
                # Create dummy results for metadata
                fallback_processed = []
                for i, doc_id in enumerate(fallback_results.ids):
                    metadata = fallback_results.metadatas[i]
                    fallback_processed.append(CourseMatchResult(
                        code=metadata.get("code", ""),
                        title=metadata.get("title", ""),
                        description=metadata.get("description", ""),
                        score=0.2,  # Low but non-zero score for fallback results
                        matched_topics=[]
                    ))
                
                if fallback_processed:
                    course_results = fallback_processed
                    total = len(fallback_processed)
                    logger.info(f"Used fallback search for query: {search_text}")
        
        return total, course_results, query_time
    
    async def select_courses(self, search_query: CourseSelectorQuery) -> Tuple[int, List[CourseMatchResult], float]:
        """Async version of select_courses for API use"""
        # Direct call to sync version and return its result
        return self.select_courses_sync(search_query)
    
    def _create_course_embedding_text(self, course_data: Dict[str, Any]) -> str:
        """Create text for embedding from course data"""
        course_info = course_data.get("course", {})
        llm_summary = course_info.get("LLM_Summary", {})
        
        # CRITICAL FIX: Log LLM_Summary to debug concepts
        logger.info(f"LLM_Summary during embedding: {json.dumps(llm_summary)}")
        
        # Combine course information
        text_parts = [
            f"COURSE: {course_info.get('title', '')}",
            f"DESCRIPTION: {course_info.get('description', '')}"
        ]
        
        # Add department if available
        if course_info.get('department'):
            text_parts.append(f"DEPARTMENT: {course_info.get('department', '')}")
        
        # Add key concepts from LLM_Summary
        key_concepts = llm_summary.get("key_concepts", [])
        if key_concepts:
            text_parts.append(f"KEY CONCEPTS: {', '.join(key_concepts)}")
            
        # CRITICAL FIX: Explicitly add concepts_covered from LLM_Summary
        concepts_covered = llm_summary.get("concepts_covered", [])
        if concepts_covered:
            logger.info(f"Adding concepts_covered from LLM_Summary: {concepts_covered}")
            text_parts.append(f"CONCEPTS: {', '.join(concepts_covered)}")
            
        # Add summary from LLM_Summary
        summary = llm_summary.get("summary", "")
        if summary:
            text_parts.append(f"SUMMARY: {summary}")
            
        # Extract all concepts for better embedding
        all_concepts = self._extract_concepts(course_data)
        if all_concepts:
            text_parts.append(f"ALL CONCEPTS: {', '.join(all_concepts)}")
            
        # Add weekly content
        weeks = course_data.get("weeks", [])
        week_texts = []
        for week in weeks:
            week_summary = week.get("LLM_Summary", {})
            week_text = f"Week {week.get('week_number')}: {week.get('title')}"
            
            # Add week summary if available
            if week_summary.get("summary"):
                week_text += f" - {week_summary.get('summary')}"
                
            # Add week key concepts if available
            if week_summary.get("key_concepts"):
                week_text += f" (Topics: {', '.join(week_summary.get('key_concepts'))})"
                
            week_texts.append(week_text)
        
        if week_texts:
            text_parts.append("WEEKLY CONTENT: " + " | ".join(week_texts))
            
        # Add lecture content
        lectures = course_data.get("lectures", [])
        lecture_texts = []
        for lecture in lectures:
            lecture_text = f"{lecture.get('title')}"
            
            # Add summary if available
            lecture_summary = lecture.get("LLM_Summary", {})
            if lecture_summary.get("summary"):
                lecture_text += f" - {lecture_summary.get('summary')}"
                
            lecture_texts.append(lecture_text)
            
        if lecture_texts:
            text_parts.append("LECTURES: " + " | ".join(lecture_texts))
            
        return "\n".join(text_parts)
    
    def _extract_concepts(self, course_data: Dict[str, Any]) -> List[str]:
        """Extract concepts from course data"""
        concepts = set()
        
        # Extract concepts from course LLM_Summary (primary source)
        course_info = course_data.get("course", {})
        
        # IMPORTANT: LLM_Summary is the main source of concepts in sample.json
        llm_summary = course_info.get("LLM_Summary", {})
        
        # Get concepts_covered from LLM_Summary (primary location in sample.json)
        llm_concepts_covered = llm_summary.get("concepts_covered", [])
        if llm_concepts_covered:
            logger.info(f"Found concepts_covered in LLM_Summary: {llm_concepts_covered}")
            for concept in llm_concepts_covered:
                if concept:  # Skip empty concepts
                    concepts.add(concept)
        
        # Also get any key_concepts if present
        key_concepts = llm_summary.get("key_concepts", [])
        if key_concepts:
            for concept in key_concepts:
                if concept:
                    concepts.add(concept)
        
        # Check top-level topics if present
        if "topics" in course_data and isinstance(course_data["topics"], list):
            topics = course_data["topics"]
            for topic in topics:
                if isinstance(topic, dict) and "name" in topic:
                    concepts.add(topic["name"])
                elif isinstance(topic, str):
                    concepts.add(topic)
        
        # Also get any concepts_covered if present at top level
        concepts_covered = course_data.get("concepts_covered", [])
        if concepts_covered:
            for concept in concepts_covered:
                if concept:
                    concepts.add(concept)
        
        # Add concepts from weeks
        for week in course_data.get("weeks", []):
            week_summary = week.get("LLM_Summary", {})
            
            # Check for key_concepts first
            week_concepts = week_summary.get("key_concepts", [])
            if week_concepts:
                for concept in week_concepts:
                    if concept:
                        concepts.add(concept)
            
            # Also check for concepts_covered within week LLM_Summary
            week_concepts_covered = week_summary.get("concepts_covered", [])
            if week_concepts_covered:
                for concept in week_concepts_covered:
                    if concept:
                        concepts.add(concept)
            
            # Check for topics list in week
            week_topics = week.get("topics", [])
            if week_topics:
                for topic in week_topics:
                    if isinstance(topic, dict) and "name" in topic:
                        concepts.add(topic["name"])
                    elif isinstance(topic, str):
                        concepts.add(topic)
            
        # Add concepts from lectures
        for lecture in course_data.get("lectures", []):
            lecture_summary = lecture.get("LLM_Summary", {})
            
            # Check for key_concepts first
            lecture_concepts = lecture_summary.get("key_concepts", [])
            if lecture_concepts:
                for concept in lecture_concepts:
                    if concept:
                        concepts.add(concept)
            
            # Also check for concepts_covered within lecture LLM_Summary
            lecture_concepts_covered = lecture_summary.get("concepts_covered", [])
            if lecture_concepts_covered:
                for concept in lecture_concepts_covered:
                    if concept:
                        concepts.add(concept)
            
            # Check for keywords field in lectures
            keywords = lecture.get("keywords", [])
            if keywords:
                for keyword in keywords:
                    if keyword:
                        concepts.add(keyword)
        
        logger.info(f"Extracted {len(concepts)} unique concepts: {list(concepts)}")
        return list(concepts)
    
    def _process_search_results(
        self, 
        results: Any, 
        start_time: float,
        query: str = ""
    ) -> Tuple[int, List[CourseMatchResult], float]:
        """Process search results into CourseMatchResult objects"""
        course_results = []
        
        for doc, metadata, distance in zip(results.documents, results.metadatas, results.distances):
            # Convert distance to similarity score - use a less restrictive formula
            # Original: similarity = max(0.0, min(1.0, 1.0 - 0.5 * distance))
            # New: soften the penalty for distance
            similarity = max(0.0, min(1.0, 1.0 - 0.3 * distance))
            
            # Extract concepts and clean them up
            concepts = []
            if metadata.get("concepts_covered"):
                # Split by comma and clean each topic
                raw_concepts = metadata.get("concepts_covered", "").split(",")
                concepts = [concept.strip() for concept in raw_concepts if concept.strip()]
                
                # Log the extracted concepts for debugging
                logger.info(f"Extracted concepts from metadata: {concepts}")
                
                # Score concepts by matching with query terms
                if query and concepts:
                    query_terms = [term.lower() for term in query.split()]
                    
                    # Score concepts by matching with query terms, with partial matching
                    scored_concepts = []
                    for concept in concepts:
                        concept_lower = concept.lower()
                        score = 0
                        
                        # Check for exact term matches
                        for term in query_terms:
                            if term in concept_lower:
                                score += 2  # Give higher weight to exact matches
                        
                        # Check for partial matches (individual words)
                        concept_words = concept_lower.split()
                        for term in query_terms:
                            for word in concept_words:
                                if term in word or word in term:
                                    score += 0.5  # Give partial credit for partial matches
                        
                        # Keep track of all concepts with their scores
                        scored_concepts.append((concept, score))
                    
                    # Sort by score and include only concepts that matched
                    if scored_concepts:
                        scored_concepts.sort(key=lambda x: x[1], reverse=True)
                        # Only include concepts that have a positive score (some relevance)
                        matching_concepts = [c[0] for c in scored_concepts if c[1] > 0]
                        concepts = matching_concepts
                        
                        # Log the matching concepts
                        if matching_concepts:
                            logger.info(f"Found {len(matching_concepts)} matching concepts: {matching_concepts}")
                        else:
                            logger.info(f"No matching concepts found for query: {query}")
                            concepts = []  # No matches, return empty list
            
            # Create result object with required fields
            course_result = CourseMatchResult(
                code=metadata.get("code", ""),
                title=metadata.get("title", ""),
                description=metadata.get("description", ""),
                score=similarity,
                matched_topics=concepts  # Use our extracted and filtered concepts
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

    async def delete_course(self, course_code: str) -> bool:
        """Delete a course by code"""
        if not self._initialized:
            self.initialize_sync()
        
        try:
            # Attempt to delete the course by its code using the correct method
            self.chroma.delete_sync(
                collection_name=self.collection_name,
                ids=[course_code]
            )
            logger.info(f"Deleted course with code: {course_code}")
            return True
        except Exception as e:
            logger.error(f"Error deleting course with code {course_code}: {str(e)}")
            return False 