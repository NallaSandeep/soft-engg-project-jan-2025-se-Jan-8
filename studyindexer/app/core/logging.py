"""Logging configuration"""
import logging
import logging.handlers
import sys
import os
from pathlib import Path
from app.core.config import settings

def setup_logging() -> None:
    """Configure application logging"""
    
    # Create logs directory if it doesn't exist
    log_dir = Path(os.path.abspath(settings.LOG_DIR))
    log_dir.mkdir(parents=True, exist_ok=True)
    
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
    
    # Ensure log files exist
    log_files = [
        "info.log",
        "error.log",
        "api.log"
    ]
    
    for log_file in log_files:
        log_path = log_dir / log_file
        try:
            if not log_path.exists():
                with open(log_path, 'a'):
                    pass
        except Exception as e:
            print(f"Warning: Could not create log file {log_path}: {str(e)}")
    
    # File handlers
    info_handler = logging.handlers.RotatingFileHandler(
        filename=f"{log_dir}/info.log",
        maxBytes=10485760,  # 10MB
        backupCount=5,
        encoding="utf-8"
    )
    info_handler.setFormatter(file_formatter)
    info_handler.setLevel(logging.INFO)
    
    error_handler = logging.handlers.RotatingFileHandler(
        filename=f"{log_dir}/error.log",
        maxBytes=10485760,  # 10MB
        backupCount=5,
        encoding="utf-8"
    )
    error_handler.setFormatter(file_formatter)
    error_handler.setLevel(logging.ERROR)
    
    # Create specialized log handlers
    api_handler = logging.handlers.RotatingFileHandler(
        filename=f"{log_dir}/api.log",
        maxBytes=10485760,  # 10MB
        backupCount=5,
        encoding="utf-8"
    )
    api_handler.setFormatter(file_formatter)
    api_handler.setLevel(logging.INFO)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(settings.LOG_LEVEL)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(info_handler)
    root_logger.addHandler(error_handler)
    
    # Create application logger
    app_logger = logging.getLogger("studyindexer")
    app_logger.setLevel(settings.LOG_LEVEL)
    
    # Create specialized loggers
    api_logger = logging.getLogger("studyindexer.api")
    api_logger.setLevel(settings.LOG_LEVEL)
    api_logger.addHandler(api_handler)
    
    # Explicitly flush handlers to avoid BrokenPipeError
    for handler in root_logger.handlers:
        handler.flush()
    for handler in app_logger.handlers:
        handler.flush()
    for handler in api_logger.handlers:
        handler.flush()

    # Log startup message
    app_logger.info(
        "Starting StudyIndexer service [Version: %s, Environment: %s]",
        settings.VERSION,
        settings.ENV
    ) 