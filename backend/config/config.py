# =============================================================================
# backend/config/config.py
# Centralized Environment-Based Configuration System
# =============================================================================

import os
from dotenv import load_dotenv

# Load variables from .env if present
load_dotenv()

class Config:
    """Base Configuration"""
    SECRET_KEY = os.getenv("SECRET_KEY", "prod-session-key-active-recall")
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "uploads")
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", 20 * 1024 * 1024))  # Default 20 MB
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Database Settings (PostgreSQL ready, SQLite fallback)
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "sqlite:///" + os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(__file__))), "app.db")
    )
    
    # Storage Settings (Local filesystem or AWS S3 upload bucket)
    STORAGE_PROVIDER = os.getenv("STORAGE_PROVIDER", "local").lower()  # 'local' or 's3'
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
    S3_BUCKET = os.getenv("S3_BUCKET")
    
    # Authentication Settings (Firebase or AWS Cognito)
    AUTH_PROVIDER = os.getenv("AUTH_PROVIDER", "firebase").lower()  # 'firebase' or 'cognito'
    COGNITO_USER_POOL_ID = os.getenv("COGNITO_USER_POOL_ID")
    COGNITO_CLIENT_ID = os.getenv("COGNITO_CLIENT_ID")
    COGNITO_REGION = os.getenv("COGNITO_REGION", "us-east-1")


class DevelopmentConfig(Config):
    """Development Configuration"""
    DEBUG = True


class ProductionConfig(Config):
    """Production Configuration"""
    DEBUG = False
    # In production, check if PostgreSQL configuration is active
    # For Heroku or AWS Beanstalk, DATABASE_URL might start with 'postgres://' which SQLAlchemy 1.4+ rejects (needs 'postgresql://')
    DATABASE_URL = os.getenv("DATABASE_URL")
    if DATABASE_URL:
        if DATABASE_URL.startswith("postgres://"):
            SQLALCHEMY_DATABASE_URI = DATABASE_URL.replace("postgres://", "postgresql://", 1)
        else:
            SQLALCHEMY_DATABASE_URI = DATABASE_URL


# Configuration mapping
config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig
}
