from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from ..models import User

def has_role(user, *roles):
    """Check if user has any of the specified roles.
    Admin role automatically has all permissions."""
    if not user:
        return False
    if user.role == 'admin':  # Admin has all permissions
        return True
    return user.role in roles

def roles_required(*roles):
    """Decorator to check if the current user has one of the required roles.
    Admin role automatically has all permissions."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            current_user = User.query.get(get_jwt_identity())
            
            if not current_user:
                return jsonify({'msg': 'User not found'}), 404
                
            if not has_role(current_user, *roles):
                return jsonify({
                    'success': False,
                    'message': f'Insufficient permissions. Required roles: {", ".join(roles)}'
                }), 403
                
            return fn(*args, **kwargs)
        return wrapper
    return decorator

def admin_required(fn):
    """Decorator to check if the current user is an admin."""
    return roles_required('admin')(fn)

def teacher_required(fn):
    """Decorator to check if the current user is a teacher."""
    return roles_required('teacher')(fn)

def ta_required(fn):
    """Decorator to check if the current user is a TA."""
    return roles_required('ta','admin')(fn)

def student_or_ta_required(fn):
    """Decorator to check if the current user is a student or TA."""
    return roles_required('student', 'ta')(fn)

def get_current_user():
    """Utility function to get the current user from JWT token."""
    try:
        current_user = User.query.get(get_jwt_identity())
        return current_user
    except:
        return None 