"""
FAQ API endpoints for StudyIndexerNew
Based on the implementation specification in FAQ_Database_Implementation.md
"""
from fastapi import APIRouter, HTTPException, Depends, status, Query, UploadFile, File
from typing import List, Dict, Any, Optional
import time
import uuid
import tempfile
import os
import shutil

from ..models.faq import (
    FAQItem, 
    FAQCreateRequest, 
    FAQUpdateRequest, 
    FAQSearchQuery, 
    FAQSearchResponse,
    FAQSearchResult,
    JSONLImportResponse
)
from ..models.base import BaseResponse
from ..services.faq import FAQService

router = APIRouter()
faq_service = FAQService()

# Initialize FAQ service
@router.on_event("startup")
async def startup_db_client():
    await faq_service.initialize()

# Special routes that must be defined BEFORE the {faq_id} route
@router.get("/topics", response_model=BaseResponse)
async def get_topics():
    """Get all FAQ topics"""
    try:
        topics = await faq_service.get_topics()
        
        return BaseResponse(
            success=True,
            data={
                "topics": topics
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving FAQ topics: {str(e)}"
        )

@router.get("/sources", response_model=BaseResponse)
async def get_sources():
    """Get all FAQ sources"""
    try:
        sources = await faq_service.get_sources()
        
        return BaseResponse(
            success=True,
            data={
                "sources": sources
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving FAQ sources: {str(e)}"
        )

@router.post("/search", response_model=FAQSearchResponse)
async def search_faqs(query: FAQSearchQuery):
    """Search for FAQs based on the query"""
    try:
        total_results, results, query_time_ms = await faq_service.search_faqs(query)
        
        return FAQSearchResponse(
            success=True,
            results=results,
            query=query.query,
            total_results=total_results,
            query_time_ms=query_time_ms
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching FAQs: {str(e)}"
        )

@router.post("/add", response_model=BaseResponse)
async def add_faq(faq: FAQCreateRequest):
    """Add a new FAQ"""
    try:
        # Convert request to FAQItem
        faq_item = FAQItem(
            topic=faq.topic,
            question=faq.question,
            answer=faq.answer,
            tags=faq.tags,
            source=faq.source,
            is_published=faq.is_published,
            priority=faq.priority
        )
        
        # Use a placeholder user ID (in production this would come from auth)
        user_id = "system"
        
        # Add to database
        faq_id = await faq_service.add_faq(faq_item, user_id)
        
        return BaseResponse(
            success=True,
            message="FAQ added successfully",
            data={
                "id": faq_id,
                "question": faq.question,
                "topic": faq.topic
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error adding FAQ: {str(e)}"
        )

@router.post("/import", response_model=JSONLImportResponse)
async def import_jsonl(file: UploadFile = File(...)):
    """Import FAQs from a JSONL file"""
    if not file.filename.endswith('.jsonl'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file must be a JSONL file with .jsonl extension"
        )
    
    # Create a temporary file
    temp_dir = tempfile.mkdtemp()
    temp_file_path = os.path.join(temp_dir, file.filename)
    
    try:
        # Save the uploaded file
        with open(temp_file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
            
        # Use a placeholder user ID (in production this would come from auth)
        user_id = "system"
            
        # Process the file
        successful_imports, failed_imports = await faq_service.import_jsonl(temp_file_path, user_id)
        
        return JSONLImportResponse(
            success=True,
            total_imported=successful_imports,
            failed_items=failed_imports if failed_imports else None,
            message=f"Successfully imported {successful_imports} FAQs from {file.filename}"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error importing JSONL file: {str(e)}"
        )
    finally:
        # Clean up
        shutil.rmtree(temp_dir)

# Dynamic ID routes should be after specific routes to avoid conflicts
@router.get("/{faq_id}", response_model=BaseResponse)
async def get_faq(faq_id: str):
    """Get an FAQ by ID"""
    try:
        result = await faq_service.get_faq(faq_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"FAQ with ID {faq_id} not found"
            )
            
        return BaseResponse(
            success=True,
            data=result
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving FAQ: {str(e)}"
        )

@router.put("/{faq_id}", response_model=BaseResponse)
async def update_faq(faq_id: str, faq_update: FAQUpdateRequest):
    """Update an existing FAQ"""
    try:
        # Convert request to dict
        update_data = faq_update.model_dump(exclude_unset=True)
        
        # Update in database
        success = await faq_service.update_faq(faq_id, update_data)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"FAQ with ID {faq_id} not found"
            )
            
        return BaseResponse(
            success=True,
            message="FAQ updated successfully",
            data={
                "id": faq_id,
                "last_updated": time.time()
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating FAQ: {str(e)}"
        )

@router.delete("/{faq_id}", response_model=BaseResponse)
async def delete_faq(faq_id: str):
    """Delete an FAQ"""
    try:
        success = await faq_service.delete_faq(faq_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"FAQ with ID {faq_id} not found or could not be deleted"
            )
            
        return BaseResponse(
            success=True,
            message="FAQ deleted successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting FAQ: {str(e)}"
        ) 