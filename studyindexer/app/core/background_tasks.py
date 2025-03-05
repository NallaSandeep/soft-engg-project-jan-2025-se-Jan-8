"""Background task monitoring and logging utilities"""
import logging
import asyncio
import time
import uuid
import functools
import threading
from typing import Callable, Any, Dict, Optional, List, Union
import os
import shutil
from pathlib import Path

logger = logging.getLogger("studyindexer.background")

class DocumentStatus:
    """Document processing status constants"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    DELETED = "deleted"

class DocumentTracker:
    """Simple document status tracker"""
    
    def __init__(self):
        """Initialize the document tracker"""
        self.document_statuses: Dict[str, Dict[str, Any]] = {}
        logger.info("Document tracker initialized")
    
    def update_status(
        self, 
        document_id: str, 
        status: str, 
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Update the status of a document"""
        if document_id not in self.document_statuses:
            self.document_statuses[document_id] = {
                "status": status,
                "updated_at": time.time(),
                "error": error,
                "metadata": metadata or {}
            }
        else:
            self.document_statuses[document_id].update({
                "status": status,
                "updated_at": time.time()
            })
            
            if error is not None:
                self.document_statuses[document_id]["error"] = error
                
            if metadata is not None:
                if "metadata" not in self.document_statuses[document_id]:
                    self.document_statuses[document_id]["metadata"] = {}
                self.document_statuses[document_id]["metadata"].update(metadata)
        
        logger.info(f"Document {document_id} status updated to {status}")
    
    def get_status(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a document"""
        return self.document_statuses.get(document_id)
    
    def list_documents(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all documents, optionally filtered by status"""
        documents = []
        
        for doc_id, doc_info in self.document_statuses.items():
            if status is None or doc_info.get("status") == status:
                documents.append({
                    "document_id": doc_id,
                    **doc_info
                })
                
        return documents
    
    def delete_document(self, document_id: str) -> bool:
        """Mark a document as deleted"""
        if document_id in self.document_statuses:
            self.update_status(document_id, DocumentStatus.DELETED)
            return True
        return False

class BackgroundTaskManager:
    """Manager for background tasks with logging and monitoring"""
    
    def __init__(self):
        """Initialize the background task manager"""
        self.tasks: Dict[str, asyncio.Task] = {}
        logger.info("Background task manager initialized")
    
    async def create_task(
        self, 
        func: Callable, 
        *args, 
        task_name: Optional[str] = None, 
        **kwargs
    ) -> str:
        """Create and monitor a background task"""
        task_id = str(uuid.uuid4())
        task_name = task_name or func.__name__
        
        # Create a wrapper to log task execution
        @functools.wraps(func)
        async def task_wrapper():
            start_time = time.time()
            logger.info(f"Background task started [id={task_id}, name={task_name}]")
            
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                logger.info(
                    f"Background task completed [id={task_id}, name={task_name}], "
                    f"duration={duration:.3f}s"
                )
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(
                    f"Background task failed [id={task_id}, name={task_name}], "
                    f"error={str(e)}, duration={duration:.3f}s"
                )
                raise
            finally:
                # Remove task from tracking
                if task_id in self.tasks:
                    del self.tasks[task_id]
        
        # Create and store the task
        task = asyncio.create_task(task_wrapper())
        self.tasks[task_id] = task
        
        return task_id
    
    def add_task(self, func: Callable, *args, **kwargs) -> None:
        """
        Add a synchronous task to be executed in a separate thread.
        This is a compatibility method for FastAPI's background tasks.
        """
        task_name = func.__name__
        logger.info(f"Adding synchronous background task: {task_name}")
        
        def run_in_thread():
            start_time = time.time()
            logger.info(f"Background task started: {task_name}")
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                logger.info(f"Background task completed: {task_name}, duration={duration:.3f}s")
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"Background task failed: {task_name}, error={str(e)}, duration={duration:.3f}s")
                
        # Start the task in a separate thread
        thread = threading.Thread(target=run_in_thread)
        thread.daemon = True
        thread.start()
    
    def get_task(self, task_id: str) -> Optional[asyncio.Task]:
        """Get a background task by ID"""
        return self.tasks.get(task_id)
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a background task by ID"""
        task = self.tasks.get(task_id)
        if task and not task.done():
            task.cancel()
            logger.info(f"Background task cancelled [id={task_id}]")
            return True
        return False
    
    def get_active_tasks(self) -> Dict[str, str]:
        """Get all active background tasks"""
        return {
            task_id: task.get_name() 
            for task_id, task in self.tasks.items() 
            if not task.done()
        }
    
    def log_task_status(self):
        """Log the status of all tracked tasks"""
        active_tasks = len([t for t in self.tasks.values() if not t.done()])
        completed_tasks = len([t for t in self.tasks.values() if t.done() and not t.cancelled()])
        cancelled_tasks = len([t for t in self.tasks.values() if t.cancelled()])
        
        logger.info(
            f"Background task status: active={active_tasks}, "
            f"completed={completed_tasks}, cancelled={cancelled_tasks}"
        )

# Create singleton instances
background_task_manager = BackgroundTaskManager()
document_tracker = DocumentTracker() 

# Create an alias for compatibility with FastAPI's background tasks
background_tasks = background_task_manager 