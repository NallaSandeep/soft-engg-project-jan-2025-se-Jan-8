"""Error handling and custom exceptions"""
from typing import Any, Dict, Optional
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
import logging

logger = logging.getLogger(__name__)

class StudyIndexerError(Exception):
    """Base exception for StudyIndexer service"""
    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_ERROR",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

class InvalidDocumentError(StudyIndexerError):
    """Raised when a document is invalid or unsupported"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="INVALID_DOCUMENT",
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details
        )

class DocumentProcessingError(StudyIndexerError):
    """Raised when there is an error processing a document"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="DOCUMENT_PROCESSING_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details
        )

class DocumentNotFoundError(StudyIndexerError):
    """Raised when a document is not found"""
    def __init__(self, document_id: str):
        super().__init__(
            message=f"Document {document_id} not found",
            code="DOCUMENT_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"document_id": document_id}
        )

class InvalidFileTypeError(StudyIndexerError):
    """Raised when an unsupported file type is uploaded"""
    def __init__(self, file_type: str):
        super().__init__(
            message=f"Unsupported file type: {file_type}",
            code="INVALID_FILE_TYPE",
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"file_type": file_type}
        )

class FileSizeTooLargeError(StudyIndexerError):
    """Raised when uploaded file exceeds size limit"""
    def __init__(self, file_size: int, max_size: int):
        super().__init__(
            message=f"File size ({file_size} bytes) exceeds maximum allowed size ({max_size} bytes)",
            code="FILE_TOO_LARGE",
            status_code=status.HTTP_400_BAD_REQUEST,
            details={
                "file_size": file_size,
                "max_size": max_size
            }
        )

class AuthenticationError(StudyIndexerError):
    """Raised when authentication fails"""
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            message=message,
            code="AUTHENTICATION_ERROR",
            status_code=status.HTTP_401_UNAUTHORIZED
        )

class AuthorizationError(StudyIndexerError):
    """Raised when user lacks required permissions"""
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(
            message=message,
            code="AUTHORIZATION_ERROR",
            status_code=status.HTTP_403_FORBIDDEN
        )

class ValidationError(StudyIndexerError):
    """Raised when request validation fails"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details
        )

class SearchError(StudyIndexerError):
    """Raised when search operation fails"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="SEARCH_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details
        )

async def error_handler(request: Request, call_next):
    """Global error handling middleware"""
    try:
        return await call_next(request)
        
    except StudyIndexerError as e:
        logger.error(
            "Application error: %s [code=%s, details=%s]",
            e.message,
            e.code,
            e.details
        )
        return JSONResponse(
            status_code=e.status_code,
            content={
                "success": False,
                "message": e.message,
                "error": {
                    "code": e.code,
                    "details": e.details
                }
            }
        )
        
    except RequestValidationError as e:
        logger.error("Validation error: %s", str(e))
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "success": False,
                "message": "Validation error",
                "error": {
                    "code": "VALIDATION_ERROR",
                    "details": e.errors()
                }
            }
        )
        
    except Exception as e:
        logger.exception("Unexpected error")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "message": "Internal server error",
                "error": {
                    "code": "INTERNAL_ERROR",
                    "details": {"error": str(e)} if str(e) else None
                }
            }
        ) 