import logging
import time
from flask import request, g
import json
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('studybot')

def init_request_logging(app):
    """Initialize request logging middleware"""
    
    @app.before_request
    def before_request():
        """Log request details and start timer"""
        g.start_time = time.time()
        
        # Log request details
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'method': request.method,
            'path': request.path,
            'query_params': dict(request.args),
            'headers': dict(request.headers),
            'source_ip': request.remote_addr
        }
        
        # Log request body for POST/PUT/PATCH requests
        if request.is_json and request.method in ['POST', 'PUT', 'PATCH']:
            # Mask sensitive data
            body = request.get_json()
            if isinstance(body, dict):
                masked_body = body.copy()
                sensitive_fields = ['password', 'token', 'api_key']
                for field in sensitive_fields:
                    if field in masked_body:
                        masked_body[field] = '***MASKED***'
                log_data['body'] = masked_body
        
        logger.info(f"Request: {json.dumps(log_data)}")

    @app.after_request
    def after_request(response):
        """Log response details and timing"""
        duration = time.time() - g.start_time
        
        # Log response details
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'method': request.method,
            'path': request.path,
            'status_code': response.status_code,
            'duration_ms': round(duration * 1000, 2),
            'response_size': len(response.get_data()),
            'content_type': response.content_type
        }
        
        # Log level based on status code
        if response.status_code >= 500:
            logger.error(f"Response: {json.dumps(log_data)}")
        elif response.status_code >= 400:
            logger.warning(f"Response: {json.dumps(log_data)}")
        else:
            logger.info(f"Response: {json.dumps(log_data)}")
        
        return response

    @app.errorhandler(Exception)
    def log_exception(error):
        """Log unhandled exceptions"""
        logger.exception("Unhandled exception occurred")
        raise error  # Re-raise the exception for the error handler 