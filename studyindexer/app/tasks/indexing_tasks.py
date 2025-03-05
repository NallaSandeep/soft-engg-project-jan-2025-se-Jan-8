"""Document processing functions"""
from app.services.indexer import DocumentIndexer
from app.core.background_tasks import document_tracker, DocumentStatus
from datetime import datetime, timedelta
import os
from app.core.config import settings
import asyncio
import logging

logger = logging.getLogger(__name__)

def process_document(document_id: str):
    """
    Process a document and index it in the vector store
    """
    try:
        logger.info(f"Processing document: {document_id}")
        
        # Initialize services
        indexer = DocumentIndexer()
        
        # Update document status
        document_tracker.update_status(
            document_id, 
            DocumentStatus.PROCESSING
        )
        
        # Use a new event loop for async operations
        loop = asyncio.new_event_loop()
        try:
            # Run the async process_document method
            result = loop.run_until_complete(indexer.process_document(document_id))
            
            # Check result
            if result and result.get("success", False):
                # Update document status with metadata
                document_tracker.update_status(
                    document_id, 
                    DocumentStatus.COMPLETED,
                    metadata=result.get("metadata", {})
                )
                logger.info(f"Document {document_id} processed successfully")
                return {"success": True, "document_id": document_id}
            else:
                # Update document status with error
                error_message = result.get("error", "Unknown error") if result else "Processing failed"
                document_tracker.update_status(
                    document_id, 
                    DocumentStatus.FAILED,
                    error=error_message
                )
                logger.error(f"Document {document_id} processing failed: {error_message}")
                return {"success": False, "document_id": document_id, "error": error_message}
        finally:
            # Always close the loop
            loop.close()
            
    except Exception as e:
        logger.exception(f"Error processing document {document_id}: {str(e)}")
        # Update document status with error
        document_tracker.update_status(
            document_id, 
            DocumentStatus.FAILED,
            error=str(e)
        )
        return {"success": False, "document_id": document_id, "error": str(e)}

def reindex_document(document_id: str):
    """
    Reindex a document in the vector store
    """
    try:
        logger.info(f"Reindexing document: {document_id}")
        
        # Initialize services
        indexer = DocumentIndexer()
        
        # Get document status
        doc_status = document_tracker.get_status(document_id)
        if not doc_status:
            logger.error(f"Document {document_id} not found for reindexing")
            return {"success": False, "document_id": document_id, "error": "Document not found"}
        
        # Update document status
        document_tracker.update_status(
            document_id, 
            DocumentStatus.PROCESSING
        )
        
        # Delete existing vectors if they exist
        vector_ids = doc_status.get("metadata", {}).get("vector_ids", [])
        if vector_ids:
            logger.info(f"Deleting existing vectors for document {document_id}")
            # Use a new event loop for async operations
            loop = asyncio.new_event_loop()
            try:
                loop.run_until_complete(indexer.delete_vectors(vector_ids))
            finally:
                loop.close()
        
        # Reindex the document
        loop = asyncio.new_event_loop()
        try:
            # Run the async index_document method
            result = loop.run_until_complete(indexer.index_document(document_id))
            
            # Check result
            if result and result.get("success", False):
                # Update document status with metadata
                document_tracker.update_status(
                    document_id, 
                    DocumentStatus.COMPLETED,
                    metadata=result.get("metadata", {})
                )
                logger.info(f"Document {document_id} reindexed successfully")
                return {"success": True, "document_id": document_id}
            else:
                # Update document status with error
                error_message = result.get("error", "Unknown error") if result else "Reindexing failed"
                document_tracker.update_status(
                    document_id, 
                    DocumentStatus.FAILED,
                    error=error_message
                )
                logger.error(f"Document {document_id} reindexing failed: {error_message}")
                return {"success": False, "document_id": document_id, "error": error_message}
        finally:
            # Always close the loop
            loop.close()
            
    except Exception as e:
        logger.exception(f"Error reindexing document {document_id}: {str(e)}")
        # Update document status with error
        document_tracker.update_status(
            document_id, 
            DocumentStatus.FAILED,
            error=str(e)
        )
        return {"success": False, "document_id": document_id, "error": str(e)}

def delete_document(document_id: str):
    """
    Delete a document from the vector store
    """
    try:
        logger.info(f"Deleting document: {document_id}")
        
        # Initialize services
        indexer = DocumentIndexer()
        
        # Get document status
        doc_status = document_tracker.get_status(document_id)
        if not doc_status:
            logger.error(f"Document {document_id} not found for deletion")
            return {"success": False, "document_id": document_id, "error": "Document not found"}
        
        # Delete vectors if they exist
        vector_ids = doc_status.get("metadata", {}).get("vector_ids", [])
        if vector_ids:
            logger.info(f"Deleting vectors for document {document_id}")
            # Use a new event loop for async operations
            loop = asyncio.new_event_loop()
            try:
                loop.run_until_complete(indexer.delete_vectors(vector_ids))
                logger.info(f"Vectors deleted for document {document_id}")
            except Exception as e:
                logger.error(f"Error deleting vectors for document {document_id}: {str(e)}")
            finally:
                loop.close()
        
        # Mark document as deleted in tracker
        document_tracker.delete_document(document_id)
        
        # Delete document file if it exists
        file_path = os.path.join(settings.UPLOAD_DIR, f"{document_id}")
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Document file deleted: {file_path}")
        
        return {"success": True, "document_id": document_id, "message": "Document deleted successfully"}
            
    except Exception as e:
        logger.exception(f"Error deleting document {document_id}: {str(e)}")
        return {"success": False, "document_id": document_id, "error": str(e)}

