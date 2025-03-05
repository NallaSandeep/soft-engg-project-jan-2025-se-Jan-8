"""Admin endpoints for StudyIndexer"""
from typing import List, Dict
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from fastapi import status as http_status
from app.core.auth import require_admin, UserContext
from app.core.errors import StudyIndexerError, DocumentNotFoundError
from app.schemas.documents import DocumentMetadata, DocumentResponse, DocumentListResponse, DocumentInfo
from app.schemas.admin import SystemStats, StorageStats, ProcessingStats, CollectionStats
from app.services.indexer import DocumentIndexer
from app.tasks.indexing_tasks import process_document, reindex_document
from app.core.config import settings
import logging
import os
from datetime import datetime

logger = logging.getLogger(__name__)
router = APIRouter()
indexer = DocumentIndexer()

def calculate_directory_size(directory: str) -> int:
    """Calculate total size of a directory in bytes"""
    total_size = 0
    try:
        for dirpath, _, filenames in os.walk(directory):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                try:
                    total_size += os.path.getsize(file_path)
                except (OSError, IOError) as e:
                    logger.warning(f"Failed to get size for {file_path}: {str(e)}")
    except (OSError, IOError) as e:
        logger.error(f"Failed to walk directory {directory}: {str(e)}")
    return total_size

@router.get("/documents", response_model=DocumentListResponse)
async def list_all_documents(
    current_user: UserContext = Depends(require_admin),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
) -> DocumentListResponse:
    """List all documents in the system (admin only)"""
    try:
        # Get all collections
        collections = await indexer.list_collections()
        all_documents = []
        
        # Search in each collection
        for collection in collections:
            try:
                # Get search results for this collection
                total_results, results = await indexer.search(
                    query="",  # Empty query to get all documents
                    collection=collection["name"],
                    limit=limit,
                    offset=offset,
                    filters={"chunk_index": 0}  # Only get first chunk of each document
                )
                
                if not results:
                    continue
                    
                # Process results for this collection
                for result in results:
                    try:
                        doc_id = result.metadata.get("document_id")
                        if not doc_id:
                            continue
                            
                        # Get document status
                        doc_status = await indexer.get_document_status(doc_id)
                            
                        # Convert to DocumentInfo
                        doc_info = DocumentInfo(
                            document_id=doc_id,
                            status=doc_status["status"],
                            metadata=DocumentMetadata(
                                title=result.metadata.get("title", "Untitled"),
                                author=result.metadata.get("author", "Unknown"),
                                course_id=result.metadata.get("course_id"),
                                document_type=result.metadata.get("document_type", "text"),
                                tags=result.metadata.get("tags", "").split(",") if result.metadata.get("tags") else [],
                                collection=result.metadata.get("collection", "general")
                            ),
                            error=doc_status.get("error")
                        )
                        all_documents.append(doc_info)
                    except Exception as e:
                        logger.warning(f"Failed to parse metadata for document: {str(e)}")
                        continue
                        
            except Exception as e:
                logger.warning(f"Failed to search collection {collection['name']}: {str(e)}")
                continue
        
        logger.info(
            "Admin document listing completed [user=%s, total=%d, limit=%d, offset=%d]",
            current_user.username,
            len(all_documents),
            limit,
            offset
        )
        
        return DocumentListResponse(
            success=True,
            documents=all_documents,
            total=len(all_documents)
        )
        
    except StudyIndexerError as e:
        logger.error(
            "StudyIndexer error during admin document listing [user=%s]: %s",
            current_user.username,
            str(e)
        )
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )
    except Exception as e:
        logger.error(
            "Failed to list all documents [user=%s]: %s",
            current_user.username,
            str(e)
        )
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list documents: {str(e)}"
        )

@router.get("/stats", response_model=SystemStats)
async def get_system_stats(current_user: UserContext = Depends(require_admin)) -> SystemStats:
    """Get system statistics (admin only)"""
    try:
        # Get collection statistics
        collections = await indexer.list_collections()
        total_documents = sum(col["document_count"] for col in collections)
        
        # Calculate storage usage
        upload_size = calculate_directory_size(settings.UPLOAD_DIR)
        chroma_size = calculate_directory_size(settings.CHROMA_PERSIST_DIR)
        total_size = upload_size + chroma_size
        
        # Get processing status counts
        status_files = os.listdir(settings.PROCESSED_DIR)
        status_counts = {"pending": 0, "processing": 0, "completed": 0, "failed": 0}
        total_processed = 0
        
        for status_file in status_files:
            if status_file.endswith(".json"):
                try:
                    doc_status = await indexer.get_document_status(
                        status_file.replace(".json", "")
                    )
                    status_counts[doc_status["status"]] += 1
                    total_processed += 1
                except Exception as e:
                    logger.warning(f"Failed to get status for {status_file}: {str(e)}")
                    continue
        
        # Convert collections to proper model
        collection_stats = [
            CollectionStats(
                name=col["name"],
                document_count=col["document_count"],
                metadata=col.get("metadata")
            )
            for col in collections
        ]
        
        return SystemStats(
            success=True,
            total_documents=total_documents,
            total_collections=len(collections),
            collections=collection_stats,
            storage_used=StorageStats(
                uploads=f"{upload_size / (1024*1024):.2f} MB",
                vectors=f"{chroma_size / (1024*1024):.2f} MB",
                total=f"{total_size / (1024*1024):.2f} MB",
                raw_total_bytes=total_size
            ),
            processing_status=ProcessingStats(
                pending=status_counts["pending"],
                processing=status_counts["processing"],
                completed=status_counts["completed"],
                failed=status_counts["failed"],
                total=total_processed
            ),
            embedding_model=settings.EMBEDDING_MODEL,
            embedding_device=settings.EMBEDDING_DEVICE,
            last_update=datetime.utcnow()
        )
        
    except StudyIndexerError as e:
        logger.error(
            "StudyIndexer error during system stats retrieval [user=%s]: %s",
            current_user.username,
            str(e)
        )
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )
    except Exception as e:
        logger.error(
            "Failed to get system stats [user=%s]: %s",
            current_user.username,
            str(e)
        )
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve system statistics: {str(e)}"
        )

@router.post("/reindex", response_model=DocumentResponse)
async def reindex_document(
    document_id: str,
    current_user: UserContext = Depends(require_admin),
    background_tasks: BackgroundTasks = BackgroundTasks()
) -> DocumentResponse:
    """Force reindex a specific document (admin only)"""
    try:
        # Verify document exists
        doc_status = await indexer.get_document_status(document_id)
        if not doc_status:
            raise HTTPException(
                status_code=404,
                detail=f"Document {document_id} not found"
            )
        
        # Start reindexing task
        background_tasks.add_task(reindex_document, document_id)
        
        logger.info(
            "Document reindexing initiated [id=%s, user=%s]",
            document_id,
            current_user.username
        )
        
        return DocumentResponse(
            success=True,
            document_id=document_id,
            status=DocumentStatus.PENDING,
            message="Document reindexing queued"
        )
        
    except DocumentNotFoundError:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    except StudyIndexerError as e:
        logger.error(
            "Failed to reindex document [id=%s, user=%s]: %s",
            document_id,
            current_user.username,
            str(e)
        )
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        ) 