import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # Core settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'fallback-secret-key')  # Fallback for security
    DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'

    # AWS RDS Database Configuration
    DB_USER = os.getenv('DB_USER', 'default_user')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'default_password')
    DB_HOST = os.getenv('DB_HOST', 'localhost')  # AWS RDS endpoint
    DB_PORT = os.getenv('DB_PORT', '3306')
    DB_NAME = os.getenv('DB_NAME', 'default_db')

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    # Additional AWS RDS Settings (Optional)
    if os.getenv('USE_SSL', 'false').lower() == 'true':
        SQLALCHEMY_DATABASE_URI += "?ssl_verify_cert=false"  # ✅ Ensure SSL handling for RDS

    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 20,        # ✅ Max number of persistent connections
        'max_overflow': 10,     # ✅ Extra connections allowed in bursts
        'pool_recycle': 1800,   # ✅ Recycles connections every 30 minutes
        'pool_timeout': 15,     # ✅ Prevents app from hanging if pool is full
        'pool_pre_ping': True   # ✅ Detects stale connections before using
    }

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # CORS Configuration
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')

    # Security Settings
    SESSION_COOKIE_SECURE = os.getenv('SESSION_SECURE', 'true').lower() == 'true'


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_ECHO = False
