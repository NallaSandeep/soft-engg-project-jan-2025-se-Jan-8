"""Admin API schemas"""
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from app.schemas.base import BaseResponse

class StorageStats(BaseModel):
    """Storage usage statistics"""
    uploads: str = Field(..., description="Upload directory size")
    vectors: str = Field(..., description="Vector database size")
    total: str = Field(..., description="Total storage used")
    raw_total_bytes: int = Field(..., description="Total storage in bytes")

class ProcessingStats(BaseModel):
    """Document processing statistics"""
    pending: int = Field(0, description="Number of pending documents")
    processing: int = Field(0, description="Number of documents being processed")
    completed: int = Field(0, description="Number of completed documents")
    failed: int = Field(0, description="Number of failed documents")
    total: int = Field(..., description="Total number of documents")

class CollectionStats(BaseModel):
    """Collection statistics"""
    name: str = Field(..., description="Collection name")
    document_count: int = Field(..., description="Number of documents")
    metadata: Optional[Dict] = Field(None, description="Collection metadata")

class SystemStats(BaseResponse):
    """System statistics response"""
    total_documents: int = Field(..., description="Total number of documents")
    total_collections: int = Field(..., description="Number of collections")
    collections: List[CollectionStats] = Field(..., description="Collection statistics")
    storage_used: StorageStats = Field(..., description="Storage usage statistics")
    processing_status: ProcessingStats = Field(..., description="Processing statistics")
    embedding_model: str = Field(..., description="Current embedding model")
    embedding_device: str = Field(..., description="Current embedding device")
    last_update: datetime = Field(..., description="Last update timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "total_documents": 100,
                "total_collections": 5,
                "collections": [{
                    "name": "general",
                    "document_count": 50,
                    "metadata": {
                        "description": "General collection"
                    }
                }],
                "storage_used": {
                    "uploads": "100.5 MB",
                    "vectors": "50.2 MB",
                    "total": "150.7 MB",
                    "raw_total_bytes": 158063616
                },
                "processing_status": {
                    "pending": 5,
                    "processing": 2,
                    "completed": 90,
                    "failed": 3,
                    "total": 100
                },
                "embedding_model": "all-MiniLM-L6-v2",
                "embedding_device": "cpu",
                "last_update": "2024-02-11T12:00:00Z"
            }
        } 