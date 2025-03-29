"""
Health check endpoints for the API
"""
from fastapi import APIRouter

router = APIRouter()

@router.get("")
@router.get("/")
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy"} 