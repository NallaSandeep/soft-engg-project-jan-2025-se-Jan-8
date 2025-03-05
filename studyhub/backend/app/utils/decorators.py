"""Decorators for route protection and authorization"""
from functools import wraps
from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from app.models import User

def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user or user.role != 'admin':
            return jsonify({
                'success': False,
                'message': 'Admin access required'
            }), 403
        return f(*args, **kwargs)
    return decorated_function

def teacher_required(f):
    """Decorator to require teacher role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user or user.role not in ['admin', 'teacher']:
            return jsonify({
                'success': False,
                'message': 'Teacher access required'
            }), 403
        return f(*args, **kwargs)
    return decorated_function

def student_required(f):
    """Decorator to require student role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user or user.role not in ['admin', 'teacher', 'student']:
            return jsonify({
                'success': False,
                'message': 'Student access required'
            }), 403
        return f(*args, **kwargs)
    return decorated_function

def user_required(f):
    """Decorator to require authenticated user"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user or not user.is_active:
            return jsonify({
                'success': False,
                'message': 'Active user account required'
            }), 403
        return f(*args, **kwargs)
    return decorated_function

def course_access_required(f):
    """Decorator to require course access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        course_id = kwargs.get('course_id')
        
        # Admin and teachers have access to all courses
        if user.role in ['admin', 'teacher']:
            return f(*args, **kwargs)
            
        # Check if student is enrolled in the course
        if not any(e.course_id == course_id for e in user.course_enrollments):
            return jsonify({
                'success': False,
                'message': 'Course enrollment required'
            }), 403
            
        return f(*args, **kwargs)
    return decorated_function
