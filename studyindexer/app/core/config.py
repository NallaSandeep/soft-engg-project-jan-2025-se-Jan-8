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
    PORT: int = Field(8080, env="PORT")
    
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "StudyIndexer"
    VERSION: str = Field("0.1.0", env="VERSION")
    
    # Security
    API_KEY_HEADER: str = "X-API-Key"
    API_KEY: str = Field("studyhub_dev_api_key_2024", env="API_KEY")
    CORS_ORIGINS: Set[str] = Field(default={"http://localhost:3000", "http://localhost:5100"}, env="CORS_ORIGINS")
    
    # JWT Settings
    JWT_SECRET: str = Field("studyhub_development_jwt_secret_key_32chars", env="JWT_SECRET")
    JWT_ALGORITHM: str = Field("HS256", env="JWT_ALGORITHM")
    JWT_TOKEN_PREFIX: str = Field("Bearer", env="JWT_TOKEN_PREFIX")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(1440, env="JWT_ACCESS_TOKEN_EXPIRE_MINUTES")  # 24 hours
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = Field(True, env="RATE_LIMIT_ENABLED")
    RATE_LIMIT_CALLS: int = Field(100, env="RATE_LIMIT_CALLS")
    RATE_LIMIT_PERIOD: int = Field(3600, env="RATE_LIMIT_PERIOD")  # in seconds
    
    # ChromaDB Settings
    CHROMA_HOST: str = Field("0.0.0.0", env="CHROMA_HOST")  # For binding
    CHROMA_CONNECT_HOST: str = Field("localhost", env="CHROMA_CONNECT_HOST")  # For connecting
    CHROMA_PORT: int = Field(8000, env="CHROMA_PORT")
    CHROMA_PERSIST_DIR: str = Field("./data/chroma", env="CHROMA_PERSIST_DIR")
    CHROMA_HEALTH_ENDPOINT: str = Field("/api/v1/heartbeat", env="CHROMA_HEALTH_ENDPOINT")
    
    # Document Processing
    MAX_CHUNK_SIZE: int = Field(1000, env="MAX_CHUNK_SIZE")
    CHUNK_OVERLAP: int = Field(200, env="CHUNK_OVERLAP")
    MAX_FILE_SIZE: int = Field(16777216, env="MAX_FILE_SIZE")  # 16MB
    MAX_UPLOAD_SIZE: int = Field(16777216, env="MAX_UPLOAD_SIZE")  # 16MB (same as MAX_FILE_SIZE)
    SUPPORTED_FILE_TYPES: Set[str] = Field(
        default={
            "application/pdf",
            "text/plain",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "text/markdown"
        },
        env="SUPPORTED_FILE_TYPES"
    )
    
    # Model Settings
    EMBEDDING_MODEL: str = Field("all-MiniLM-L6-v2", env="EMBEDDING_MODEL")
    EMBEDDING_DEVICE: str = Field("cpu", env="EMBEDDING_DEVICE")
    
    # Logging
    LOG_LEVEL: str = Field("INFO", env="LOG_LEVEL")
    LOG_FILE: str = Field("logs/app.log", env="LOG_FILE")
    LOG_FORMAT: str = Field("%(asctime)s - %(name)s - %(levelname)s - %(message)s", env="LOG_FORMAT")
    
    # Storage
    UPLOAD_DIR: str = Field("./uploads", env="UPLOAD_DIR")
    PROCESSED_DIR: str = Field("./data/processed", env="PROCESSED_DIR")
    TEMP_DIR: str = Field("./data/temp", env="TEMP_DIR")
    LOG_DIR: str = Field("./logs", env="LOG_DIR")
    
    # Health Check
    FASTAPI_HEALTH_ENDPOINT: str = Field("/api/health", env="FASTAPI_HEALTH_ENDPOINT")
    
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
        env_file=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), ".env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow",
        env_prefix=""
    )

# Create settings instance
settings = Settings()

# Ensure directories exist
settings.ensure_directories() 