"""Document schemas with validation"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, field_validator, model_validator
from typing_extensions import Annotated
from app.schemas.base import (
    DocumentStatus,
    DocumentType,
    CollectionType,
    BaseResponse
)

class PersonalMetadata(BaseModel):
    """Personal knowledge base metadata"""
    folder_path: Optional[str] = Field(None, description="Virtual folder path in personal KB")
    is_favorite: bool = Field(False, description="Whether document is marked as favorite")
    last_viewed: Optional[datetime] = Field(None, description="Last time document was viewed")
    importance: int = Field(1, ge=1, le=5, description="Document importance (1-5)")
    source_url: Optional[str] = Field(None, description="Original source URL if any")
    related_docs: List[str] = Field(default_factory=list, description="Related document IDs")
    custom_fields: Dict[str, Any] = Field(default_factory=dict, description="User-defined fields")

class DocumentMetadata(BaseModel):
    """Document metadata model with validation"""
    title: Optional[str] = Field(None, max_length=255)
    author: Optional[str] = Field(None, max_length=100)
    course_id: Optional[str] = Field(None, pattern=r'^[A-Z]{2,4}\d{3,4}$')
    document_type: DocumentType
    tags: Optional[List[str]] = Field(default_factory=list, max_items=10)
    collection: CollectionType = Field(default=CollectionType.GENERAL)
    custom_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    personal: Optional[PersonalMetadata] = Field(None, description="Personal KB metadata")

    @field_validator('tags')
    def validate_tags(cls, v):
        if v:
            for tag in v:
                if len(tag) > 50:
                    raise ValueError("Tag length must not exceed 50 characters")
                if not tag.replace('-', '').replace('_', '').isalnum():
                    raise ValueError("Tags must contain only alphanumeric characters, hyphens, and underscores")
        return v

    @model_validator(mode='after')
    def validate_personal_metadata(self):
        """Ensure personal metadata is present for personal collections"""
        if self.collection == CollectionType.PERSONAL and not self.personal:
            self.personal = PersonalMetadata()
        return self

class ProcessingStatus(BaseModel):
    """Document processing status model"""
    status: DocumentStatus
    message: Optional[str] = None
    error: Optional[str] = None
    progress: Optional[float] = Field(None, ge=0, le=100)
    started_at: datetime
    completed_at: Optional[datetime] = None

    @field_validator('completed_at')
    def validate_completion_time(cls, v, values):
        if v and 'started_at' in values and v < values['started_at']:
            raise ValueError("Completion time cannot be before start time")
        return v

class DocumentResponse(BaseResponse):
    """Document operation response model"""
    document_id: str = Field(..., description="Unique document identifier")
    status: DocumentStatus
    message: Optional[str] = None
    metadata: Optional[DocumentMetadata] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "document_id": "doc_123",
                "status": "completed",
                "message": "Document processed successfully",
                "metadata": {
                    "title": "Sample Document",
                    "author": "john_doe",
                    "document_type": "pdf",
                    "collection": "personal",
                    "course_id": "CS101",
                    "personal": {
                        "folder_path": "/study/algorithms",
                        "is_favorite": True,
                        "importance": 3,
                        "related_docs": ["doc_456", "doc_789"]
                    }
                },
                "timestamp": "2024-02-08T12:00:00Z"
            }
        }

class DocumentInfo(BaseModel):
    """Document information model with metadata and status"""
    document_id: str = Field(..., description="Unique document identifier")
    status: DocumentStatus
    metadata: DocumentMetadata
    error: Optional[str] = None

class DocumentListResponse(BaseResponse):
    """Response model for document list operations"""
    documents: List[DocumentInfo] = Field(..., description="List of documents")
    total: int = Field(..., description="Total number of documents")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "documents": [{
                    "document_id": "doc_123",
                    "status": "completed",
                    "metadata": {
                        "title": "Sample Document",
                        "author": "john_doe",
                        "document_type": "pdf",
                        "collection": "personal",
                        "course_id": "CS101",
                        "personal": {
                            "folder_path": "/study/algorithms",
                            "is_favorite": True,
                            "importance": 3,
                            "related_docs": ["doc_456", "doc_789"]
                        }
                    }
                }],
                "total": 1
            }
        }

class DocumentIndexTracker(BaseModel):
    """Document indexing tracking model"""
    document_id: str = Field(..., description="Unique document identifier")
    checksum: str = Field(..., description="Document content checksum")
    source_uri: str = Field(..., description="Original document URI/location")
    user_id: str = Field(..., description="User who requested indexing")
    document_type: DocumentType
    status: DocumentStatus
    indexed_at: Optional[datetime] = None
    last_checked: datetime = Field(default_factory=datetime.utcnow)
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

    class Config:
        json_schema_extra = {
            "example": {
                "document_id": "doc_123",
                "checksum": "sha256:abc123...",
                "source_uri": "personal/algorithms/lecture1.pdf",
                "user_id": "user_1",
                "document_type": "pdf",
                "status": "completed",
                "indexed_at": "2024-02-11T12:00:00Z",
                "last_checked": "2024-02-11T12:00:00Z",
                "metadata": {
                    "title": "Lecture 1",
                    "collection": "personal",
                    "personal": {
                        "folder_path": "/algorithms",
                        "importance": 3
                    }
                }
            }
        }

class DocumentIndexStatus(BaseResponse):
    """Document indexing status response"""
    document_id: str
    is_indexed: bool
    status: DocumentStatus
    indexed_at: Optional[datetime]
    last_checked: datetime
    checksum: str
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "document_id": "doc_123",
                "is_indexed": True,
                "status": "completed",
                "indexed_at": "2024-02-11T12:00:00Z",
                "last_checked": "2024-02-11T12:00:00Z",
                "checksum": "sha256:abc123...",
                "metadata": {
                    "title": "Lecture 1",
                    "collection": "personal",
                    "personal": {
                        "folder_path": "/algorithms",
                        "importance": 3
                    }
                }
            }
        } 