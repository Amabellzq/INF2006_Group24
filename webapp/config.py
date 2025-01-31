# webapp/config.py
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Core
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret')
    DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'

    # Database
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{os.getenv('DB_USER' )}:{os.getenv('DB_PASSWORD')}"
        f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}"
        f"/{os.getenv('DB_NAME',)}"
    )
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'max_overflow': 20,
        'pool_recycle': 3600,
        'pool_pre_ping': True
    }
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY')
    DEBUG = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    # Security
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '').split(',')
    SESSION_COOKIE_SECURE = os.getenv('SESSION_SECURE', 'true') == 'true'


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    DEBUG = False