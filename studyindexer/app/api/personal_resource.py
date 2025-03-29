"""
PersonalResource API endpoints for StudyIndexerNew

This API provides endpoints for managing and searching student-specific resources
such as notes, files, and URLs that are relevant to their courses.

Core Purpose:
------------
The primary function of this API is to serve as a retrieval system for StudyAI,
providing personal resources to enhance the learning experience with personalized content.

Key Endpoints:
- GET /search: The primary search endpoint that returns resources matching a query
- GET /{resource_id}: Get a specific personal resource with its files
- GET /: List resources for a student, optionally filtered by course
- POST /: Add a new personal resource
- PUT /{resource_id}: Update an existing personal resource
- DELETE /{resource_id}: Delete a personal resource
- POST /sync: Synchronize resources from StudyHub (used by initialization scripts)

The search endpoint is the most important for the RAG system, as it delivers
the personal resources that StudyAI uses to enhance responses with personalized content.
"""
from fastapi import APIRouter, HTTPException, Depends, status, Query, UploadFile, File
from typing import List, Dict, Any, Optional, Union
import os
import time
import json
import glob

from ..models.personal_resource import (
    PersonalResource,
    PersonalResourceInfo,
    ResourceFile,
    PersonalResourceSearchQuery,
    PersonalResourceSearchResponse,
    PersonalResourceSearchResult
)
from ..models.base import BaseResponse
from ..services.personal_resource import PersonalResourceService

# Check if in development mode
IS_DEV_MODE = os.environ.get('ENVIRONMENT', 'development').lower() == 'development'

router = APIRouter()
personal_resource_service = PersonalResourceService()

# Initialize PersonalResource service
@router.on_event("startup")
async def startup_db_client():
    await personal_resource_service.initialize()

@router.get("/search", response_model=PersonalResourceSearchResponse)
async def search_resources(
    query: str,
    student_id: int,
    personal_resource_ids: Optional[List[str]] = Query(None),
    limit: int = 10
):
    """
    Search personal resources for a given student
    
    Parameters:
    - query: The search query text
    - student_id: ID of the student whose resources to search
    - personal_resource_ids: Optional list of resource IDs to filter by
    - limit: Maximum number of results to return
    
    Returns:
    - Matching personal resources with relevance scores
    """
    try:
        total_results, results, query_time_ms = await personal_resource_service.search_resources(
            query=query,
            student_id=student_id,
            resource_ids=personal_resource_ids,
            limit=limit
        )
        return PersonalResourceSearchResponse(
            success=True,
            resources=results,
            query=query,
            total_results=total_results,
            query_time_ms=query_time_ms
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching resources: {str(e)}"
        )

@router.get("", response_model=BaseResponse)
async def list_resources(
    student_id: int = Query(..., description="Student ID to list resources for"),
    course_id: Optional[int] = Query(None, description="Optional course ID to filter resources"),
    limit: int = Query(100, description="Maximum number of results to return"),
    offset: int = Query(0, description="Number of results to skip")
):
    """List personal resources for a student, optionally filtered by course"""
    try:
        resources = await personal_resource_service.list_resources(
            student_id=student_id,
            course_id=course_id,
            limit=limit,
            offset=offset
        )
        
        return BaseResponse(
            success=True,
            data={
                "resources": resources,
                "total": len(resources),
                "limit": limit,
                "offset": offset
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing personal resources: {str(e)}"
        )

@router.get("/{resource_id}", response_model=BaseResponse)
async def get_resource(resource_id: int):
    """Get a specific personal resource with its files"""
    try:
        result = await personal_resource_service.get_resource(resource_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Personal resource with ID {resource_id} not found"
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
            detail=f"Error retrieving personal resource: {str(e)}"
        )

@router.post("", response_model=BaseResponse)
async def add_resource(resource_data: Dict[str, Any]):
    """Add a new personal resource"""
    try:
        resource_id = await personal_resource_service.add_resource(resource_data)
        
        return BaseResponse(
            success=True,
            message="Personal resource added successfully",
            data={
                "resource_id": resource_id
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error adding personal resource: {str(e)}"
        )

@router.put("/{resource_id}", response_model=BaseResponse)
async def update_resource(resource_id: int, resource_data: Dict[str, Any]):
    """Update an existing personal resource"""
    try:
        success = await personal_resource_service.update_resource(resource_id, resource_data)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Personal resource with ID {resource_id} not found or could not be updated"
            )
            
        return BaseResponse(
            success=True,
            message="Personal resource updated successfully",
            data={
                "resource_id": resource_id
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating personal resource: {str(e)}"
        )

@router.delete("/{resource_id}", response_model=BaseResponse)
async def delete_resource(resource_id: int):
    """Delete a personal resource"""
    try:
        success = await personal_resource_service.delete_resource(resource_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Personal resource with ID {resource_id} not found or could not be deleted"
            )
            
        return BaseResponse(
            success=True,
            message="Personal resource deleted successfully",
            data={
                "resource_id": resource_id
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting personal resource: {str(e)}"
        )

@router.post("/sync", response_model=BaseResponse)
async def sync_resources(sync_data: Dict[str, Any]):
    """
    Synchronize resources from StudyHub
    
    This endpoint is used by initialization scripts to sync resources from StudyHub
    to StudyIndexer. It accepts a list of resources to add, update, or delete.
    
    Expected format:
    {
        "resources": [
            {
                "resource": {...},  # PersonalResourceInfo data
                "files": [...]      # List of ResourceFile data
            },
            ...
        ]
    }
    """
    try:
        resources = sync_data.get("resources", [])
        
        results = {
            "added": 0,
            "failed": 0,
            "resource_ids": []
        }
        
        for resource_data in resources:
            try:
                resource_id = await personal_resource_service.add_resource(resource_data)
                results["added"] += 1
                results["resource_ids"].append(resource_id)
            except Exception as e:
                results["failed"] += 1
                # Log the error but continue processing other resources
                # This ensures that one bad resource doesn't block the entire sync
                logger.error(f"Error syncing resource: {str(e)}")
        
        return BaseResponse(
            success=True,
            message=f"Synced {results['added']} resources ({results['failed']} failed)",
            data=results
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error syncing resources: {str(e)}"
        )

# Development-only endpoints
if IS_DEV_MODE:
    @router.delete("/cleanup", response_model=BaseResponse, tags=["Development"])
    async def cleanup_resources(
        student_id: Optional[int] = Query(None, description="Delete resources for specific student"),
        delete_all: bool = Query(False, description="Set to true to delete all resources")
    ):
        """Delete resources for testing/cleanup (DEVELOPMENT ONLY)"""
        try:
            if not delete_all and student_id is None:
                return BaseResponse(
                    success=False,
                    message="Must specify either student_id or delete_all=true"
                )
                
            # This is a development endpoint, so we don't have a bulk delete
            # We would need to implement it for this endpoint
            return BaseResponse(
                success=False,
                message="Not implemented yet"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error cleaning up resources: {str(e)}"
            ) 