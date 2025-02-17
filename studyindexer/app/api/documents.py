"""Document management endpoints for StudyIndexer"""
from typing import List, Tuple, Optional
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status, Query
from app.core.auth import require_teacher, require_student, UserContext, get_current_user
from app.core.errors import (
    DocumentNotFoundError,
    InvalidFileTypeError,
    FileSizeTooLargeError,
    StudyIndexerError,
    ValidationError
)
from app.schemas.documents import DocumentMetadata, DocumentResponse, DocumentListResponse, DocumentInfo, DocumentStatus
from app.schemas.base import DocumentType, CollectionType
from app.services.indexer import DocumentIndexer
from app.core.config import settings
from app.tasks.indexing_tasks import process_document
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
indexer = DocumentIndexer()

async def process_document_results(results: List[dict], seen_docs: set) -> List[DocumentInfo]:
    """Helper function to process document search results into DocumentInfo objects"""
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
                status=DocumentStatus(status["status"]),
                metadata=DocumentMetadata(
                    title=status["metadata"].get("title", "Untitled"),
                    author=status["metadata"].get("author", "Unknown"),
                    course_id=status["metadata"].get("course_id"),
                    document_type=status["metadata"].get("document_type", "text"),
                    tags=status["metadata"].get("tags", []),
                    collection=status["metadata"].get("collection", "general"),
                    custom_metadata=status["metadata"].get("custom_metadata", {})
                ),
                error=status.get("error")
            )
            documents.append(doc_info)
        except Exception as e:
            logger.warning(f"Failed to get status for document {doc_id}: {str(e)}")
            continue
    
    return documents

@router.post("/", response_model=DocumentResponse)
async def index_document(
    file: UploadFile = File(...),
    title: str = Query(None),
    course_id: str = Query(None),
    document_type: DocumentType = Query(DocumentType.TEXT),
    tags: str = Query(None),
    collection: CollectionType = Query(CollectionType.GENERAL),
    current_user: UserContext = Depends(get_current_user)
):
    """
    Index a new document in the vector store.
    The actual indexing happens in a Celery task.
    """
    try:
        # Process tags if provided
        tag_list = []
        if tags:
            tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()]

        # Create metadata
        metadata = DocumentMetadata(
            title=title or file.filename,
            course_id=course_id,
            document_type=document_type,
            tags=tag_list,
            collection=collection
        )

        document_id = indexer.prepare_document(
            file=file, 
            metadata=metadata,
            user_id=current_user.user_id
        )
        # Start Celery task
        task = process_document.delay(document_id)
        
        return DocumentResponse(
            document_id=document_id,
            status="processing",
            message=f"Document queued for indexing (task: {task.id})"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get(
    "/my",
    response_model=DocumentListResponse,
    dependencies=[Depends(require_teacher)]
)
async def list_my_documents(
    current_user: UserContext = Depends(require_teacher)
) -> DocumentListResponse:
    """List all documents uploaded by the current user"""
    try:
        # Search for documents with author filter
        total_results, results = await indexer.search(
            query="",  # Empty query to get all documents
            filters={"user_id": current_user.user_id},  # Use user_id instead of id
            limit=100  # Reasonable limit for user's documents
        )
        
        # Process results
        seen_docs = set()
        documents = []
        
        # Use the helper function to process results
        documents = await process_document_results(results, seen_docs)
        
        return DocumentListResponse(
            documents=documents,
            total=len(documents)
        )
        
    except Exception as e:
        logger.error(f"Failed to list documents for user {current_user.user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve documents"
        )

@router.get(
    "/course/{course_id}",
    response_model=DocumentListResponse,
    dependencies=[Depends(require_student)]
)
async def list_course_documents(
    course_id: str,
    current_user: UserContext = Depends(require_student)
) -> DocumentListResponse:
    """List all documents for a specific course"""
    try:
        # Search for documents with course filter
        total_results, results = await indexer.search(
            query="",  # Empty query to get all documents
            filters={"course_id": course_id},
            limit=100  # Reasonable limit for course documents
        )
        
        # Process results using helper function
        seen_docs = set()
        documents = await process_document_results(results, seen_docs)
        
        return DocumentListResponse(
            documents=documents,
            total=len(documents)
        )
        
    except Exception as e:
        logger.error(f"Failed to list course documents [course={course_id}, user={current_user.user_id}]: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve course documents"
        )

@router.delete("/{document_id}")
async def delete_document(document_id: str):
    """
    Delete a document from the vector store
    """
    try:
        indexer.delete_document(document_id)
        return {"message": f"Document {document_id} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document_status(document_id: str):
    """
    Get the indexing status of a document
    """
    try:
        status = indexer.get_document_status(document_id)
        return DocumentResponse(
            document_id=document_id,
            status=status["status"],
            message=status.get("message", ""),
            metadata=status.get("metadata")
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e)) 