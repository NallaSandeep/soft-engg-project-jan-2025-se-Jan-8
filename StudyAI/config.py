"""Application configuration."""

import os
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv
import logging

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class Config:
    """Configuration settings for the application."""

    # Required environment variables
    REQUIRED_VARS = ["GEMINI_API_KEY", "LANGSMITH_API_KEY"]

    # API Keys
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")

    # LangSmith Configuration
    LANGSMITH_PROJECT = os.getenv("LANGSMITH_PROJECT")
    LANGSMITH_TRACING = os.getenv("LANGSMITH_TRACING", "true").lower() == "true"

    # LangChain Configuration
    ENABLE_LANGCHAIN_CACHE = (
        os.getenv("ENABLE_LANGCHAIN_CACHE", "true").lower() == "true"
    )

    # SQLAlchemy Configuration
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # CORS Configuration
    CORS_ORIGINS: List[str] = os.getenv("CORS_ORIGINS", "*").split(",")

    # Rate Limiting Configuration
    RATE_LIMIT_ENABLED: bool = (
        os.getenv("RATE_LIMIT_ENABLED", "false").lower() == "true"
    )
    RATE_LIMIT: Optional[str] = os.getenv("RATE_LIMIT")

    # Server Configuration
    HOST = os.getenv("HOST")
    PORT = int(os.getenv("PORT", "5010"))
    
    # Study Indexer Configuration
    STUDY_INDEXER_PORT = os.getenv("STUDY_INDEXER_PORT", "8081")

    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        """Get configuration value by key."""
        return getattr(cls, key.upper(), default)

    @classmethod
    def validate_config(cls) -> Dict[str, bool]:
        """Validate that all required environment variables are set.

        Returns:
            Dict[str, bool]: Dictionary with validation results for each required variable
        """
        results = {}
        for var in cls.REQUIRED_VARS:
            value = cls.get(var)
            results[var] = value is not None and value != ""
            if not results[var]:
                logger.warning(f"Required configuration variable {var} is not set")
        return results

    @classmethod
    def is_valid(cls) -> bool:
        """Check if all required configuration is valid.

        Returns:
            bool: True if all required variables are set, False otherwise
        """
        return all(cls.validate_config().values())
