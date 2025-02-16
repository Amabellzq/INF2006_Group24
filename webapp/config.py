import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Base Configuration for Flask App on AWS EC2 + RDS"""

    # Core Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'fallback-secret-key')  # Security fallback
    DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'

    # AWS RDS Database Configuration
    DB_USER = os.getenv('DB_USER')  # RDS Master username
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    DB_HOST = os.getenv('DB_HOST')  # AWS RDS endpoint
    DB_PORT = os.getenv('DB_PORT')
    DB_NAME = os.getenv('DB_NAME')

    # SQLAlchemy Database URI for MySQL on AWS RDS
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    # Ensure SSL handling for AWS RDS (if enabled)
    #if os.getenv('USE_SSL', 'false').lower() == 'true':
    #    SQLALCHEMY_DATABASE_URI += "?ssl_verify_cert=false"

    # SQLAlchemy Engine Options (Optimized for AWS RDS)
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,  # Max 10 persistent connections
        'max_overflow': 5,  # Allow up to 5 additional connections
        'pool_recycle': 1800,  # Reset idle connections every 30 minutes
        'pool_timeout': 15,  # Prevents app from hanging if pool is full
        'pool_pre_ping': True  # Detects stale connections before using
    }

    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Performance boost

    # Flask-Login & Session Management
    SESSION_TYPE = 'filesystem'  # Switch to 'redis' if needed
    SESSION_PERMANENT = True
    SESSION_USE_SIGNER = True  # Protects against cookie tampering
    SESSION_KEY_PREFIX = 'flask_'  # Avoids conflicts if using Redis

    # Security settings for Flask-Login sessions
    SESSION_COOKIE_SECURE = os.getenv('SESSION_SECURE', 'true').lower() == 'true'  # Should be True in production
    SESSION_COOKIE_HTTPONLY = True  # Prevents JavaScript access
    SESSION_COOKIE_SAMESITE = os.getenv('SESSION_SAMESITE', 'Lax')  # 'None' for OAuth, 'Lax' for security

    # Cross-Origin Resource Sharing (CORS) for API security
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
    CORS_SUPPORTS_CREDENTIALS = True  # Allow cookies in cross-origin requests

    # Logging Configuration for AWS EC2
    #LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')  # Can be DEBUG, INFO, WARNING, ERROR
    #LOG_FILE = os.getenv('LOG_FILE', '/var/log/flask-app.log')  # Store logs in EC2

    # Gunicorn Worker Settings (For AWS EC2)
    #GUNICORN_WORKERS = int(os.getenv('GUNICORN_WORKERS', '3'))  # Default: 3 workers


class DevelopmentConfig(Config):
    """Development Configuration"""
    DEBUG = True
    SQLALCHEMY_ECHO = True  # Log SQL statements for debugging
    SESSION_COOKIE_SECURE = False  # No HTTPS required for local development
    SESSION_COOKIE_SAMESITE = 'Lax'


class ProductionConfig(Config):
    """Production Configuration"""
    DEBUG = False
    SQLALCHEMY_ECHO = False  # Disable SQL logging for performance
    SESSION_COOKIE_SECURE = True  # Ensures cookies are sent only over HTTPS
    # SESSION_COOKIE_SAMESITE = 'Strict'  # Prevents CSRF (Cross-Site Request Forgery)
