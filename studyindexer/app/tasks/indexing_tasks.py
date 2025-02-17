"""Celery tasks for document processing"""
from app.core.celery_app import celery_app
from app.services.indexer import DocumentIndexer
from app.services.tracker import DocumentTracker
from app.schemas.documents import DocumentStatus
from celery.utils.log import get_task_logger
from datetime import datetime, timedelta
import os
from app.core.config import settings

logger = get_task_logger(__name__)

@celery_app.task(
    bind=True,
    name="app.tasks.indexing_tasks.process_document",
    queue="indexing",
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 3, 'countdown': 60}
)
def process_document(self, document_id: str):
    """
    Celery task to process and index a document
    """
    try:
        logger.info(f"Starting document processing for {document_id}")
        
        # Initialize services (lazy initialization)
        indexer = DocumentIndexer()
        tracker = DocumentTracker()
        
        # Update tracking status
        tracker.update_status(
            document_id=document_id,
            status=DocumentStatus.PROCESSING
        )
        
        # Process document
        indexer.index_document(document_id)
        
        # Update tracking status
        tracker.update_status(
            document_id=document_id,
            status=DocumentStatus.COMPLETED
        )
        
        logger.info(f"Document {document_id} processed successfully")
        return {"status": "success", "document_id": document_id}
        
    except Exception as e:
        logger.error(f"Error processing document {document_id}: {str(e)}")
        
        # Update tracking status with error
        tracker = DocumentTracker()  # Re-initialize in case of error
        tracker.update_status(
            document_id=document_id,
            status=DocumentStatus.FAILED,
            error=str(e)
        )
        
        # Retry if possible
        raise self.retry(exc=e)

@celery_app.task(
    bind=True,
    name="app.tasks.indexing_tasks.reindex_document",
    queue="indexing",
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 3, 'countdown': 60}
)
def reindex_document(self, document_id: str):
    """
    Celery task to reindex an existing document
    """
    try:
        logger.info(f"Starting document reindexing for {document_id}")
        
        # Initialize services (lazy initialization)
        indexer = DocumentIndexer()
        tracker = DocumentTracker()
        
        # Update tracking status
        tracker.update_status(
            document_id=document_id,
            status=DocumentStatus.PROCESSING
        )
        
        # Delete existing vectors
        indexer.delete_document(document_id)
        
        # Reindex document
        indexer.index_document(document_id)
        
        # Update tracking status
        tracker.update_status(
            document_id=document_id,
            status=DocumentStatus.COMPLETED
        )
        
        logger.info(f"Document {document_id} reindexed successfully")
        return {"status": "success", "document_id": document_id}
        
    except Exception as e:
        logger.error(f"Error reindexing document {document_id}: {str(e)}")
        
        # Update tracking status with error
        tracker = DocumentTracker()  # Re-initialize in case of error
        tracker.update_status(
            document_id=document_id,
            status=DocumentStatus.FAILED,
            error=str(e)
        )
        
        # Retry if possible
        raise self.retry(exc=e)

@celery_app.task(
    name="app.tasks.indexing_tasks.delete_document",
    queue="maintenance"
)
def delete_document(document_id: str):
    """
    Celery task to delete a document and its tracking
    """
    try:
        logger.info(f"Deleting document {document_id}")
        
        # Initialize services (lazy initialization)
        indexer = DocumentIndexer()
        tracker = DocumentTracker()
        
        # Delete from vector store
        indexer.delete_document(document_id)
        
        # Delete tracking
        tracker.delete_tracking(document_id)
        
        logger.info(f"Document {document_id} deleted successfully")
        return {"status": "success", "document_id": document_id}
        
    except Exception as e:
        logger.error(f"Error deleting document {document_id}: {str(e)}")
        raise

@celery_app.task(
    name="app.tasks.indexing_tasks.cleanup_documents",
    queue="maintenance"
)
def cleanup_old_documents():
    """
    Periodic task to clean up old processed documents
    """
    try:
        logger.info("Starting document cleanup")
        
        # Initialize services (lazy initialization)
        indexer = DocumentIndexer()
        
        # Get list of processed documents
        processed_dir = os.path.join(settings.PROCESSED_DIR)
        for filename in os.listdir(processed_dir):
            if not filename.endswith('.json'):
                continue
                
            document_id = filename.replace('.json', '')
            
            try:
                # Get document status
                status = indexer.get_document_status(document_id)
                
                # Check if document is old and failed
                if (
                    status and
                    status["status"] == "failed" and
                    datetime.fromisoformat(status["upload_time"]) < datetime.utcnow() - timedelta(days=7)
                ):
                    logger.info(f"Cleaning up old failed document {document_id}")
                    delete_document.delay(document_id)
                    
            except Exception as e:
                logger.warning(f"Error checking document {document_id}: {str(e)}")
                continue
        
        logger.info("Document cleanup completed")
        
    except Exception as e:
        logger.error(f"Error during document cleanup: {str(e)}")
        raise

@celery_app.task(
    name="app.tasks.indexing_tasks.check_stuck_tasks",
    queue="maintenance"
)
def check_stuck_tasks():
    """
    Periodic task to check for stuck processing tasks
    """
    try:
        logger.info("Checking for stuck tasks")
        
        # Initialize services (lazy initialization)
        indexer = DocumentIndexer()
        
        # Get list of processing documents
        processed_dir = os.path.join(settings.PROCESSED_DIR)
        for filename in os.listdir(processed_dir):
            if not filename.endswith('.json'):
                continue
                
            document_id = filename.replace('.json', '')
            
            try:
                # Get document status
                status = indexer.get_document_status(document_id)
                
                # Check if document is stuck in processing
                if (
                    status and
                    status["status"] == "processing" and
                    datetime.fromisoformat(status["upload_time"]) < datetime.utcnow() - timedelta(hours=1)
                ):
                    logger.warning(f"Found stuck document {document_id}, requeueing")
                    process_document.delay(document_id)
                    
            except Exception as e:
                logger.warning(f"Error checking document {document_id}: {str(e)}")
                continue
        
        logger.info("Stuck task check completed")
        
    except Exception as e:
        logger.error(f"Error checking stuck tasks: {str(e)}")
        raise 