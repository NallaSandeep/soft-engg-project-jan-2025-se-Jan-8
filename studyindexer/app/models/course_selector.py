"""
CourseSelector models for StudyIndexerNew
This module contains the data models for the CourseSelector functionality,
which helps identify relevant courses from a student's subscribed courses
based on their query.
"""
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from enum import Enum
from .base import BaseSearchQuery, BaseSearchResponse

class CourseMetadata(BaseModel):
    """Course metadata model"""
    level: str = Field(default="introductory", description="Course level (introductory/advanced/etc)")
    prerequisites: List[str] = Field(default_factory=list, description="List of prerequisite courses")
    is_active: bool = Field(default=True, description="Whether the course is currently active")

class WeekOverview(BaseModel):
    """Week overview model"""
    week_number: int = Field(..., ge=1, le=15, description="Week number")
    title: str = Field(..., min_length=2, max_length=200, description="Week title")
    description: str = Field(..., min_length=10, description="Week description")
    topics: List[str] = Field(default_factory=list, description="Topics covered in this week")
    summary: Optional[str] = Field(None, description="LLM-generated summary of the week")
    concepts: Optional[List[str]] = Field(default_factory=list, description="Key concepts covered in this week")

class CourseInfo(BaseModel):
    """Course information model"""
    code: str = Field(..., description="Course code")
    title: str = Field(..., description="Course title")
    description: str = Field(..., description="Course description")
    course_id: Optional[int] = Field(None, description="Course ID that matches StudyHub")
    department: Optional[str] = Field(None, description="Department")
    credits: Optional[int] = Field(None, description="Number of credits")
    summary: Optional[str] = Field(None, description="LLM-generated summary of the course")
    concepts: Optional[List[str]] = Field(default_factory=list, description="Key concepts covered in the course")

class CourseTopic(BaseModel):
    """Course topic model"""
    name: str = Field(..., description="Topic name")
    description: Optional[str] = Field(None, description="Topic description")

class CourseContent(BaseModel):
    """
    Course content model with all course data
    
    This model represents the complete data for a course, including metadata,
    weeks, topics, lectures, and assignments. It serves as the primary data
    structure for the RAG system, containing all content chunks that can be
    retrieved and used by StudyAI for generating responses.
    """
    course: CourseInfo
    metadata: Optional[CourseMetadata] = None
    weeks: Optional[List[WeekOverview]] = None
    topics: Optional[List[CourseTopic]] = None
    lectures: Optional[List[Dict[str, Any]]] = None
    assignments: Optional[List[Dict[str, Any]]] = None

class CourseSelectorQuery(BaseSearchQuery):
    """Query model for CourseSelector search"""
    subscribed_courses: List[str] = Field(
        ..., 
        description="List of course codes the student is subscribed to (e.g. 'MATH301', 'CS350')",
        min_items=1
    )
    
    @validator('subscribed_courses')
    def validate_subscribed_courses(cls, v):
        """Validate that there is at least one subscribed course"""
        if not v:
            raise ValueError("At least one subscribed course code must be provided")
        return v

class CourseMatchResult(BaseModel):
    """Search result model for matched courses"""
    code: str = Field(..., description="Course code (e.g. 'MATH301', 'CS350')")
    title: str = Field(..., description="Course title")
    description: Optional[str] = Field(None, description="Course description")
    score: float = Field(..., ge=0.0, le=1.0, description="Relevance score")
    matched_topics: List[str] = Field(default_factory=list, description="Topics that matched the query")

class CourseSelectorResponse(BaseSearchResponse):
    """Response model for CourseSelector operations"""
    results: List[CourseMatchResult]
    metadata: Optional[Dict[str, Any]] = Field(
        default=None, 
        description="Additional metadata about the search"
    ) 