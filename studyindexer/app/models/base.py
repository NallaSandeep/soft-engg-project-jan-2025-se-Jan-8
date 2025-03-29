"""
Base models for StudyIndexerNew
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from enum import Enum

class BaseResponse(BaseModel):
    """Base response model for API endpoints"""
    success: bool
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

class BaseSearchQuery(BaseModel):
    """Base search query model"""
    query: str = Field(..., min_length=0, description="Search query text")
    limit: int = Field(default=10, ge=1, le=50, description="Maximum number of results")
    min_score: float = Field(default=0.3, ge=0.0, le=1.0, description="Minimum similarity score")

class BaseSearchResponse(BaseModel):
    """Base search response model"""
    success: bool
    query: str
    total_results: int
    query_time_ms: float 