"""Document tracking service"""
import hashlib
import json
import os
import aiofiles
from datetime import datetime
from typing import Optional, Dict, Any
import logging
from app.core.config import settings
from app.core.errors import StudyIndexerError
from app.schemas.documents import DocumentIndexTracker, DocumentStatus
from app.utils.redis import get_redis_client

logger = logging.getLogger(__name__)

# Global instance for singleton
_tracker_instance = None

class DocumentTracker:
    """Service for tracking document indexing status"""
    
    def __new__(cls):
        global _tracker_instance
        if _tracker_instance is None:
            instance = super(DocumentTracker, cls).__new__(cls)
            instance._initialized = False
            _tracker_instance = instance
        return _tracker_instance
    
    def __init__(self):
        """Initialize document tracker"""
        if getattr(self, '_initialized', False):
            return
            
        self.tracking_dir = os.path.join(settings.PROCESSED_DIR, "tracking")
        os.makedirs(self.tracking_dir, exist_ok=True)
        self.redis = get_redis_client()
        self._initialized = True
    
    async def compute_checksum(self, file_content: bytes) -> str:
        """Compute SHA-256 checksum of file content"""
        return f"sha256:{hashlib.sha256(file_content).hexdigest()}"
    
    async def get_tracking_path(self, document_id: str) -> str:
        """Get path to tracking file"""
        return os.path.join(self.tracking_dir, f"{document_id}.track.json")
    
    async def track_document(
        self,
        document_id: str,
        file_content: bytes,
        source_uri: str,
        user_id: str,
        document_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> DocumentIndexTracker:
        """Create or update document tracking"""
        try:
            checksum = await self.compute_checksum(file_content)
            tracking_path = await self.get_tracking_path(document_id)
            
            # Check if document already exists
            existing_tracker = await self.get_document_status(document_id)
            if existing_tracker and existing_tracker.checksum == checksum:
                # Document exists and hasn't changed
                existing_tracker.last_checked = datetime.utcnow()
                async with aiofiles.open(tracking_path, 'w') as f:
                    await f.write(existing_tracker.model_dump_json(indent=2))
                return existing_tracker
            
            # Create new tracking record
            tracker = DocumentIndexTracker(
                document_id=document_id,
                checksum=checksum,
                source_uri=source_uri,
                user_id=user_id,
                document_type=document_type,
                status=DocumentStatus.PENDING,
                metadata=metadata or {}
            )
            
            # Save tracking info
            async with aiofiles.open(tracking_path, 'w') as f:
                await f.write(tracker.model_dump_json(indent=2))
            
            logger.info(
                "Document tracking created [id=%s, checksum=%s]",
                document_id,
                checksum
            )
            return tracker
            
        except Exception as e:
            logger.error(
                "Failed to track document %s: %s",
                document_id,
                str(e)
            )
            raise StudyIndexerError(
                message=f"Failed to track document: {str(e)}",
                code="TRACKING_ERROR"
            )
    
    def update_status(
        self,
        document_id: str,
        status: DocumentStatus,
        error: Optional[str] = None
    ):
        """Update document processing status"""
        key = f"doc:{document_id}:status"
        data = {
            "status": status.value,
            "updated_at": datetime.now().isoformat(),
        }
        if error:
            data["error"] = error
            
        self.redis.set(key, json.dumps(data))
        return data
    
    async def get_document_status(
        self,
        document_id: str
    ) -> Optional[DocumentIndexTracker]:
        """Get document tracking status"""
        try:
            tracking_path = await self.get_tracking_path(document_id)
            if not os.path.exists(tracking_path):
                return None
                
            async with aiofiles.open(tracking_path, 'r') as f:
                content = await f.read()
                data = json.loads(content)
                return DocumentIndexTracker(**data)
                
        except Exception as e:
            logger.error(
                "Failed to get document status %s: %s",
                document_id,
                str(e)
            )
            return None
    
    async def delete_tracking(self, document_id: str) -> None:
        """Delete document tracking"""
        try:
            tracking_path = await self.get_tracking_path(document_id)
            if os.path.exists(tracking_path):
                os.remove(tracking_path)
                logger.info("Document tracking deleted [id=%s]", document_id)
        except Exception as e:
            logger.error(
                "Failed to delete document tracking %s: %s",
                document_id,
                str(e)
            )
            raise StudyIndexerError(
                message=f"Failed to delete document tracking: {str(e)}",
                code="TRACKING_DELETE_ERROR"
            ) 