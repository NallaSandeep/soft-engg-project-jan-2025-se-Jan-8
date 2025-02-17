"""Application configuration with environment support"""
from typing import Set, Dict, Any, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
import os
from pathlib import Path

class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Environment
    ENV: str = Field("development", env="APP_ENV")
    DEBUG: bool = Field(True, env="DEBUG")  # Default to True for development
    
    # Server Settings
    HOST: str = Field("0.0.0.0", env="HOST")
    PORT: int = Field(8000, env="PORT")
    
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "StudyIndexer"
    VERSION: str = "0.1.0"
    
    # Security
    API_KEY_HEADER: str = "X-API-Key"
    API_KEY: Optional[str] = Field(None, env="API_KEY")
    CORS_ORIGINS: Set[str] = Field(default={"http://localhost", "http://localhost:3000"})
    
    # JWT Settings
    JWT_SECRET: str = Field("development_jwt_secret_key_minimum_32_chars_long", env="JWT_SECRET")
    JWT_ALGORITHM: str = Field("HS256", env="JWT_ALGORITHM")
    JWT_TOKEN_PREFIX: str = Field("Bearer", env="JWT_TOKEN_PREFIX")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(30, env="JWT_ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_CALLS: int = Field(100, env="RATE_LIMIT_CALLS")
    RATE_LIMIT_PERIOD: int = Field(3600, env="RATE_LIMIT_PERIOD")  # in seconds
    
    # ChromaDB Settings
    CHROMA_HOST: str = Field("localhost", env="CHROMA_HOST")
    CHROMA_PORT: int = Field(8000, env="CHROMA_PORT")
    CHROMA_PERSIST_DIR: str = Field("./data/chroma", env="CHROMA_PERSIST_DIR")
    
    # Document Processing
    MAX_CHUNK_SIZE: int = Field(1000, env="MAX_CHUNK_SIZE")
    CHUNK_OVERLAP: int = Field(200, env="CHUNK_OVERLAP")
    MAX_FILE_SIZE: int = Field(16777216, env="MAX_FILE_SIZE")  # 16MB
    MAX_UPLOAD_SIZE: int = Field(16777216, env="MAX_UPLOAD_SIZE")  # 16MB (same as MAX_FILE_SIZE)
    SUPPORTED_FILE_TYPES: Set[str] = {
        "application/pdf",
        "text/plain",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "text/markdown"
    }
    
    # Model Settings
    EMBEDDING_MODEL: str = Field("all-MiniLM-L6-v2", env="EMBEDDING_MODEL")
    EMBEDDING_DEVICE: str = Field("cpu", env="EMBEDDING_DEVICE")
    
    # Logging
    LOG_LEVEL: str = Field("INFO", env="LOG_LEVEL")
    LOG_FILE: str = Field("app.log", env="LOG_FILE")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Redis Settings (Updated for WSL)
    REDIS_HOST: str = Field("localhost", env="REDIS_HOST")  # WSL Redis is accessible via localhost
    REDIS_PORT: int = Field(6379, env="REDIS_PORT")
    REDIS_DB: int = Field(0, env="REDIS_DB")
    REDIS_PASSWORD: Optional[str] = Field(None, env="REDIS_PASSWORD")
    
    # Celery Settings (Updated for WSL)
    CELERY_BROKER_URL: str = Field("redis://localhost:6379/0", env="CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND: str = Field("redis://localhost:6379/0", env="CELERY_RESULT_BACKEND")
    
    # Storage
    UPLOAD_DIR: str = Field("./data/uploads", env="UPLOAD_DIR")
    PROCESSED_DIR: str = Field("./data/processed", env="PROCESSED_DIR")
    TEMP_DIR: str = Field("./data/temp", env="TEMP_DIR")
    LOG_DIR: str = Field("./logs", env="LOG_DIR")
    
    @field_validator("ENV")
    def validate_env(cls, v: str) -> str:
        """Validate environment setting"""
        allowed_envs = {"development", "testing", "production"}
        if v not in allowed_envs:
            raise ValueError(f"ENV must be one of {allowed_envs}")
        return v
    
    @field_validator("EMBEDDING_DEVICE")
    def validate_embedding_device(cls, v: str) -> str:
        """Validate embedding device setting"""
        allowed_devices = {"cpu", "cuda"}
        if v not in allowed_devices:
            raise ValueError(f"EMBEDDING_DEVICE must be one of {allowed_devices}")
        return v
    
    @field_validator("LOG_LEVEL")
    def validate_log_level(cls, v: str) -> str:
        """Validate log level setting"""
        allowed_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if v.upper() not in allowed_levels:
            raise ValueError(f"LOG_LEVEL must be one of {allowed_levels}")
        return v.upper()
    
    @field_validator("JWT_SECRET")
    def validate_jwt_secret(cls, v: str) -> str:
        """Validate JWT secret key"""
        if not v or len(v) < 32:
            raise ValueError("JWT_SECRET must be at least 32 characters long")
        return v
    
    @field_validator("MAX_FILE_SIZE", mode="before")
    def validate_max_file_size(cls, v: Any) -> int:
        """Convert and validate max file size"""
        if isinstance(v, str):
            # Remove any comments and whitespace
            v = v.split('#')[0].strip()
        try:
            return int(v)
        except (ValueError, TypeError):
            raise ValueError("MAX_FILE_SIZE must be a valid integer")
    
    def get_redis_url(self) -> str:
        """Get Redis URL with optional password"""
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    def ensure_directories(self) -> None:
        """Ensure all required directories exist"""
        dirs = [
            self.UPLOAD_DIR,
            self.PROCESSED_DIR,
            self.TEMP_DIR,
            self.LOG_DIR,
            self.CHROMA_PERSIST_DIR
        ]
        for dir_path in dirs:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow",
        env_prefix=""
    )

# Create settings instance
settings = Settings()

# Ensure directories exist
settings.ensure_directories() 