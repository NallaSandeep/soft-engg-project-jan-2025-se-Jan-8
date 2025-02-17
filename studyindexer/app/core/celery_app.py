"""Celery application configuration"""
from celery import Celery
from celery.schedules import crontab
import os
import sys
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

# Configure Celery application
celery_app = Celery(
    "studyindexer",
    broker=settings.get_redis_url(),
    backend=settings.get_redis_url(),
    include=['app.tasks.indexing_tasks']
)

# Configure Celery
celery_app.conf.update(
    # Core Settings
    broker_connection_retry=True,
    broker_connection_max_retries=10,
    broker_connection_timeout=30,
    
    # Worker Settings
    worker_concurrency=1,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=10,
    worker_max_memory_per_child=512000,  # 512MB
    
    # Task Settings
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    task_track_started=True,
    task_time_limit=3600,
    task_soft_time_limit=3000,
    task_acks_late=True,
    
    # Queue Settings
    task_queues={
        'indexing': {
            'exchange': 'indexing',
            'routing_key': 'indexing'
        },
        'maintenance': {
            'exchange': 'maintenance',
            'routing_key': 'maintenance'
        }
    },
    
    # Task Routing
    task_routes={
        'app.tasks.indexing_tasks.*': {'queue': 'indexing'},
        'app.tasks.maintenance_tasks.*': {'queue': 'maintenance'}
    },
    
    # Scheduled Tasks
    beat_schedule={
        'cleanup-old-documents': {
            'task': 'app.tasks.indexing_tasks.cleanup_documents',
            'schedule': crontab(hour=2, minute=0),
            'options': {'queue': 'maintenance'}
        },
        'check-stuck-tasks': {
            'task': 'app.tasks.indexing_tasks.check_stuck_tasks',
            'schedule': crontab(minute='*/15'),
            'options': {'queue': 'maintenance'}
        }
    },
    
    # Time Settings
    timezone='UTC',
    enable_utc=True,
    
    # Result Settings
    result_expires=86400  # 24 hours
)

# Development Settings
if settings.DEBUG:
    celery_app.conf.update(
        task_always_eager=False,
        worker_log_color=True,
        worker_redirect_stdouts=True,
        worker_redirect_stdouts_level='INFO'
    )

# Import tasks to ensure they're registered
import app.tasks.indexing_tasks  # noqa

logger.info("Celery application configured with broker: %s", settings.get_redis_url()) 