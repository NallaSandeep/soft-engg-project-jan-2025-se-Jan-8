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
        # Simplified search logic
        total_results, results, query_time_ms = await course_selector_service.select_courses(query)
        return CourseSelectorResponse(
            success=True,
            results=results,
            query=query.query,
            total_results=total_results,
            query_time_ms=query_time_ms,
            metadata={
                "subscribed_courses": query.subscribed_courses,
                "query_time_ms": query_time_ms,
                "total_results": total_results
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error selecting courses: {str(e)}"
        )

@router.post("/index", response_model=BaseResponse)
async def index_course(course_data: Dict[str, Any]):
    """Index a course for the course selector"""
    try:
        # Transform simple string topics to CourseTopic objects if needed
        if "topics" in course_data and isinstance(course_data["topics"], list):
            transformed_topics = []
            for topic in course_data["topics"]:
                if isinstance(topic, str):
                    # Convert string to CourseTopic format
                    transformed_topics.append({"name": topic, "description": None})
                else:
                    # Keep existing object format
                    transformed_topics.append(topic)
            course_data["topics"] = transformed_topics
        
        # Add required fields for StudyIndexer format compatibility
        if "weeks" in course_data:
            for i, week in enumerate(course_data["weeks"]):
                if "week_id" in week and "week_number" not in week:
                    week["week_number"] = week.get("order", i + 1)  
                if "description" not in week:
                    week["description"] = week.get("title", f"Week {i+1}")
        
        # Extract course field if needed
        has_valid_course = False
        if "course" in course_data:
            if isinstance(course_data["course"], dict) and "title" in course_data["course"]:
                has_valid_course = True
        elif "title" in course_data:
            # Create course field from main data
            course_data["course"] = {
                "code": course_data.get("code", "UNKNOWN"),
                "title": course_data.get("title", ""),
                "description": course_data.get("description", ""),
                "course_id": course_data.get("course_id", None)
            }
            has_valid_course = True
            
        if not has_valid_course:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Course data must contain a valid 'course' object with 'title'"
            )
                
        # Validate with the CourseContent model
        try:
            course_content = CourseContent(**course_data)
            # Convert to dict for the service - this resolves the .get() attribute error
            course_dict = course_content.model_dump()
        except Exception as validation_error:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid course data format: {str(validation_error)}"
            )
        
        # Index the course with validated data
        course_code = await course_selector_service.index_course(course_dict)
        
        return BaseResponse(
            success=True,
            message="Course indexed successfully",
            data={
                "course_code": course_code
            }
        )
    except HTTPException:
        raise
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

