"""
IntegrityCheck API endpoints for StudyIndexerNew

This API provides endpoints for integrity checking of student submissions against
graded assignments to identify potential academic integrity violations.

Core Purpose:
------------
The primary function of this API is to serve as an integrity checking system,
identifying potential matches between student submissions and graded assignments.

Key Endpoints:
- GET /assignments: List all indexed assignments
- GET /assignment/{assignment_id}: Get a specific graded assignment details
- GET /search-assignments: Search for assignments with a text query
- POST /index: Index a new graded assignment for future integrity checks
- POST /bulk-index: Index multiple assignments in a single request
"""
from fastapi import APIRouter, HTTPException, Depends, status, Query, UploadFile, File
from typing import List, Dict, Any, Optional, Union
import os
import time
import json

from ..models.integrity_check import (
    IntegrityCheckResponse,
    GradedAssignmentInfo
)
from ..models.base import BaseResponse
from ..services.integrity_check import IntegrityCheckService

# Check if in development mode
IS_DEV_MODE = os.environ.get('ENVIRONMENT', 'development').lower() == 'development'

router = APIRouter()
integrity_check_service = IntegrityCheckService()

# Initialize IntegrityCheck service
@router.on_event("startup")
async def startup_db_client():
    await integrity_check_service.initialize()

@router.post("/index", response_model=BaseResponse)
async def index_assignment(assignment_data: Dict[str, Any]):
    """Index a new graded assignment for integrity checking"""
    try:
        assignment_id = await integrity_check_service.index_assignment(assignment_data)
        
        return BaseResponse(
            success=True,
            message=f"Assignment indexed successfully with ID: {assignment_id}",
            data={
                "assignment_id": assignment_id
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error indexing assignment: {str(e)}"
        )

@router.get("/assignment/{assignment_id}", response_model=BaseResponse)
async def get_assignment(assignment_id: str):
    """
    Get details of a graded assignment by ID
    
    This endpoint retrieves a specific assignment by its ID, including all its questions.
    
    Path Parameters:
    - assignment_id: The unique identifier of the assignment
    
    Returns:
    - Assignment details including questions
    """
    try:
        result = await integrity_check_service.get_assignment(assignment_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Assignment with ID {assignment_id} not found"
            )
            
        return BaseResponse(
            success=True,
            data=result
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving assignment: {str(e)}"
        )

@router.post("/bulk-index", response_model=BaseResponse)
async def bulk_index_assignments(assignments: List[Dict[str, Any]]):
    """Index multiple assignments in a single request"""
    results = {
        "success": True,
        "total_indexed": 0,
        "failed": [],
        "indexed": []
    }
    
    for assignment_data in assignments:
        try:
            assignment_id = await integrity_check_service.index_assignment(assignment_data)
            results["indexed"].append({
                "assignment_id": assignment_id,
                "title": assignment_data.get("title", "")
            })
            results["total_indexed"] += 1
        except Exception as e:
            results["failed"].append({
                "title": assignment_data.get("title", ""),
                "error": str(e)
            })
    
    if results["failed"]:
        results["success"] = False
    
    return BaseResponse(
        success=True,
        data=results
    )

@router.get("/assignments", response_model=BaseResponse)
async def list_assignments():
    """
    List all indexed assignments
    
    This endpoint returns a list of all assignments that have been indexed for integrity checking.
    It provides basic metadata about each assignment, including title, course, and number of questions.
    
    Returns:
    - assignments: List of assignment metadata
    """
    try:
        assignments = await integrity_check_service.get_all_assignments()
        
        return BaseResponse(
            success=True,
            message=f"Retrieved {len(assignments)} assignments",
            data={
                "assignments": assignments,
                "total": len(assignments)
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving assignments: {str(e)}"
        )

@router.get("/search-assignments", response_model=BaseResponse)
async def search_graded_assignments(
    query: Optional[str] = None,
    threshold: float = 0.5  # Changed default from 0.8 to 0.5 to match service
):
    """
    Search for indexed graded assignments with text query only
    
    This endpoint is specifically designed for academic integrity checking, finding 
    assignments that closely match the provided text query. It returns detailed information
    about matching assignments including the specific questions that matched and their
    similarity scores.
    
    Query parameters:
    - query: Text to search for in the assignments
    - threshold: Optional similarity threshold (default: 0.5, range: 0-1)
      Will filter out results below this threshold
    
    Returns:
    - assignments: List of matching assignments with details
    - highest_match: The most similar assignment and question found
    - total: Total number of matching assignments
    - potential_violation: Boolean indicating if any match exceeds the violation threshold (0.8)
    """
    try:
        if not query or query.strip() == "":
            return BaseResponse(
                success=True,
                message="No query provided",
                data={
                    "assignments": [],
                    "highest_match": None,
                    "total": 0,
                    "potential_violation": False
                }
            )
            
        # Validate threshold
        search_threshold = min(max(0.0, threshold), 1.0)
        
        # Fixed threshold for determining potential violations (0.8)
        violation_threshold = 0.8
            
        # Call the service with search threshold
        assignments = await integrity_check_service.search_graded_assignments(
            search_query=query,
            course_ids=None,
            limit=100,  # Fixed limit
            threshold=search_threshold  # Pass threshold to service
        )
        
        # Create enhanced response with highest match information
        highest_match = None
        highest_similarity = 0.0
        
        # Deduplicate results by question content to avoid showing the same question multiple times
        unique_questions = {}
        unique_assignments = []
        
        for assignment in assignments:
            assignment_copy = dict(assignment)
            # Filter questions to unique ones only
            unique_matched_questions = []
            
            for question in assignment.get("matched_questions", []):
                question_content = question.get("content", "")
                if question_content and question_content not in unique_questions:
                    # Add to unique questions mapping
                    unique_questions[question_content] = question
                    unique_matched_questions.append(question)
                    
                    # Update highest match if needed
                    if question.get("similarity", 0) > highest_similarity:
                        highest_similarity = question.get("similarity", 0)
                        highest_match = {
                            "assignment_id": assignment["assignment_id"],
                            "assignment_title": assignment["title"],
                            "course_id": assignment["course_id"],
                            "course_code": assignment.get("course_code", ""),
                            "question_id": question["question_id"],
                            "question_title": question["title"],
                            "question_content": question["content"],
                            "similarity": question["similarity"]
                        }
            
            if unique_matched_questions:
                assignment_copy["matched_questions"] = unique_matched_questions
                assignment_copy["question_count"] = len(unique_matched_questions)
                unique_assignments.append(assignment_copy)
        
        # Determine potential violation status using fixed violation threshold
        potential_violation = highest_similarity >= violation_threshold
        
        return BaseResponse(
            success=True,
            message=f"Found {len(unique_assignments)} assignments with unique matching questions",
            data={
                "assignments": unique_assignments,
                "highest_match": highest_match,
                "total": len(unique_assignments),
                "potential_violation": potential_violation
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching assignments: {str(e)}"
        ) 