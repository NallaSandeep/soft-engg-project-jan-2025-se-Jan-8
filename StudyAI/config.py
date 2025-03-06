"""Application configuration."""
import os
from typing import Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration settings for the application."""
    
    # Required environment variables
    REQUIRED_VARS = ['GEMINI_API_KEY', 'LANGSMITH_API_KEY']
    
    # API Keys
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    LANGSMITH_API_KEY = os.getenv('LANGSMITH_API_KEY')
    
    # LangSmith Configuration
    LANGSMITH_PROJECT = os.getenv('LANGSMITH_PROJECT', 'Agentic AI')
    LANGSMITH_TRACING = os.getenv('LANGSMITH_TRACING', 'true')
    
    # SQLAlchemy Configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///chatbot.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        """Get configuration value by key."""
        return getattr(cls, key.upper(), default)