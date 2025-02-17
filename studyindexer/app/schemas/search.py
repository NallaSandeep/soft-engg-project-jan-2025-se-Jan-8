from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, field_validator
from app.schemas.base import CollectionType, BaseResponse

class SearchQuery(BaseModel):
    """Search query model"""
    text: str = Field(..., min_length=3, max_length=1000)
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(10, ge=1, le=50, description="Results per page")
    filters: Optional[Dict[str, Any]] = None
    collection: CollectionType = Field(default=CollectionType.GENERAL)
    min_score: float = Field(0.0, ge=0.0, le=1.0)

    @field_validator('text')
    def validate_query_text(cls, v):
        if len(v.strip()) < 3:
            raise ValueError("Search query must contain at least 3 non-whitespace characters")
        return v.strip()

    class Config:
        json_schema_extra = {
            "example": {
                "text": "machine learning",
                "page": 1,
                "page_size": 10,
                "filters": {"course_id": "CS101"},
                "collection": "general",
                "min_score": 0.5
            }
        }

class SearchResult(BaseModel):
    """Search result model"""
    document_id: str
    score: float = Field(..., ge=0.0, le=1.0)
    content: str
    metadata: Dict[str, Any]
    page_number: Optional[int] = Field(None, ge=1)
    position: Optional[Dict[str, Optional[int]]] = None
    highlight: Optional[Dict[str, List[str]]] = None

class PaginationMetadata(BaseModel):
    """Pagination metadata"""
    current_page: int = Field(..., ge=1)
    page_size: int = Field(..., ge=1)
    total_pages: int = Field(..., ge=0)
    total_results: int = Field(..., ge=0)
    has_next: bool
    has_previous: bool

class SearchResponse(BaseResponse):
    """Search operation response model"""
    results: List[SearchResult]
    pagination: PaginationMetadata
    query_time_ms: float = Field(..., ge=0)
    collection: str
    filters_applied: Optional[Dict[str, Any]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "results": [{
                    "document_id": "doc_123",
                    "score": 0.85,
                    "content": "Sample document content...",
                    "metadata": {
                        "title": "Sample Document",
                        "course_id": "CS101"
                    },
                    "page_number": 1,
                    "highlight": {
                        "text": ["Relevant text snippet..."]
                    }
                }],
                "pagination": {
                    "current_page": 1,
                    "page_size": 10,
                    "total_pages": 5,
                    "total_results": 45,
                    "has_next": True,
                    "has_previous": False
                },
                "query_time_ms": 125.45,
                "collection": "course",
                "filters_applied": {"course_id": "CS101"}
            }
        } 