from flask import jsonify
from werkzeug.exceptions import HTTPException
import traceback

class APIError(Exception):
    """Base class for API errors"""
    def __init__(self, message, status_code=400, errors=None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.errors = errors

    def to_dict(self):
        response = {
            'success': False,
            'message': self.message
        }
        if self.errors:
            response['errors'] = self.errors
        return response

class ValidationError(APIError):
    """Validation error"""
    def __init__(self, message="Invalid input", errors=None):
        super().__init__(message, status_code=400, errors=errors)

class AuthenticationError(APIError):
    """Authentication error"""
    def __init__(self, message="Authentication failed"):
        super().__init__(message, status_code=401)

class AuthorizationError(APIError):
    """Authorization error"""
    def __init__(self, message="Permission denied"):
        super().__init__(message, status_code=403)

class NotFoundError(APIError):
    """Resource not found error"""
    def __init__(self, message="Resource not found"):
        super().__init__(message, status_code=404)

class ConflictError(APIError):
    """Resource conflict error"""
    def __init__(self, message="Resource already exists"):
        super().__init__(message, status_code=409)

def handle_api_error(error):
    """Handle custom API errors"""
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

def handle_404_error(error):
    """Handle 404 errors"""
    return jsonify({
        'success': False,
        'message': 'Resource not found'
    }), 404

def handle_500_error(error):
    """Handle 500 errors"""
    # Log the full error traceback
    traceback.print_exc()
    return jsonify({
        'success': False,
        'message': 'Internal server error'
    }), 500

def init_error_handlers(app):
    """Initialize error handlers for the app"""
    app.register_error_handler(APIError, handle_api_error)
    app.register_error_handler(404, handle_404_error)
    app.register_error_handler(500, handle_500_error)
    
    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        """Handle any unexpected errors"""
        # Log the full error traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': 'An unexpected error occurred'
        }), 500

def success_response(data=None, message="Success", status_code=200):
    """Create a standardized success response"""
    response = {
        'success': True,
        'message': message
    }
    if data is not None:
        response['data'] = data
    return jsonify(response), status_code

def error_response(message="Error", errors=None, status_code=400):
    """Create a standardized error response"""
    response = {
        'success': False,
        'message': message
    }
    if errors:
        response['errors'] = errors
    return jsonify(response), status_code 