"""
API package
"""
from fastapi import APIRouter, Depends, HTTPException
from app.core.auth import get_current_user
from app.services.chroma import ChromaService
import logging
from datetime import datetime
from app.api import admin, documents, search, personal

logger = logging.getLogger(__name__)

# Create API router
router = APIRouter()

# Include sub-routers
router.include_router(
    admin.router,
    prefix="/admin",
    tags=["admin"]
)

router.include_router(
    documents.router,
    prefix="/documents",
    tags=["documents"]
)

router.include_router(
    search.router,
    prefix="/search",
    tags=["search"]
)

router.include_router(
    personal.router,
    prefix="/personal",
    tags=["personal"]
)

@router.get("/heartbeat")
async def chroma_heartbeat(current_user = Depends(get_current_user)):
    """Proxy endpoint for ChromaDB heartbeat"""
    try:
        chroma_service = ChromaService()
        chroma_service._ensure_connection()
        return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}
    except Exception as e:
        logger.error(f"ChromaDB heartbeat check failed: {str(e)}")
        raise HTTPException(status_code=500, detail="ChromaDB service is not responding") 