from enum import Enum
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, validator

class DocumentStatus(str, Enum):
    """Document processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class DocumentType(str, Enum):
    """Supported document types"""
    PDF = "pdf"
    TEXT = "text"
    DOCX = "docx"
    MARKDOWN = "markdown"

class CollectionType(str, Enum):
    """Vector store collection types"""
    GENERAL = "general"
    COURSE = "course"
    PERSONAL = "personal"
    FAQ = "faq"

class BaseResponse(BaseModel):
    """Base response model"""
    success: bool = True
    message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ErrorDetail(BaseModel):
    """Error detail model"""
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None

class ErrorResponse(BaseResponse):
    """Error response model"""
    success: bool = False
    error: ErrorDetail

    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "message": "Operation failed",
                "error": {
                    "code": "DOCUMENT_NOT_FOUND",
                    "message": "The requested document was not found",
                    "details": {"document_id": "123"}
                },
                "timestamp": "2024-02-08T12:00:00Z"
            }
        } 