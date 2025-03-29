"""
CourseContent API endpoints for StudyIndexerNew

This API provides endpoints for managing and searching course content for RAG applications.

Core Purpose:
------------
The primary function of this API is to serve as a retrieval system for StudyAI,
providing content chunks that can be used for retrieval-augmented generation.

Key Endpoints:
- GET /search: The primary RAG retrieval endpoint that returns content chunks matching a query
- GET /{course_id}: Get full course content by ID
- GET /: List all available courses with basic information
- POST /: Add new course content 
- PUT /{course_id}: Update existing course content
- DELETE /{course_id}: Delete course content
- POST /import: Import course content from JSON files
- POST /import-sample: Import sample course content for testing (dev only)

The search endpoint is the most important for the RAG system, as it delivers
the content chunks that StudyAI uses to generate responses based on course materials.
"""
from fastapi import APIRouter, HTTPException, Depends, status, Query, UploadFile, File
from typing import List, Dict, Any, Optional, Union
import os
import time
import json
import glob

from ..models.course_selector import CourseContent, CourseInfo, CourseTopic, WeekOverview
from ..models.base import BaseResponse, BaseSearchQuery, BaseSearchResponse
from ..services.course_content import CourseContentService

# Check if in development mode
IS_DEV_MODE = os.environ.get('ENVIRONMENT', 'development').lower() == 'development'

router = APIRouter()
course_content_service = CourseContentService()

# Initialize CourseContent service
@router.on_event("startup")
async def startup_db_client():
    await course_content_service.initialize()

