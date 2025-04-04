"""
FAQ database models for StudyIndexerNew
Based on the implementation specification in FAQ_Database_Implementation.md

Validation Rules:
- topic: min 2 chars, max 100 chars
- question: min 5 chars, max 500 chars
- answer: min 2 chars, max 5000 chars (to allow short answers like "Yes", "No", "December")
- tags: can contain any printable characters, max 100 chars each
- source: min 2 chars, max 100 chars
- priority: integer between 0-100
"""
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
from .base import BaseSearchQuery, BaseSearchResponse

class FAQItem(BaseModel):
    """FAQ item model with validation"""
    topic: str = Field(..., min_length=2, max_length=100, description="Topic category of the FAQ")
    question: str = Field(..., min_length=5, max_length=500, description="The FAQ question")
    answer: str = Field(..., min_length=2, max_length=5000, description="The FAQ answer")
    tags: List[str] = Field(default=[], description="Tags for filtering and categorization")
    source: str = Field(..., min_length=2, max_length=100, description="Source document of the information")
    last_updated: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    created_by: Optional[str] = Field(None, description="User who created this FAQ")
    is_published: bool = Field(True, description="Whether this FAQ is publicly visible")
    priority: int = Field(default=0, ge=0, le=100, description="Priority/importance (0-100)")
    
    @validator('tags')
    def validate_tags(cls, v):
        """Validate tags format"""
        if v:
            for tag in v:
                if len(tag) > 100:
                    raise ValueError("Tag length must not exceed 100 characters")
                # We allow any printable character now, just check that the tag isn't empty or just whitespace
                if not tag.strip():
                    raise ValueError("Tags cannot be empty or only whitespace")
        return v

class FAQCreateRequest(BaseModel):
    """Request model for creating a new FAQ"""
    topic: str = Field(..., min_length=2, max_length=100)
    question: str = Field(..., min_length=5, max_length=500)
    answer: str = Field(..., min_length=2, max_length=5000)
    tags: List[str] = Field(default=[])
    source: str = Field(..., min_length=2, max_length=100)
    is_published: bool = Field(True)
    priority: int = Field(default=0, ge=0, le=100)

class FAQUpdateRequest(BaseModel):
    """Request model for updating an existing FAQ"""
    topic: Optional[str] = Field(None, min_length=2, max_length=100)
    question: Optional[str] = Field(None, min_length=5, max_length=500)
    answer: Optional[str] = Field(None, min_length=2, max_length=5000)
    tags: Optional[List[str]] = None
    source: Optional[str] = Field(None, min_length=2, max_length=100)
    is_published: Optional[bool] = None
    priority: Optional[int] = Field(None, ge=0, le=100)

class FAQSearchQuery(BaseSearchQuery):
    """Query model for FAQ search"""
    tags: Optional[List[str]] = Field(None, description="Filter by specific tags")
    topic: Optional[str] = Field(None, description="Filter by topic")
    source: Optional[str] = Field(None, description="Filter by source document")

class FAQSearchResult(BaseModel):
    """Search result model for FAQ items"""
    id: str
    topic: str
    question: str
    answer: str
    tags: List[str]
    score: float = Field(..., ge=0.0, le=1.0, description="Similarity score")
    source: str
    last_updated: datetime

class FAQSearchResponse(BaseSearchResponse):
    """Response model for FAQ search operations"""
    results: List[FAQSearchResult]

class JSONLImportItem(BaseModel):
    """Model for a single item in JSONL import format"""
    topic: str = Field(..., min_length=2, max_length=100)
    question: str = Field(..., min_length=5, max_length=500)
    answer: str = Field(..., min_length=2, max_length=5000)
    tags: List[str] = Field(default=[])
    source: str = Field(..., min_length=2, max_length=100)

class JSONLImportResponse(BaseModel):
    """Response model for JSONL import operations"""
    success: bool
    total_imported: int
    failed_items: Optional[List[Dict[str, Any]]] = None
    message: Optional[str] = None 