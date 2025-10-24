"""
Configuration settings for the FastAPI backend
"""

import os
from typing import Optional

class Settings:
    """Application settings"""
    
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "ÉpítAI Construction Management API"
    VERSION: str = "1.0.0"
    
    # Database
    DATABASE_URL: str = os.getenv('DATABASE_URL', 'postgresql://postgres:Cyrtoz-ziqrad-kummo8@db.idohoalwmovuewvcpqcn.supabase.co:5432/postgres')
    
    # SSL Configuration
    SSL_CERT_PATH: Optional[str] = os.getenv('SSL_CERT_PATH')
    SSL_KEY_PATH: Optional[str] = os.getenv('SSL_KEY_PATH')
    SSL_CA_PATH: Optional[str] = os.getenv('SSL_CA_PATH')
    SSL_MODE: str = os.getenv('SSL_MODE', 'require')
    
    # CORS
    BACKEND_CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost:8501",  # Streamlit default
    ]
    
    # Security
    SECRET_KEY: str = os.getenv('SECRET_KEY', 'your-secret-key-here')
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

settings = Settings()
