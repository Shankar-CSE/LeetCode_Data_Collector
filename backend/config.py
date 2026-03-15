"""
Centralized configuration management for the application.
"""
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration."""
    
    # MongoDB
    MONGODB_URI: str = os.getenv("MONGODB_URI", "")
    DB_NAME: str = os.getenv("DB_NAME", "leetcodedata")
    COLLECTION_VALID_USERS: str = os.getenv("COLLECTION_VALID_USERS", "validusers")
    COLLECTION_INVALID_USERS: str = os.getenv("COLLECTION_INVALID_USERS", "invalidusers")
    
    # Redis (Optional)
    REDIS_HOST: Optional[str] = os.getenv("REDIS_HOST")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", 6379))
    REDIS_USERNAME: Optional[str] = os.getenv("REDIS_USERNAME")
    REDIS_PASSWORD: Optional[str] = os.getenv("REDIS_PASSWORD")
    
    # API
    API_PORT: int = int(os.getenv("API_PORT", 8000))
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    
    # Application
    NODE_ENV: str = os.getenv("NODE_ENV", "development")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # LeetCode Scraper
    MAX_THREADS: int = int(os.getenv("MAX_THREADS", 20))
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", 15))
    CACHE_TTL: int = int(os.getenv("CACHE_TTL", 1800))
    
    # Validation
    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration."""
        if not cls.MONGODB_URI:
            raise ValueError("MONGODB_URI is required")
        return True


# Validate on import
Config.validate()
