"""
IntegrityCheck API endpoints for StudyIndexerNew

This API provides endpoints for integrity checking of student submissions against
graded assignments to identify potential academic integrity violations.

Core Purpose:
------------
The primary function of this API is to serve as an integrity checking system,
identifying potential matches between student submissions and graded assignments.

Key Endpoints:
- POST /check: The primary endpoint that checks a submission against indexed assignments
- POST /index: Index a new graded assignment for future integrity checks
- GET /assignment/{assignment_id}: Get a specific graded assignment details
"""
from fastapi import APIRouter, HTTPException, Depends, status, Query, UploadFile, File
from typing import List, Dict, Any, Optional, Union
import os
import time
import json

from ..models.integrity_check import (
    IntegrityCheckQuery,
    IntegrityCheckResponse,
    AssignmentMatch,
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

@router.post("/check", response_model=IntegrityCheckResponse)
async def check_integrity(query: IntegrityCheckQuery):
    """
    Check a submission against indexed graded assignments
    
    This is the primary integrity checking endpoint. It returns potential matches
    between the submission text and indexed graded assignments, with similarity scores.
    
    Request body:
    - query: The text to check against graded assignments (required)
    - course_ids: Optional list of course IDs to limit the check [e.g., [101, 102]]
    - threshold: Similarity threshold (default: 0.8)
    
    Returns:
    - matches: List of matching assignments with similarity scores
    - highest_match: Details of the highest matching assignment
    - potential_violation: Whether any match exceeded the threshold
    """
    try:
        # Ensure query is a valid string
        if not isinstance(query.query, str):
            raise ValueError("Query must be a string")
            
        # Call the service
        result = await integrity_check_service.check_integrity(query)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error checking integrity: {str(e)}"
        )

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
    """Get details of a graded assignment by ID"""
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