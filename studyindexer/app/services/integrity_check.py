"""
IntegrityCheck service for StudyIndexerNew

This service handles integrity checking for student submissions against graded assignments.
It uses vector embeddings to identify potential matches between student submissions and 
existing graded assignments to help detect potential academic integrity violations.

Core Functionality:
- Indexing graded assignment questions for comparison
- Checking student submissions against indexed assignments
- Identifying potential matches with similarity scores
- Supporting integrity checking workflows
"""
import logging
import json
import time
from typing import List, Dict, Any, Optional, Tuple, Union
from datetime import datetime

from ..models.integrity_check import (
    GradedAssignmentInfo,
    GradedAssignmentQuestion,
    IntegrityCheckQuery,
    AssignmentMatch,
    HighestMatch,
    IntegrityCheckResponse,
    MatchSegment
)
from .chroma import ChromaService
from .embeddings import EmbeddingService, TextChunker

logger = logging.getLogger(__name__)

class IntegrityCheckService:
    """Service for checking submissions against graded assignments"""
    
    _instance = None
    
    def __new__(cls):
        """Singleton pattern to ensure only one instance is created"""
        if cls._instance is None:
            cls._instance = super(IntegrityCheckService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the IntegrityCheck service"""
        if getattr(self, '_initialized', False):
            return
            
        # Initialize dependencies
        self.chroma = ChromaService()
        self.embedder = EmbeddingService()
        self.chunker = TextChunker(chunk_size=500, chunk_overlap=100)
        
        # Set collection name for graded assignments
        self.collection_name = "graded-assignments"
        
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
                metadata={"description": "Graded assignments for integrity checking"}
            )
            
            self._initialized = True
            return True
        except Exception as e:
            logger.error(f"Failed to initialize IntegrityCheck service: {str(e)}")
            return False
    
    async def initialize(self) -> bool:
        """Async version of initialize for API use"""
        return self.initialize_sync()
    
    def index_assignment_sync(self, assignment_data: Dict[str, Any]) -> str:
        """
        Index a graded assignment for integrity checking
        
        Args:
            assignment_data: Dictionary containing assignment information with the following structure:
                - assignment_id: Unique identifier for the assignment
                - course_id: Course ID this assignment belongs to
                - title: Assignment title
                - description: Assignment description
                - questions: List of questions in the assignment
                
        Returns:
            The assignment_id as a string
        """
        if not self._initialized:
            self.initialize_sync()
            
        # Extract assignment info
        assignment_id = str(assignment_data.get("assignment_id"))
        if not assignment_id:
            raise ValueError("Assignment ID is required")
            
        course_id = str(assignment_data.get("course_id", ""))
        course_code = assignment_data.get("course_code", "")
        title = assignment_data.get("title", "")
        description = assignment_data.get("description", "")
        
        # Get questions
        questions = assignment_data.get("questions", [])
        if not questions:
            raise ValueError("Assignment must have at least one question")
            
        # Process each question
        for question_index, question in enumerate(questions):
            question_id = str(question.get("question_id"))
            if not question_id:
                # Generate a question ID if not provided
                question_id = f"{assignment_id}_q{question_index+1}"
                
            # Create document ID combining assignment and question
            document_id = f"{assignment_id}_{question_id}"
            
            # Get question content
            question_title = question.get("title", "")
            question_content = question.get("content", "")
            question_type = question.get("type", "")
            
            # For multiple choice, include options
            options_text = ""
            if question_type == "multiple_choice" and "options" in question:
                options = question.get("options", [])
                options_text = "\n".join([f"Option {i+1}: {opt.get('text', '')}" 
                                         for i, opt in enumerate(options)])
            
            # Combine all text for this question
            combined_text = f"QUESTION: {question_title}\n{question_content}\n{options_text}"
            
            # Generate embedding
            embedding = self.embedder.generate_embedding(combined_text)
            
            # Prepare metadata
            metadata = {
                "assignment_id": assignment_id,
                "question_id": question_id,
                "course_id": course_id,
                "course_code": course_code,
                "title": title[:100] if title else "",  # Truncate for metadata limits
                "question_title": question_title[:100] if question_title else "",
                "question_type": question_type,
                "indexed_at": datetime.utcnow().isoformat(),
            }
            
            # Store in ChromaDB
            self.chroma.add_documents_sync(
                collection_name=self.collection_name,
                documents=[combined_text],
                metadatas=[metadata],
                ids=[document_id],
                embeddings=[embedding]
            )
            
        logger.info(f"Indexed assignment {title} (ID: {assignment_id}) with {len(questions)} questions")
        return assignment_id
    
    async def index_assignment(self, assignment_data: Dict[str, Any]) -> str:
        """Async wrapper for index_assignment_sync"""
        return self.index_assignment_sync(assignment_data)
        
    def check_integrity_sync(self, query: IntegrityCheckQuery) -> IntegrityCheckResponse:
        """
        Check a submission against indexed graded assignments
        
        Args:
            query: IntegrityCheckQuery with submission text and optional filters
                
        Returns:
            IntegrityCheckResponse with potential matches
        """
        if not self._initialized:
            self.initialize_sync()
            
        # Start timing the query
        start_time = time.time()
            
        # Get submission text
        submission_text = query.query
        if not submission_text or not isinstance(submission_text, str) or len(submission_text.strip()) == 0:
            return IntegrityCheckResponse(
                success=True,
                query=query.query,
                total_results=0,
                query_time_ms=0,
                potential_violation=False,
                highest_match=None,
                matches=[]
            )
            
        # Use the submission text directly without chunking for simplicity
        chunks = [submission_text]
        
        # Generate embeddings for each chunk
        embeddings = [self.embedder.generate_embedding(chunk) for chunk in chunks]
        
        # Prepare search filters
        where_filter = None
        if query.course_ids and len(query.course_ids) > 0:
            # Convert course IDs to strings
            course_id_strings = [str(cid) for cid in query.course_ids]
            
            # If only one course ID, use simple filter
            if len(course_id_strings) == 1:
                where_filter = {"course_id": course_id_strings[0]}
            # If multiple course IDs, use $or operator
            elif len(course_id_strings) > 1:
                where_filter = {"$or": [{"course_id": cid} for cid in course_id_strings]}
        
        # Search for matches for each chunk
        all_matches = []
        highest_similarity = 0.0
        highest_match = None
        
        for chunk_idx, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            # Search for similar questions
            result = self.chroma.search_sync(
                collection_name=self.collection_name,
                query="",  # Empty as we're using embeddings directly
                n_results=5,  # Get top 5 matches
                where=where_filter,
                query_embedding=embedding
            )
            
            # Process results
            for doc_idx, (doc_id, distance, metadata, document) in enumerate(zip(
                result.ids, result.distances, result.metadatas, result.documents
            )):
                # Convert distance to similarity score (1 - distance)
                similarity = 1.0 - min(distance, 1.0)
                
                # Skip low similarity matches
                if similarity < 0.7:  # 70% threshold
                    continue
                    
                # Create match segments
                match_segment = MatchSegment(
                    query_segment=chunk,
                    matched_segment=document,
                    similarity=similarity
                )
                
                # Parse assignment ID from document ID
                assignment_id = metadata.get("assignment_id", "")
                question_id = metadata.get("question_id", "")
                
                # Find if we already have this assignment in our matches
                existing_match = next(
                    (m for m in all_matches if m.assignment_id == assignment_id), 
                    None
                )
                
                if existing_match:
                    # Update existing match if this has higher similarity
                    if similarity > existing_match.highest_similarity:
                        existing_match.highest_similarity = similarity
                    
                    # Add this segment to existing match
                    existing_match.segments.append(match_segment)
                    
                    # Sort segments by similarity
                    existing_match.segments.sort(key=lambda s: s.similarity, reverse=True)
                else:
                    # Create new match
                    match = AssignmentMatch(
                        assignment_id=assignment_id,
                        title=metadata.get("title", ""),
                        course_id=metadata.get("course_id", ""),
                        highest_similarity=similarity,
                        matched_questions=[question_id],
                        segments=[match_segment]
                    )
                    all_matches.append(match)
                
                # Update highest match
                if similarity > highest_similarity:
                    highest_similarity = similarity
                    highest_match = HighestMatch(
                        assignment_id=assignment_id,
                        question_id=question_id,
                        title=metadata.get("title", ""),
                        question_title=metadata.get("question_title", ""),
                        similarity=similarity
                    )
        
        # Calculate query time
        query_time_ms = (time.time() - start_time) * 1000
        
        # Sort matches by highest similarity
        all_matches.sort(key=lambda m: m.highest_similarity, reverse=True)
        
        # Determine if there's a potential violation (similarity > 80%)
        potential_violation = highest_similarity > 0.8
        
        # Create response
        response = IntegrityCheckResponse(
            success=True,
            query=query.query,
            total_results=len(all_matches),
            query_time_ms=query_time_ms,
            potential_violation=potential_violation,
            highest_match=highest_match,
            matches=all_matches
        )
        
        return response
    
    async def check_integrity(self, query: IntegrityCheckQuery) -> IntegrityCheckResponse:
        """Async wrapper for check_integrity_sync"""
        return self.check_integrity_sync(query)
    
    def get_assignment_sync(self, assignment_id: str) -> Optional[Dict[str, Any]]:
        """
        Get assignment details by ID
        
        Args:
            assignment_id: The ID of the assignment to retrieve
                
        Returns:
            Dictionary with assignment details or None if not found
        """
        if not self._initialized:
            self.initialize_sync()
            
        # Search for questions with this assignment ID
        result = self.chroma.search_sync(
            collection_name=self.collection_name,
            query="",  # Empty query to match all
            n_results=100,  # Get all questions for this assignment
            where={"assignment_id": str(assignment_id)}
        )
        
        if not result or not result.ids:
            return None
            
        # Group by question ID to build the assignment structure
        questions = {}
        assignment_info = {}
        
        for doc_idx, (doc_id, metadata, document) in enumerate(zip(
            result.ids, result.metadatas, result.documents
        )):
            question_id = metadata.get("question_id", "")
            
            # Store assignment info from first result
            if not assignment_info:
                assignment_info = {
                    "assignment_id": metadata.get("assignment_id", ""),
                    "course_id": metadata.get("course_id", ""),
                    "course_code": metadata.get("course_code", ""),
                    "title": metadata.get("title", ""),
                }
                
            # Store question info
            if question_id not in questions:
                questions[question_id] = {
                    "question_id": question_id,
                    "title": metadata.get("question_title", ""),
                    "content": document,
                    "type": metadata.get("question_type", "")
                }
                
        # Build complete assignment
        assignment = {
            **assignment_info,
            "questions": list(questions.values())
        }
        
        return assignment
    
    async def get_assignment(self, assignment_id: str) -> Optional[Dict[str, Any]]:
        """Async wrapper for get_assignment_sync"""
        return self.get_assignment_sync(assignment_id)
    
    def get_all_assignments_sync(self) -> List[Dict[str, Any]]:
        """
        Get a list of all indexed assignments
        
        Returns:
            List of assignment metadata dictionaries
        """
        if not self._initialized:
            self.initialize_sync()
            
        try:
            # Query all documents using search_sync instead of get_collection_sync
            query_result = self.chroma.search_sync(
                collection_name=self.collection_name,
                query="",  # Empty query to match all documents
                n_results=1000,  # Get up to 1000 documents
                where={}  # No filters
            )
            
            if not query_result or not query_result.ids:
                return []
                
            # Group by assignment ID to get unique assignments
            assignments = {}
            
            for doc_id, metadata in zip(query_result.ids, query_result.metadatas):
                assignment_id = metadata.get("assignment_id")
                if not assignment_id or assignment_id in assignments:
                    continue
                    
                # Create assignment entry
                assignments[assignment_id] = {
                    "assignment_id": assignment_id,
                    "title": metadata.get("title", ""),
                    "course_id": metadata.get("course_id", ""),
                    "course_code": metadata.get("course_code", ""),
                    "indexed_at": metadata.get("indexed_at", ""),
                    "question_count": 0  # Will count questions below
                }
            
            # Count questions for each assignment
            for metadata in query_result.metadatas:
                assignment_id = metadata.get("assignment_id")
                if assignment_id and assignment_id in assignments:
                    assignments[assignment_id]["question_count"] += 1
            
            return list(assignments.values())
            
        except Exception as e:
            logger.error(f"Failed to get all assignments: {str(e)}")
            return []
    
    async def get_all_assignments(self) -> List[Dict[str, Any]]:
        """Async wrapper for get_all_assignments_sync"""
        return self.get_all_assignments_sync()
    
    def search_graded_assignments_sync(
        self, 
        search_query: Optional[str] = None, 
        course_ids: Optional[List[int]] = None,
        limit: int = 50,
        threshold: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Search for graded assignments with optional filters
        
        Args:
            search_query: Optional text to search for in assignment titles/content
            course_ids: Optional list of course IDs to filter by
            limit: Maximum number of results to return
            threshold: Minimum similarity threshold (default 0.5)
            
        Returns:
            List of matching assignment metadata dictionaries with question-level matches
        """
        if not self._initialized:
            self.initialize_sync()
            
        # If no query provided, return empty results
        if not search_query or search_query.strip() == "":
            return []
            
        try:
            # Clean and preprocess the query text
            search_query = search_query.strip()
            
            # Validate threshold
            threshold = min(max(0.0, threshold), 1.0)
            
            # Prepare search parameters
            where_filter = {}
            if course_ids and len(course_ids) > 0:
                # Convert course IDs to strings
                course_id_strings = [str(cid) for cid in course_ids]
                if len(course_id_strings) == 1:
                    where_filter["course_id"] = course_id_strings[0]
                elif len(course_id_strings) > 1:
                    where_filter["$or"] = [{"course_id": cid} for cid in course_id_strings]
            
            # Use semantic search with higher result count for better matching
            query_result = self.chroma.search_sync(
                collection_name=self.collection_name,
                query=search_query,
                n_results=1000,  # Get more results to process and filter
                where=where_filter
            )
            
            if not query_result or not query_result.ids:
                return []
            
            # Process results with question-level matching
            matches = []
            processed_assignments = set()
            
            # Group results by assignment ID
            assignment_matches = {}
            
            # Calculate similarity scores and organize by assignment
            for idx, (doc_id, distance, metadata, document) in enumerate(zip(
                query_result.ids, query_result.distances, query_result.metadatas, query_result.documents
            )):
                # Extract assignment and question info
                assignment_id = metadata.get("assignment_id")
                if not assignment_id:
                    continue
                    
                # Calculate similarity (higher is better)
                similarity = 1.0 - min(distance, 1.0)
                
                # Filter out low similarity matches
                if similarity < threshold:  # Changed from hardcoded 0.5 to threshold parameter
                    continue
                
                # Get or create assignment entry
                if assignment_id not in assignment_matches:
                    assignment_matches[assignment_id] = {
                        "assignment_id": assignment_id,
                        "title": metadata.get("title", ""),
                        "course_id": metadata.get("course_id", ""),
                        "course_code": metadata.get("course_code", ""),
                        "highest_similarity": 0.0,
                        "matched_questions": [],
                        "question_count": 0
                    }
                
                # Update assignment metadata
                assignment_entry = assignment_matches[assignment_id]
                assignment_entry["question_count"] += 1
                
                # Add question match if not already added
                question_id = metadata.get("question_id")
                if question_id and question_id not in [q.get("question_id") for q in assignment_entry["matched_questions"]]:
                    # Get question title/content
                    question_title = metadata.get("question_title", "")
                    
                    # Create question entry
                    question_match = {
                        "question_id": question_id,
                        "title": question_title,
                        "content": document,
                        "similarity": similarity
                    }
                    
                    # Add to matched questions
                    assignment_entry["matched_questions"].append(question_match)
                    
                    # Update highest similarity
                    if similarity > assignment_entry["highest_similarity"]:
                        assignment_entry["highest_similarity"] = similarity
            
            # Convert to list and sort by highest similarity
            result_list = list(assignment_matches.values())
            result_list.sort(key=lambda x: x["highest_similarity"], reverse=True)
            
            # Sort questions within each assignment by similarity
            for assignment in result_list:
                assignment["matched_questions"].sort(key=lambda x: x["similarity"], reverse=True)
            
            # Apply overall limit
            return result_list[:limit]
            
        except Exception as e:
            logger.error(f"Failed to search graded assignments: {str(e)}")
            return []
    
    async def search_graded_assignments(
        self, 
        search_query: Optional[str] = None, 
        course_ids: Optional[List[int]] = None,
        limit: int = 50,
        threshold: float = 0.5
    ) -> List[Dict[str, Any]]:
        """Async wrapper for search_graded_assignments_sync"""
        return self.search_graded_assignments_sync(search_query, course_ids, limit, threshold) 