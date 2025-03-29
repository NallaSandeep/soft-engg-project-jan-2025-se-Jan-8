"""
IntegrityCheck models for StudyIndexerNew
This module contains the data models for the IntegrityCheck functionality,
which helps identify if a query potentially matches graded assignments.
"""
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from .base import BaseSearchQuery, BaseSearchResponse

class GradedAssignmentInfo(BaseModel):
    """Information about a graded assignment for integrity checking"""
    assignment_id: str = Field(..., description="Assignment ID")
    title: str = Field(..., description="Assignment title")
    description: Optional[str] = Field(None, description="Assignment description")
    course_id: str = Field(..., description="Course ID")
    course_code: str = Field(..., description="Course code")
    course_title: str = Field(..., description="Course title")
    week_id: Optional[str] = Field(None, description="Week ID")
    week_number: Optional[int] = Field(None, description="Week number")
    week_title: Optional[str] = Field(None, description="Week title")
    due_date: Optional[datetime] = Field(None, description="Assignment due date")
    is_active: bool = Field(True, description="Whether the assignment is active")

class GradedAssignmentQuestion(BaseModel):
    """Question from a graded assignment for integrity checking"""
    question_id: str = Field(..., description="Question ID")
    assignment_id: str = Field(..., description="Assignment ID")
    content: str = Field(..., description="Question content")
    title: Optional[str] = Field(None, description="Question title")
    question_type: str = Field(..., description="Question type (MCQ, MSQ, NUMERIC)")
    options: Optional[List[str]] = Field(None, description="Options for MCQ/MSQ questions")
    points: Optional[int] = Field(None, description="Question points")
    
class IntegrityCheckQuery(BaseSearchQuery):
    """Query to check if it matches graded assignment questions"""
    query: str = Field(..., description="The query text to check against graded assignments")
    course_ids: Optional[List[int]] = Field(None, description="Optional list of course IDs to limit the check")
    threshold: float = Field(0.8, ge=0.0, le=1.0, description="Minimum score threshold to consider a match")

class MatchSegment(BaseModel):
    """A matched segment from the query and question"""
    query_segment: str = Field(..., description="The matching segment from the query")
    matched_segment: str = Field(..., description="The matching segment from the question")
    similarity: float = Field(..., ge=0.0, le=1.0, description="Similarity score")

class AssignmentMatch(BaseModel):
    """A matching assignment and question"""
    assignment_id: str = Field(..., description="Assignment ID")
    title: str = Field(..., description="Assignment title")
    course_id: str = Field(..., description="Course ID")
    course_code: Optional[str] = Field(None, description="Course code") 
    course_title: Optional[str] = Field(None, description="Course title")
    highest_similarity: float = Field(..., ge=0.0, le=1.0, description="Highest similarity score")
    matched_questions: List[str] = Field(default_factory=list, description="List of matched question IDs")
    segments: List["MatchSegment"] = Field(default_factory=list, description="Matched segments with details")
    
class HighestMatch(BaseModel):
    """Information about the highest matching assignment"""
    assignment_id: str = Field(..., description="Assignment ID")
    question_id: str = Field(..., description="Question ID")
    title: str = Field(..., description="Assignment title")
    question_title: Optional[str] = Field(None, description="Question title")
    similarity: float = Field(..., ge=0.0, le=1.0, description="Similarity score")
    
class IntegrityCheckResponse(BaseSearchResponse):
    """Response for integrity check operation"""
    matches: List[AssignmentMatch] = Field(..., description="Matching assignments with similarity scores")
    highest_match: Optional[HighestMatch] = Field(None, description="Details of the highest matching assignment")
    potential_violation: bool = Field(False, description="Whether any match exceeded threshold") 