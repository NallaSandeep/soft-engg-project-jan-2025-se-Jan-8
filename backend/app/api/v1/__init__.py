"""API v1 Blueprint Package"""

from flask import Blueprint
from .auth import auth_bp
from .courses import courses_bp
from .assignments import assignments_bp
from .users import users_bp
from .resources import resources_bp
from .question_bank import question_bank_bp
from .admin import admin_bp

api_v1_bp = Blueprint('api_v1', __name__, url_prefix='/api/v1')

# Register blueprints
api_v1_bp.register_blueprint(auth_bp, url_prefix='/auth')
api_v1_bp.register_blueprint(courses_bp, url_prefix='/courses')
api_v1_bp.register_blueprint(assignments_bp)
api_v1_bp.register_blueprint(users_bp, url_prefix='/users')
api_v1_bp.register_blueprint(resources_bp, url_prefix='/resources')
api_v1_bp.register_blueprint(question_bank_bp, url_prefix='/question-bank')
api_v1_bp.register_blueprint(admin_bp, url_prefix='/admin')

__all__ = [
    'auth_bp',
    'users_bp',
    'courses_bp',
    'resources_bp',
    'assignments_bp',
    'question_bank_bp',
    'admin_bp'
] 