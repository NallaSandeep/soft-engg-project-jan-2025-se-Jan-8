"""Logging configuration"""
import logging
import logging.handlers
import sys
from pathlib import Path
from app.core.config import settings

def setup_logging() -> None:
    """Configure application logging"""
    
    # Create logs directory if it doesn't exist
    Path(settings.LOG_DIR).mkdir(parents=True, exist_ok=True)
    
    # Create formatters
    console_formatter = logging.Formatter(
        '%(levelname)s: %(message)s'
    )
    file_formatter = logging.Formatter(
        settings.LOG_FORMAT
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(logging.INFO)
    
    # File handlers
    info_handler = logging.handlers.RotatingFileHandler(
        filename=f"{settings.LOG_DIR}/info.log",
        maxBytes=10485760,  # 10MB
        backupCount=5,
        encoding="utf-8"
    )
    info_handler.setFormatter(file_formatter)
    info_handler.setLevel(logging.INFO)
    
    error_handler = logging.handlers.RotatingFileHandler(
        filename=f"{settings.LOG_DIR}/error.log",
        maxBytes=10485760,  # 10MB
        backupCount=5,
        encoding="utf-8"
    )
    error_handler.setFormatter(file_formatter)
    error_handler.setLevel(logging.ERROR)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(settings.LOG_LEVEL)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(info_handler)
    root_logger.addHandler(error_handler)
    
    # Create application logger
    app_logger = logging.getLogger("studyindexer")
    app_logger.setLevel(settings.LOG_LEVEL)
    
    # Log startup message
    app_logger.info(
        "Starting StudyIndexer service [Version: %s, Environment: %s]",
        settings.VERSION,
        settings.ENV
    ) 