def cleanup_old_documents():
    """
    Cleanup old documents based on retention policy
    """
    try:
        logger.info("Starting document cleanup task")
        
        # Get all documents
        documents = document_tracker.list_documents()
        
        # Get retention period from settings (default 30 days)
        retention_days = getattr(settings, "DOCUMENT_RETENTION_DAYS", 30)
        retention_date = datetime.now() - timedelta(days=retention_days)
        
        # Initialize services
        indexer = DocumentIndexer()
        
        # Track cleanup stats
        deleted_count = 0
        failed_count = 0
        
        for doc in documents:
            try:
                # Skip if not completed or already deleted
                if doc.get("status") not in [DocumentStatus.COMPLETED, DocumentStatus.FAILED]:
                    continue
                
                # Check if document is older than retention period
                updated_at = doc.get("updated_at")
                if not updated_at:
                    continue
                
                # Convert timestamp to datetime
                if isinstance(updated_at, (int, float)):
                    doc_date = datetime.fromtimestamp(updated_at)
                else:
                    continue
                
                if doc_date < retention_date:
                    # Document is older than retention period, delete it
                    document_id = doc.get("document_id")
                    logger.info(f"Cleaning up old document: {document_id}")
                    
                    # Delete vectors if they exist
                    if "metadata" in doc and "vector_ids" in doc["metadata"]:
                        vector_ids = doc["metadata"]["vector_ids"]
                        if vector_ids:
                            # Use a new event loop
                            loop = asyncio.new_event_loop()
                            try:
                                loop.run_until_complete(indexer.delete_vectors(vector_ids))
                            finally:
                                loop.close()
                    
                    # Mark document as deleted in tracker
                    document_tracker.delete_document(document_id)
                    
                    # Delete document file if it exists
                    file_path = os.path.join(settings.UPLOAD_DIR, f"{document_id}")
                    if os.path.exists(file_path):
                        os.remove(file_path)
                    
                    deleted_count += 1
            except Exception as e:
                logger.error(f"Error cleaning up document {doc.get('document_id')}: {str(e)}")
                failed_count += 1
        
        logger.info(f"Document cleanup completed: {deleted_count} deleted, {failed_count} failed")
        return {
            "success": True, 
            "deleted_count": deleted_count, 
            "failed_count": failed_count
        }
        
    except Exception as e:
        logger.exception(f"Error in document cleanup task: {str(e)}")
        return {"success": False, "error": str(e)}

def check_stuck_tasks():
    """
    Check for stuck processing tasks and mark them as failed
    """
    try:
        logger.info("Checking for stuck processing tasks")
        
        # Get all documents with processing status
        processing_docs = document_tracker.list_documents(status=DocumentStatus.PROCESSING)
        
        # Get timeout period from settings (default 1 hour)
        timeout_hours = getattr(settings, "PROCESSING_TIMEOUT_HOURS", 1)
        timeout_time = datetime.now() - timedelta(hours=timeout_hours)
        
        # Track stats
        marked_failed = 0
        
        for doc in processing_docs:
            try:
                # Check if document has been processing for too long
                updated_at = doc.get("updated_at")
                if not updated_at:
                    continue
                
                # Convert timestamp to datetime
                if isinstance(updated_at, (int, float)):
                    doc_date = datetime.fromtimestamp(updated_at)
                else:
                    continue
                
                if doc_date < timeout_time:
                    # Document has been processing for too long, mark as failed
                    document_id = doc.get("document_id")
                    logger.warning(f"Document {document_id} has been processing for over {timeout_hours} hours, marking as failed")
                    
                    # Update document status
                    document_tracker.update_status(
                        document_id, 
                        DocumentStatus.FAILED,
                        error=f"Processing timed out after {timeout_hours} hours"
                    )
                    
                    marked_failed += 1
            except Exception as e:
                logger.error(f"Error checking document {doc.get('document_id')}: {str(e)}")
        
        logger.info(f"Stuck task check completed: {marked_failed} tasks marked as failed")
        return {"success": True, "marked_failed": marked_failed}
        
    except Exception as e:
        logger.exception(f"Error in stuck task check: {str(e)}")
        return {"success": False, "error": str(e)} 