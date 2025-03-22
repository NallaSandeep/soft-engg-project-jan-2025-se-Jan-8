"""Application configuration."""
import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration."""
    
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    
    # SQLAlchemy
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///studyhub.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        seconds=int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 86400))
    )
    
    # File Upload
    UPLOAD_FOLDER = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads'))
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_FILE_EXTENSIONS = set(
        os.getenv('ALLOWED_FILE_EXTENSIONS', 'pdf,doc,docx,txt').split(',')
    )
    
    # CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')
    CORS_METHODS = os.getenv('CORS_METHODS', 'GET,POST,PUT,DELETE,OPTIONS').split(',')
    CORS_HEADERS = os.getenv('CORS_HEADERS', 'Content-Type,Authorization').split(',')
    CORS_SUPPORTS_CREDENTIALS = True
    
    # Server
    HOST = os.getenv('FLASK_HOST', '0.0.0.0')
    PORT = int(os.getenv('FLASK_PORT', 5000))

    # StudyIndexer Service
    INDEXER_SERVICE_URL = os.getenv('INDEXER_SERVICE_URL', 'http://localhost:8000')
    INDEXER_API_KEY = os.getenv('INDEXER_API_KEY', 'studyindexer_dev_api_key_2024')
    
    @staticmethod
    def init_app(app):
        """Initialize application."""
        # Ensure upload directory exists
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        
        # Configure CORS
        from flask_cors import CORS
        CORS(app, 
             resources={
                 r"/*": {
                     "origins": Config.CORS_ORIGINS,
                     "methods": Config.CORS_METHODS,
                     "allow_headers": Config.CORS_HEADERS,
                     "supports_credentials": Config.CORS_SUPPORTS_CREDENTIALS
                 }
             })

class DevelopmentConfig(Config):
    """Development configuration."""
    
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'sqlite:///' + os.path.join(os.path.dirname(__file__), 'studyhub.db')
    )

class TestingConfig(Config):
    """Testing configuration."""
    
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'TEST_DATABASE_URL',
        'sqlite:///' + os.path.join(os.path.dirname(__file__), 'test.db')
    )
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    """Production configuration."""
    
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    
    @classmethod
    def init_app(cls, app):
        """Production initialization."""
        Config.init_app(app)
        
        # Log to stderr
        import logging
        from logging import StreamHandler
        file_handler = StreamHandler()
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
} 