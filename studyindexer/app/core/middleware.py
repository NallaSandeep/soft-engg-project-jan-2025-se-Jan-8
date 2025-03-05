"""Middleware for request logging and monitoring"""
import time
import logging
import json
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import uuid

logger = logging.getLogger("studyindexer.api")

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging request and response details"""
    
    async def dispatch(self, request: Request, call_next):
        """Process the request, log details, and pass to the next middleware"""
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Extract request details
        client_host = request.client.host if request.client else "unknown"
        method = request.method
        url = str(request.url)
        
        # Get request headers (excluding sensitive information)
        headers = dict(request.headers)
        if "authorization" in headers:
            headers["authorization"] = "Bearer [FILTERED]"
        if "x-api-key" in headers:
            headers["x-api-key"] = "[FILTERED]"
            
        # Log request start
        logger.info(
            f"Request started [id={request_id}]: {method} {url} from {client_host}"
        )
        
        # Process request and measure time
        start_time = time.time()
        
        try:
            # Get request body for non-GET requests (if not a file upload)
            body = None
            if method != "GET" and not url.endswith("/upload"):
                try:
                    body_bytes = await request.body()
                    if body_bytes:
                        body = body_bytes.decode()
                        # Try to parse as JSON for better logging
                        try:
                            body_json = json.loads(body)
                            # Filter out sensitive fields
                            if isinstance(body_json, dict):
                                if "password" in body_json:
                                    body_json["password"] = "[FILTERED]"
                                if "token" in body_json:
                                    body_json["token"] = "[FILTERED]"
                            body = json.dumps(body_json)
                        except json.JSONDecodeError:
                            # Not JSON, use as is
                            pass
                except Exception as e:
                    logger.warning(f"Failed to read request body: {str(e)}")
            
            if body:
                logger.debug(f"Request body [id={request_id}]: {body}")
            
            # Call next middleware/endpoint
            response = await call_next(request)
            
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Log response
            status_code = response.status_code
            logger.info(
                f"Request completed [id={request_id}]: {method} {url} - "
                f"Status: {status_code}, Time: {process_time:.3f}s"
            )
            
            return response
            
        except Exception as e:
            # Log exception
            process_time = time.time() - start_time
            logger.error(
                f"Request failed [id={request_id}]: {method} {url} - "
                f"Error: {str(e)}, Time: {process_time:.3f}s"
            )
            raise 