from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from datetime import timedelta
import os
from config import Config
from .utils.errors import init_error_handlers
from .utils.logging import init_request_logging

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
cors = CORS()

def create_app(config_class=Config):
    """Create and configure the Flask application"""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config_class)
    
    # Disable strict slashes
    app.url_map.strict_slashes = False
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # Configure CORS - must be done before registering blueprints
    cors.init_app(app, resources={
        r"/api/*": {  # Match all API routes
            "origins": ["http://localhost:3000", "http://127.0.0.1:3000"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True,
            "expose_headers": ["Content-Type", "Authorization"]
        }
    })

    # Register blueprints
    from .api.v1 import api_v1_bp
    app.register_blueprint(api_v1_bp)
    
    # Initialize error handlers
    init_error_handlers(app)

    # Initialize request logging
    init_request_logging(app)
    
    from .models import User  # Add this import for JWT
    
    @jwt.user_identity_loader
    def user_identity_lookup(user):
        if isinstance(user, int):
            return str(user)
        return user

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        from .models import User  # Import here to avoid circular imports
        identity = jwt_data["sub"]
        try:
            return User.query.get(int(identity))
        except (ValueError, TypeError):
            return None

    # Create database tables
    with app.app_context():
        db.create_all()

    @app.route('/api/health')
    def health_check():
        """Health check endpoint"""
        return {'status': 'ok', 'message': 'StudyBot API is running'}

    return app 