@router.post("", response_model=BaseResponse)
async def add_course_content(course_data: dict):
    """Add course content to the database"""
    try:
        # If the course data is not in the expected format, wrap it
        if "course" not in course_data:
            course_data = {"course": course_data}
        
        course_id = await course_content_service.add_course_content(course_data)
        
        return BaseResponse(
            success=True,
            message="Course content added successfully",
            data={
                "course_id": course_id
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error adding course content: {str(e)}"
        )

@router.get("", response_model=BaseResponse)
async def list_courses(
    limit: int = Query(100, description="Maximum number of results to return"),
    offset: int = Query(0, description="Number of results to skip")
):
    """List all courses with basic information"""
    try:
        results = await course_content_service.list_courses(limit=limit, offset=offset)
        
        return BaseResponse(
            success=True,
            data={
                "courses": results,
                "total_count": len(results),
                "limit": limit,
                "offset": offset
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing courses: {str(e)}"
        )

@router.get("/search", response_model=BaseResponse)
async def search_courses(
    query: str = Query("", description="Search query for content matching"),
    course_ids: Optional[List[str]] = Query(None, description="Optional list of course IDs to filter search results"),
    limit: int = Query(10, description="Maximum number of results to return")
):
    """
    Search for course content chunks matching the query
    
    This is the primary RAG retrieval endpoint used by StudyAI. It returns specific 
    content chunks (lectures, topics, week content) that match the query, enabling
    retrieval-augmented generation.
    
    The response includes:
    - Source course information (metadata)
    - Content chunks that match the query
    - Relevance scores for ranking
    
    This endpoint powers the core functionality of providing relevant course materials
    to StudyAI for generating responses based on course content.
    """
    try:
        results = await course_content_service.search_courses(
            query=query, 
            limit=limit,
            course_ids=course_ids
        )
        
        return BaseResponse(
            success=True,
            data={
                "content_chunks": results,
                "total_count": len(results),
                "query": query,
                "limit": limit
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching course content: {str(e)}"
        )

@router.get("/{course_id}", response_model=BaseResponse)
async def get_course_content(course_id: Union[int, str]):
    """Get course content by ID"""
    try:
        result = await course_content_service.get_course_content(course_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Course content with ID {course_id} not found"
            )
            
        return BaseResponse(
            success=True,
            data=result.dict()
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving course content: {str(e)}"
        )

@router.put("/{course_id}", response_model=BaseResponse)
async def update_course_content(course_id: Union[int, str], course: CourseContent):
    """Update course content by ID"""
    try:
        success = await course_content_service.update_course_content(course_id, course)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Course content with ID {course_id} not found or could not be updated"
            )
            
        return BaseResponse(
            success=True,
            message="Course content updated successfully",
            data={
                "course_id": str(course_id)
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating course content: {str(e)}"
        )

@router.delete("/{course_id}", response_model=BaseResponse)
async def delete_course_content(course_id: Union[int, str]):
    """Delete course content by ID"""
    try:
        success = await course_content_service.delete_course_content(course_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Course content with ID {course_id} not found or could not be deleted"
            )
            
        return BaseResponse(
            success=True,
            message="Course content deleted successfully",
            data={
                "course_id": str(course_id)
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting course content: {str(e)}"
        )

@router.post("/import", response_model=BaseResponse)
async def import_course_files(
    files: List[UploadFile] = File(..., description="Course content JSON files")
):
    """Import course content from JSON files"""
    try:
        # Create temp directory if it doesn't exist
        temp_dir = os.path.join(os.getcwd(), "temp")
        os.makedirs(temp_dir, exist_ok=True)
        
        results = {
            "success": True,
            "total_imported": 0,
            "failed_items": [],
            "course_ids": []
        }
        
        for file in files:
            try:
                # Save the file temporarily
                file_path = os.path.join(temp_dir, file.filename)
                with open(file_path, "wb") as f:
                    content = await file.read()
                    f.write(content)
                
                # Load the JSON
                with open(file_path, 'r', encoding='utf-8') as f:
                    course_data = json.load(f)
                
                # Add the course content
                course_id = await course_content_service.add_course_content(course_data)
                results["total_imported"] += 1
                results["course_ids"].append(course_id)
                
                # Clean up the temp file
                os.remove(file_path)
            except Exception as e:
                results["failed_items"].append({
                    "file": file.filename,
                    "error": str(e)
                })
                results["success"] = False
        
        return BaseResponse(
            success=results["success"],
            message=f"Imported {results['total_imported']} courses",
            data=results
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error importing courses: {str(e)}"
        )

# Development-only endpoint - will be disabled in production
if IS_DEV_MODE:
    @router.post("/import-sample", response_model=BaseResponse, tags=["Development"])
    async def import_sample_courses():
        """Import sample course content files for testing (DEVELOPMENT ONLY)"""
        try:
            # Find sample course files
            sample_dir = os.path.join(os.getcwd(), "samples")
            course_files = glob.glob(os.path.join(sample_dir, "sample_course*.json"))
            course_files.extend(glob.glob(os.path.join(sample_dir, "*se*.json")))
            
            if not course_files:
                return BaseResponse(
                    success=False,
                    message="No sample course files found in the samples directory"
                )
            
            results = {
                "success": True,
                "total_imported": 0,
                "failed_items": [],
                "course_ids": []
            }
            
            for file_path in course_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        course_data = json.load(f)
                    
                    # Add the course content
                    course_id = await course_content_service.add_course_content(course_data)
                    results["total_imported"] += 1
                    results["course_ids"].append(course_id)
                except Exception as e:
                    results["failed_items"].append({
                        "file": os.path.basename(file_path),
                        "error": str(e)
                    })
                    results["success"] = False
            
            return BaseResponse(
                success=results["success"],
                message=f"Imported {results['total_imported']} sample courses",
                data=results
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error importing sample courses: {str(e)}"
            )
            
    @router.delete("/cleanup", response_model=BaseResponse, tags=["Development"])
    async def cleanup_courses(
        course_ids: Optional[List[str]] = Query(None, description="Specific course IDs to delete"),
        delete_all: bool = Query(False, description="Set to true to delete all courses")
    ):
        """Delete specific courses or all courses (DEVELOPMENT ONLY)"""
        try:
            if not delete_all and not course_ids:
                return BaseResponse(
                    success=False,
                    message="Must specify either course_ids or delete_all=true"
                )
                
            results = {
                "success": True,
                "deleted_count": 0,
                "failed_items": []
            }
            
            if delete_all:
                # Get all courses
                all_courses = await course_content_service.list_courses(limit=1000)
                course_ids = [course["course_id"] for course in all_courses]
                
            for course_id in course_ids:
                try:
                    success = await course_content_service.delete_course_content(course_id)
                    if success:
                        results["deleted_count"] += 1
                    else:
                        results["failed_items"].append({
                            "course_id": course_id,
                            "error": "Course not found or could not be deleted"
                        })
                except Exception as e:
                    results["failed_items"].append({
                        "course_id": course_id,
                        "error": str(e)
                    })
                    
            if results["failed_items"]:
                results["success"] = False
                
            return BaseResponse(
                success=results["success"],
                message=f"Deleted {results['deleted_count']} courses",
                data=results
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error cleaning up courses: {str(e)}"
            ) 