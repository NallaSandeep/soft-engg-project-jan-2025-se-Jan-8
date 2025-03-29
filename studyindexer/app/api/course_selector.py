"""
CourseSelector API endpoints for StudyIndexerNew
This API helps identify which courses from a student's subscribed courses
are relevant to their query.
"""
from fastapi import APIRouter, HTTPException, Depends, status, Query, UploadFile, File
from typing import List, Dict, Any, Optional
import os
import time
import json
import glob

from ..models.course_selector import (
    CourseInfo,
    CourseTopic,
    WeekOverview,
    CourseContent,
    CourseSelectorQuery,
    CourseSelectorResponse,
    CourseMatchResult
)
from ..models.base import BaseResponse
from ..services.course_selector import CourseSelectorService

router = APIRouter()
course_selector_service = CourseSelectorService()

# Initialize CourseSelector service
@router.on_event("startup")
async def startup_db_client():
    await course_selector_service.initialize()

@router.get("/courses", response_model=BaseResponse)
async def list_all_courses(
    limit: int = Query(100, description="Maximum number of courses to return"),
    offset: int = Query(0, description="Number of courses to skip")
):
    """
    List all courses in the database with full details.
    
    This endpoint returns a list of all indexed courses with their complete information,
    useful for exploration and verification of the data.
    """
    try:
        courses = await course_selector_service.list_all_courses(limit, offset)
        
        return BaseResponse(
            success=True,
            message=f"Found {len(courses)} courses",
            data={
                "courses": courses,
                "total": len(courses),
                "limit": limit,
                "offset": offset
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing courses: {str(e)}"
        )

@router.post("/search", response_model=CourseSelectorResponse)
async def select_courses(query: CourseSelectorQuery):
    """Find relevant courses based on a query and subscribed courses"""
    try:
        total_results, results, query_time_ms = await course_selector_service.select_courses(query)
        
        return CourseSelectorResponse(
            success=True,
            results=results,
            query=query.query,
            total_results=total_results,
            query_time_ms=query_time_ms,
            metadata={
                "subscribed_courses": query.subscribed_courses
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error selecting courses: {str(e)}"
        )

@router.post("/index", response_model=BaseResponse)
async def index_course(course: CourseContent):
    """Index a course for the course selector"""
    try:
        course_id = await course_selector_service.index_course(course)
        
        return BaseResponse(
            success=True,
            message="Course indexed successfully",
            data={
                "course_id": course_id
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error indexing course: {str(e)}"
        )

@router.post("/index-sample-courses", response_model=BaseResponse)
async def index_sample_courses():
    """Index the sample course files (for demo/testing purposes)"""
    try:
        # Find sample course files
        sample_dir = os.path.join(os.getcwd(), "samples")
        course_files = glob.glob(os.path.join(sample_dir, "*.json"))
        
        if not course_files:
            return BaseResponse(
                success=False,
                message="No sample course files found in the samples directory"
            )
        
        # Index the courses
        result = await course_selector_service.bulk_index_courses_from_files(course_files)
        
        return BaseResponse(
            success=result["success"],
            message=f"Indexed {result['total_indexed']} sample courses",
            data=result
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error indexing sample courses: {str(e)}"
        )

@router.get("/{course_id}", response_model=BaseResponse)
async def get_course(course_id: int):
    """Get course details by ID"""
    try:
        result = await course_selector_service.get_course(course_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Course with ID {course_id} not found"
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
            detail=f"Error retrieving course: {str(e)}"
        ) 