@router.post("/import-json-data", response_model=BaseResponse)
async def import_json_data(
    file: UploadFile = File(...),
    transform_format: bool = Query(True, description="Whether to attempt format transformation for non-standard JSON structures")
):
    """
    Import and index a course from a JSON file.
    Supports both standard format and alternative structures like sample.json.
    """
    try:
        # Read the uploaded file
        content = await file.read()
        
        try:
            data = json.loads(content.decode('utf-8'))
        except UnicodeDecodeError:
            # Try other encodings if UTF-8 fails
            for encoding in ['latin-1', 'utf-16', 'windows-1252']:
                try:
                    data = json.loads(content.decode(encoding))
                    break
                except:
                    continue
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Unable to decode the JSON file. Please check the file encoding."
                )
        
        # Transform the data if needed and requested
        if transform_format and "course" in data:
            # Handle format like sample.json
            course_info = data["course"]
            
            # Make sure course_id is a string (for ChromaDB compatibility)
            course_id = course_info.get("course_id", "")
            if not isinstance(course_id, str):
                course_id = str(course_id)
            
            # Create standard course content structure
            transformed_data = {
                "course": {
                    "code": course_info.get("code", ""),  # Make sure code is prioritized
                    "course_id": course_id,
                    "title": course_info.get("title", ""),
                    "description": course_info.get("description", ""),
                    "department": course_info.get("department", ""),
                    "credits": course_info.get("credits", 0)
                },
                "topics": [],
                "concepts_covered": [],
                "concepts_not_covered": [],
                "weeks": [],
                "lectures": []
            }
            
            # Validate course code is present - it's required
            if not transformed_data["course"]["code"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Course code is required in the JSON file"
                )
            
            # Extract concepts from LLM_Summary
            if "LLM_Summary" in course_info:
                llm_summary = course_info["LLM_Summary"]
                # Make sure LLM_Summary gets included in the course object
                transformed_data["course"]["LLM_Summary"] = llm_summary
                
                # IMPORTANT: Extract concepts_covered
                if "concepts_covered" in llm_summary and llm_summary["concepts_covered"]:
                    print(f"Found concepts_covered in LLM_Summary: {llm_summary['concepts_covered']}")
                    transformed_data["concepts_covered"] = llm_summary["concepts_covered"]
                    
                    # Create topics from concepts_covered
                    for i, topic_name in enumerate(llm_summary["concepts_covered"]):
                        if topic_name:  # Skip empty topics
                            transformed_data["topics"].append({
                                "name": topic_name,
                                "description": "Generated from concepts_covered",
                                "week": (i % 4) + 1,  # Distribute across weeks 1-4
                                "importance": 8
                            })
                
                # Add concepts_not_covered
                if "concepts_not_covered" in llm_summary and llm_summary["concepts_not_covered"]:
                    transformed_data["concepts_not_covered"] = llm_summary["concepts_not_covered"]
            
            # Extract weeks
            if "weeks" in data:
                for week in data["weeks"]:
                    week_data = {
                        "order": week.get("order", week.get("week_id", 0)),
                        "title": week.get("title", ""),
                        "description": week.get("description", "Week content"),
                        "is_published": True,
                        "week_number": week.get("week_id", week.get("order", 0)),
                        "topics": []  # Add topics field
                    }
                    
                    # Extract week LLM_Summary if available
                    if "LLM_Summary" in week:
                        week_data["LLM_Summary"] = week["LLM_Summary"]
                        
                        # Add topics from concepts_covered in week LLM_Summary
                        if "concepts_covered" in week["LLM_Summary"]:
                            week_concepts = week["LLM_Summary"]["concepts_covered"]
                            if week_concepts:
                                week_data["topics"] = week_concepts
                    
                    transformed_data["weeks"].append(week_data)
            
            # Extract lectures and their concepts
            if "lectures" in data:
                for lecture in data["lectures"]:
                    transcript = lecture.get("content_transcript", "")
                    
                    # Get lecture summary and concepts if available
                    lecture_concepts = []
                    if "keywords" in lecture:
                        lecture_concepts = lecture["keywords"]
                    
                    lecture_data = {
                        "title": lecture.get("title", ""),
                        "week": lecture.get("week_id", 1),
                        "order": lecture.get("order", 1),
                        "content_type": lecture.get("resource_type", "text"),
                        "url": lecture.get("video_url", lecture.get("resource_url", "")),
                        "transcript": transcript,
                        "concepts": lecture_concepts,
                        "keywords": lecture.get("keywords", []),
                        "is_published": True
                    }
                    
                    # Add LLM_Summary if available
                    if "LLM_Summary" in lecture:
                        lecture_data["LLM_Summary"] = lecture["LLM_Summary"]
                        
                        # Extract concepts from LLM_Summary
                        if "concepts_covered" in lecture["LLM_Summary"]:
                            lecture_concepts.extend(lecture["LLM_Summary"]["concepts_covered"])
                            
                            # Add unique lecture concepts to the course concepts
                            for concept in lecture["LLM_Summary"]["concepts_covered"]:
                                if concept and concept not in transformed_data["concepts_covered"]:
                                    transformed_data["concepts_covered"].append(concept)
                    
                    transformed_data["lectures"].append(lecture_data)
            
            data = transformed_data
        else:
            # For standard format, rename course_info to course if needed
            if "course_info" in data and "course" not in data:
                data["course"] = data.pop("course_info")
            
            # Even if not transforming, we need to add week_number to weeks
            if "weeks" in data:
                for week in data["weeks"]:
                    if "week_number" not in week:
                        week["week_number"] = week.get("order", week.get("week_id", 0))
        
        # Index the course with our service
        try:
            # Validate and convert to dictionary to pass to the service
            course_content = CourseContent(**data)
            course_dict = course_content.model_dump()
            
            # IMPORTANT: Preserve any concepts_covered after validation
            if "concepts_covered" in data and isinstance(data["concepts_covered"], list):
                course_dict["concepts_covered"] = data["concepts_covered"]
                print(f"Preserved concepts_covered after validation: {course_dict['concepts_covered']}")
            
            # Also preserve concepts in LLM_Summary
            if "course" in data and "LLM_Summary" in data["course"] and "concepts_covered" in data["course"]["LLM_Summary"]:
                if "course" not in course_dict:
                    course_dict["course"] = {}
                if "LLM_Summary" not in course_dict["course"]:
                    course_dict["course"]["LLM_Summary"] = {}
                
                course_dict["course"]["LLM_Summary"]["concepts_covered"] = data["course"]["LLM_Summary"]["concepts_covered"]
                print(f"Preserved LLM_Summary.concepts_covered: {course_dict['course']['LLM_Summary']['concepts_covered']}")
        except Exception as validation_error:
            print(f"Validation error: {validation_error}")
            
            return BaseResponse(
                success=False,
                message=f"Invalid course data format: {str(validation_error)}",
                data={
                    "original_format": "alternative" if "course" in data else "standard"
                }
            )
        
        # Index the course
        course_code = await course_selector_service.index_course(course_dict)
        
        return BaseResponse(
            success=True,
            message=f"Course indexed successfully from file {file.filename}",
            data={
                "course_code": course_code,
                "original_format": "alternative" if "course" in data else "standard",
                "transformation_applied": transform_format and "course" in data
            }
        )
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON format. Please check the file contents."
        )
    except Exception as e:
        print(f"Error importing course data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error importing course data: {str(e)}"
        )

@router.get("/{course_code}", response_model=BaseResponse)
async def get_course(course_code: str):
    """Get course details by code"""
    try:
        result = await course_selector_service.get_course(course_code)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Course with code {course_code} not found"
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

@router.delete("/courses/{course_code}", response_model=BaseResponse)
async def delete_course(course_code: str):
    """Delete a course by code"""
    try:
        success = await course_selector_service.delete_course(course_code)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Course with code {course_code} not found"
            )
        return BaseResponse(
            success=True,
            message=f"Course with code {course_code} deleted successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting course: {str(e)}"
        ) 