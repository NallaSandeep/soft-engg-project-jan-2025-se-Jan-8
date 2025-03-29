"""
PersonalResource models for StudyIndexerNew
This module contains the data models for the PersonalResource functionality,
which helps students manage and search their personal resources.
"""
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from enum import Enum
from .base import BaseSearchQuery, BaseSearchResponse

class ResourceType(str, Enum):
    """Resource type enum"""
    TEXT = "text"
    FILE = "file"
    URL = "url"

class ResourceFile(BaseModel):
    """Resource file model"""
    id: int = Field(..., description="Resource file ID")
    resource_id: int = Field(..., description="Parent resource ID")
    name: str = Field(..., description="File name")
    type: ResourceType = Field(..., description="Resource type (text, file, url)")
    content: Optional[str] = Field(None, description="Text content, for text/url types")
    file_path: Optional[str] = Field(None, description="File path for uploaded files")
    file_type: Optional[str] = Field(None, description="MIME type")
    file_size: Optional[int] = Field(None, description="File size in bytes")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class PersonalResourceInfo(BaseModel):
    """Personal resource information model"""
    id: int = Field(..., description="Resource ID")
    user_id: int = Field(..., description="User ID")
    course_id: int = Field(..., description="Course ID")
    name: str = Field(..., description="Resource name")
    description: Optional[str] = Field(None, description="Resource description")
    is_active: bool = Field(True, description="Whether the resource is active")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    settings: Optional[Dict[str, Any]] = Field(None, description="Resource settings")

class PersonalResource(BaseModel):
    """Complete personal resource model with files"""
    resource: PersonalResourceInfo
    files: List[ResourceFile] = Field(default_factory=list)
    course_info: Optional[Dict[str, Any]] = Field(None, description="Associated course information")

class PersonalResourceSearchQuery(BaseSearchQuery):
    """Query model for personal resource search"""
    student_id: int = Field(..., description="Student ID to search resources for")
    personal_resource_ids: Optional[List[int]] = Field(
        None, description="Optional list of resource IDs to filter search results"
    )
    course_ids: Optional[List[int]] = Field(
        None, description="Optional list of course IDs to filter search results"
    )

class PersonalResourceSearchResult(BaseModel):
    """Search result model for personal resources"""
    resource_id: int = Field(..., description="Resource ID")
    title: str = Field(..., description="Resource title/name")
    description: Optional[str] = Field(None, description="Resource description")
    content: str = Field(..., description="Matched content")
    type: str = Field(..., description="Resource type")
    course_id: Optional[int] = Field(None, description="Associated course ID")
    score: float = Field(..., ge=0.0, le=1.0, description="Relevance score")
    file_id: Optional[int] = Field(None, description="File ID if applicable")

class PersonalResourceSearchResponse(BaseSearchResponse):
    """Response model for personal resource search"""
    resources: List[PersonalResourceSearchResult]
    metadata: Optional[Dict[str, Any]] = Field(
        None, description="Additional metadata about the search"
    ) 