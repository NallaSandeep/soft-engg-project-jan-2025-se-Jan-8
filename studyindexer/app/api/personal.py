"""Personal knowledge base endpoints"""
from fastapi import APIRouter, HTTPException, Depends, Query, status
from typing import List, Optional
from app.core.auth import require_student, UserContext
from app.schemas.documents import (
    DocumentMetadata,
    DocumentResponse,
    DocumentListResponse,
    DocumentInfo,
    PersonalMetadata
)
from app.services.indexer import DocumentIndexer
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
indexer = DocumentIndexer()

@router.get(
    "/folders",
    response_model=List[str],
    dependencies=[Depends(require_student)]
)
async def list_folders(
    current_user: UserContext = Depends(require_student)
) -> List[str]:
    """List all folders in user's personal knowledge base"""
    try:
        # Search for all personal documents
        total_results, results = await indexer.search(
            query="",
            filters={
                "$and": [
                    {"collection": "personal"},
                    {"user_id": current_user.user_id}
                ]
            },
            limit=1000  # High limit to get all folders
        )
        
        # Extract unique folder paths
        folders = set()
        for result in results:
            if result.metadata.personal and result.metadata.personal.folder_path:
                # Split path and add all parent folders
                parts = result.metadata.personal.folder_path.strip('/').split('/')
                current_path = ""
                for part in parts:
                    current_path = f"{current_path}/{part}" if current_path else part
                    folders.add(current_path)
        
        return sorted(list(folders))
        
    except Exception as e:
        logger.error(f"Failed to list folders: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list folders"
        )

@router.get(
    "/documents",
    response_model=DocumentListResponse,
    dependencies=[Depends(require_student)]
)
async def list_documents(
    folder: Optional[str] = None,
    favorite: Optional[bool] = None,
    importance: Optional[int] = None,
    search: Optional[str] = None,
    tags: Optional[List[str]] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    current_user: UserContext = Depends(require_student)
) -> DocumentListResponse:
    """List documents in user's personal knowledge base with filtering"""
    try:
        # Build filters
        filters = {
            "$and": [
                {"collection": "personal"},
                {"user_id": current_user.user_id}
            ]
        }
        
        # Add optional filters
        if folder:
            filters["$and"].append({"personal.folder_path": folder})
        if favorite is not None:
            filters["$and"].append({"personal.is_favorite": favorite})
        if importance:
            filters["$and"].append({"personal.importance": importance})
        if tags:
            filters["$and"].append({"tags": {"$in": tags}})
            
        # Calculate offset
        offset = (page - 1) * page_size
        
        # Perform search
        total_results, results = await indexer.search(
            query=search or "",
            filters=filters,
            limit=page_size,
            offset=offset
        )
        
        # Process results
        seen_docs = set()
        documents = await process_document_results(results, seen_docs)
        
        return DocumentListResponse(
            documents=documents,
            total=total_results
        )
        
    except Exception as e:
        logger.error(f"Failed to list documents: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list documents"
        )

@router.patch(
    "/documents/{document_id}/metadata",
    response_model=DocumentResponse,
    dependencies=[Depends(require_student)]
)
async def update_metadata(
    document_id: str,
    metadata: PersonalMetadata,
    current_user: UserContext = Depends(require_student)
) -> DocumentResponse:
    """Update personal metadata for a document"""
    try:
        # Get current document status
        status = await indexer.get_document_status(document_id)
        if not status:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
            
        # Verify ownership
        if status["metadata"].get("user_id") != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to modify this document"
            )
            
        # Update metadata
        status["metadata"]["personal"] = metadata.model_dump()
        await indexer.update_document_metadata(document_id, status["metadata"])
        
        return DocumentResponse(
            document_id=document_id,
            status=status["status"],
            metadata=status["metadata"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update metadata: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update metadata"
        )

@router.get(
    "/documents/{document_id}/related",
    response_model=DocumentListResponse,
    dependencies=[Depends(require_student)]
)
async def get_related_documents(
    document_id: str,
    limit: int = Query(5, ge=1, le=20),
    current_user: UserContext = Depends(require_student)
) -> DocumentListResponse:
    """Get related documents for a personal document"""
    try:
        # Get document status
        status = await indexer.get_document_status(document_id)
        if not status:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
            
        # Get related document IDs
        related_ids = status["metadata"].get("personal", {}).get("related_docs", [])
        
        # Search for related documents
        if related_ids:
            filters = {
                "$and": [
                    {"document_id": {"$in": related_ids}},
                    {"user_id": current_user.user_id}
                ]
            }
            
            total_results, results = await indexer.search(
                query="",
                filters=filters,
                limit=limit
            )
            
            seen_docs = set()
            documents = await process_document_results(results, seen_docs)
            
            return DocumentListResponse(
                documents=documents,
                total=len(documents)
            )
        
        return DocumentListResponse(documents=[], total=0)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get related documents: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get related documents"
        )

async def process_document_results(results: List[dict], seen_docs: set) -> List[DocumentInfo]:
    """Helper function to process document search results"""
    documents = []
    for result in results:
        doc_id = result.metadata.get("document_id")
        if not doc_id or doc_id in seen_docs:
            continue
            
        seen_docs.add(doc_id)
        
        try:
            # Get document status
            status = await indexer.get_document_status(doc_id)
            
            # Create document info
            doc_info = DocumentInfo(
                document_id=doc_id,
                status=status["status"],
                metadata=DocumentMetadata(**status["metadata"]),
                error=status.get("error")
            )
            documents.append(doc_info)
        except Exception as e:
            logger.warning(f"Failed to get status for document {doc_id}: {str(e)}")
            continue
    
    return documents 