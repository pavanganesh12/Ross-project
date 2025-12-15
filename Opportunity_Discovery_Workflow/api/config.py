"""
API Configuration Settings.

Load configuration from environment variables with sensible defaults.
"""
import os
from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Settings
    api_title: str = "Opportunity Discovery API"
    api_version: str = "1.0.0"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_reload: bool = True
    api_workers: int = 1
    api_log_level: str = "info"
    
    # Environment
    environment: str = "development"
    debug: bool = False
    
    # Database
    database_path: str = "opportunity_discovery.db"
    
    # Keywords file path
    keywords_path: str = r"d:\Agno\keywords.json"
    
    # Outputs directory
    outputs_dir: str = "outputs"
    
    # OpenAI
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-5.1-2025-11-13"
    
    # SAM.gov
    sam_gov_api_key: Optional[str] = None
    
    # CORS
    cors_origins: str = "*"
    
    # Workflow settings
    default_days_back: int = 7
    max_days_back: int = 30
    batch_size: int = 10
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    
    Uses lru_cache to ensure settings are only loaded once.
    """
    return Settings()


# Export settings instance for convenience
settings = get_settings()
