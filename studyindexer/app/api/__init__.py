"""
API package
"""
from fastapi import APIRouter
from app.api import admin, documents, search, personal

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