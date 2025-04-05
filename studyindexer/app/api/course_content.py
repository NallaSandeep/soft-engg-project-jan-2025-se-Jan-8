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
import logging

from ..models.course_selector import CourseContent, CourseInfo, CourseTopic, WeekOverview
from ..models.base import BaseResponse, BaseSearchQuery, BaseSearchResponse
from ..services.course_content import CourseContentService
from ..services.chroma import ChromaService
from ..services.course_selector import CourseSelectorService
from ..services.personal_resource import PersonalResourceService
from ..services.faq import FAQService

# Set up standard logger
logger = logging.getLogger(__name__)

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
        
        # --- Log Received Payload --- BEGIN
        received_acronyms = course_data.get('course', {}).get('acronyms', 'MISSING')
        received_synonyms = course_data.get('course', {}).get('synonyms', 'MISSING')
        course_code = course_data.get('course', {}).get('code', 'UNKNOWN')
        logger.debug(f"DEBUG: API /course-content received for {course_code} - Acronyms: {json.dumps(received_acronyms)}, Synonyms: {json.dumps(received_synonyms)}")
        # --- Log Received Payload --- END
        
        # For weeks, ensure they have the required fields
        if "weeks" in course_data:
            for i, week in enumerate(course_data["weeks"]):
                if "week_id" in week and "week_number" not in week:
                    week["week_number"] = week.get("order", i + 1)
                if "description" not in week:
                    week["description"] = week.get("title", f"Week {i+1}")
        
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
    limit: int = Query(10, description="Maximum number of results to return"),
    min_score: float = Query(0.01, description="Minimum relevance score threshold (0.0-1.0)"),
    exact_match_boost: float = Query(0.1, description="Boost factor for exact term matches (0.0-1.0)"),
    phrase_match_boost: float = Query(0.15, description="Boost for exact phrase matches (0.0-1.0)"),
    description_threshold: float = Query(0.05, description="Threshold for including course descriptions (0.0-1.0)")
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
    
    Advanced parameters allow fine-tuning of search behavior:
    - min_score: Controls minimum relevance needed (lower = more results)
    - exact_match_boost: Controls boost for keyword matches
    - phrase_match_boost: Controls boost for exact phrase matches
    - description_threshold: Controls when to include course descriptions
    """
    try:
        raw_results = await course_content_service.search_courses(
            query=query, 
            limit=limit,
            course_ids=course_ids,
            min_score=min_score,
            exact_match_boost=exact_match_boost,
            phrase_match_boost=phrase_match_boost,
            description_threshold=description_threshold
        )
        
        # Extract content chunks
        content_chunks = raw_results.get("content_chunks", [])
        
        # Group results by course
        courses_map = {}
        for chunk in content_chunks:
            metadata = chunk.get("metadata", {})
            course_id = metadata.get("course_id", "unknown")
            course_code = metadata.get("course_code", "unknown")
            course_title = metadata.get("course_title", "Unknown Course")
            
            # Create source_course if not exists
            if course_id not in courses_map:
                courses_map[course_id] = {
                    "source_course": {
                        "code": course_code,
                        "title": course_title,
                        "match_score": chunk.get("relevance_score", 0)
                    },
                    "content_chunks": [],
                    "score": chunk.get("relevance_score", 0)
                }
            
            # Determine chunk type and extract relevant info
            content_type = metadata.get("content_type", "unknown")
            
            if content_type == "lecture_chunk":
                chunk_data = {
                    "type": "lecture",
                    "title": metadata.get("lecture_title", ""),
                    "description": metadata.get("description", ""),
                    "content": chunk.get("content", ""),
                    "week_number": metadata.get("week_number", 0)
                }
            elif content_type == "course_description":
                chunk_data = {
                    "type": "course",
                    "title": course_title,
                    "description": metadata.get("description", ""),
                    "content": chunk.get("content", "")
                }
            else:
                # Generic chunk type
                chunk_data = {
                    "type": content_type,
                    "title": metadata.get("title", ""),
                    "description": metadata.get("description", ""),
                    "content": chunk.get("content", "")
                }
            
            # Add to course's content chunks
            courses_map[course_id]["content_chunks"].append(chunk_data)
            
            # Update score if higher
            if chunk.get("relevance_score", 0) > courses_map[course_id]["score"]:
                courses_map[course_id]["score"] = chunk.get("relevance_score", 0)
                courses_map[course_id]["source_course"]["match_score"] = chunk.get("relevance_score", 0)
        
        # Convert to list and sort by score
        formatted_results = list(courses_map.values())
        formatted_results.sort(key=lambda x: x["score"], reverse=True)
        
        return BaseResponse(
            success=True,
            data={
                "content_chunks": formatted_results,
                "total_count": len(formatted_results),
                "query": query,
                "limit": limit
            }
        )
    except Exception as e:
        logger.error(f"Error searching course content: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching course content: {str(e)}"
        )

# Development-only endpoint for resetting ChromaDB - MUST come BEFORE the parameterized routes
if IS_DEV_MODE:
    @router.delete("/reset", response_model=BaseResponse, tags=["Development"])
    async def reset_chromadb(
        confirm: bool = Query(False, description="Set to true to confirm complete reset of ChromaDB. WARNING: This will delete ALL data and cannot be undone.")
    ):
        """Delete ALL data from ChromaDB (DEVELOPMENT ONLY)
        
        WARNING: This will delete ALL data in ChromaDB including:
        - Course content
        - Course selector data
        - Personal resources
        - FAQs
        
        This operation cannot be undone.
        """
        if not confirm:
            return BaseResponse(
                success=False,
                message="Operation not confirmed. Set confirm=true to proceed with reset"
            )
            
        try:
            # Get ChromaDB service
            chroma = ChromaService()
            
            # Reset all collections
            success = await chroma.reset_all()
            
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to reset ChromaDB"
                )
                
            # Re-initialize all services to create fresh collections
            course_content = CourseContentService()
            course_selector = CourseSelectorService()
            personal_resource = PersonalResourceService()
            faq = FAQService()
            
            await course_content.initialize()
            await course_selector.initialize()
            await personal_resource.initialize()
            await faq.initialize()
            
            return BaseResponse(
                success=True,
                message="ChromaDB reset successful. All collections deleted and reinitialized."
            )
            
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error during cleanup: {str(e)}"
            )

@router.get("/{course_id}", response_model=BaseResponse)
async def get_course_content(course_id: Union[int, str]):
    """Get course content by ID or course code"""
    try:
        result = await course_content_service.get_course_content(course_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Course content with ID {course_id} not found"
            )
            
        # Return raw dictionary instead of trying to convert to CourseContent model
        # This provides more flexibility if the data structure doesn't exactly match
        if isinstance(result, dict):
            return BaseResponse(
                success=True,
                data=result
            )
        else:
            # If it's a CourseContent model, convert to dict
            try:
                return BaseResponse(
                    success=True,
                    data=result.dict()
                )
            except AttributeError:
                # If dict() fails, return the raw result
                return BaseResponse(
                    success=True,
                    data=result
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