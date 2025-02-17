"""Search endpoints for StudyIndexer"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from app.core.auth import require_student, UserContext, get_current_user
from app.core.errors import StudyIndexerError, SearchError
from app.schemas.documents import DocumentMetadata
from app.schemas.base import CollectionType
from app.schemas.search import (
    SearchQuery,
    SearchResult,
    SearchResponse,
    PaginationMetadata
)
from app.services.indexer import DocumentIndexer
import logging
import time
import math

logger = logging.getLogger(__name__)
router = APIRouter()
indexer = DocumentIndexer()

@router.post(
    "/",
    response_model=SearchResponse,
    dependencies=[Depends(require_student)]
)
async def search_documents(
    query: SearchQuery,
    current_user: UserContext = Depends(require_student)
) -> SearchResponse:
    """Search for documents"""
    try:
        # Prepare filters
        filters = query.filters or {}
        
        # Add course access filter for students
        if current_user.role not in ["admin", "teacher"]:
            course_filter = {"$or": [
                {"course_id": {"$in": current_user.courses}},
                {"course_id": None}  # Include documents without course
            ]}
            filters = {"$and": [filters, course_filter]} if filters else course_filter
        
        # Prepare collection name
        collection_name = query.collection.value if isinstance(query.collection, CollectionType) else "general"
        
        # Calculate offset for pagination
        offset = (query.page - 1) * query.page_size
        
        start_time = time.time()
        
        # Perform search
        total_results, results = await indexer.search(
            query=query.text,
            offset=offset,
            limit=query.page_size,
            filters=filters,
            collection=collection_name,
            min_score=query.min_score
        )
        
        query_time = (time.time() - start_time) * 1000
        
        # Calculate pagination metadata
        total_pages = math.ceil(total_results / query.page_size)
        
        logger.info(
            "Search completed [query=%s, user=%s, results=%d, time=%.2fms]",
            query.text,
            current_user.username,
            len(results),
            query_time
        )
        
        return SearchResponse(
            success=True,
            results=results,
            pagination=PaginationMetadata(
                current_page=query.page,
                page_size=query.page_size,
                total_pages=total_pages,
                total_results=total_results,
                has_next=query.page < total_pages,
                has_previous=query.page > 1
            ),
            query_time_ms=query_time,
            collection=collection_name,
            filters_applied=filters
        )
        
    except Exception as e:
        logger.error(
            "Search failed [query=%s, user=%s]: %s",
            query.text,
            current_user.username,
            str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get(
    "/similar/{document_id}",
    response_model=SearchResponse,
    dependencies=[Depends(require_student)]
)
async def find_similar_documents(
    document_id: str,
    limit: int = Query(5, ge=1, le=50),
    min_score: float = Query(0.5, ge=0.0, le=1.0),
    current_user: UserContext = Depends(require_student)
) -> SearchResponse:
    """Find documents similar to the given document"""
    try:
        start_time = time.time()
        
        # Get document metadata
        doc_status = await indexer.get_document_status(document_id)
        
        # Check course access if document is course-specific and user is not admin/teacher
        metadata = doc_status.get("metadata", {})
        course_id = metadata.get("course_id")
        if course_id and current_user.role not in ["admin", "teacher"] and course_id not in current_user.courses:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enrolled in this course"
            )
        
        # Get collection name
        collection = metadata.get("collection", "general")
        
        # Get document content
        total_results, results = await indexer.search(
            query="",  # Empty query to get document content
            filters={"document_id": document_id},
            collection=collection,
            limit=1
        )
        
        if not results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
            
        # Use first chunk's content as query
        query_text = results[0].content
        
        # Prepare filters for similar documents
        filters = {}
        if current_user.role not in ["admin", "teacher"]:
            # For students, filter by their enrolled courses
            if current_user.courses:
                # Create individual course conditions
                course_filters = []
                for course_id in current_user.courses:
                    if course_id:  # Skip empty course IDs
                        course_filters.append({"course_id": course_id})
                
                # Add condition for public documents (no course_id)
                course_filters.append({"course_id": ""})  # Using empty string instead of None
                
                if len(course_filters) > 1:
                    filters = {"$or": course_filters}
                else:
                    filters = course_filters[0] if course_filters else {"course_id": ""}
            else:
                # If user has no courses, only show public documents
                filters = {"course_id": ""}
        
        # Search for similar documents
        total_results, similar_docs = await indexer.search(
            query=query_text,
            limit=limit + 1,  # Get one extra to exclude source document
            collection=collection,
            min_score=min_score,
            filters=filters
        )
        
        # Filter out the source document and limit results
        filtered_docs = [
            doc for doc in similar_docs 
            if doc.document_id != document_id
        ][:limit]
        
        query_time = (time.time() - start_time) * 1000
        
        return SearchResponse(
            success=True,
            results=filtered_docs,
            pagination=PaginationMetadata(
                current_page=1,
                page_size=limit,
                total_pages=1,
                total_results=len(filtered_docs),
                has_next=False,
                has_previous=False
            ),
            query_time_ms=query_time,
            collection=collection,
            filters_applied=filters
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during similarity search [document={document_id}, user={current_user.user_id}]: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to find similar documents"
        )