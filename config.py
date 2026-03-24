import os
from dotenv import load_dotenv
import sys

load_dotenv()

class Config:
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(32).hex()
    
    # Database configuration - PostgreSQL for production (Render)
    DATABASE_URL = os.environ.get('DATABASE_URL')
    
    if not DATABASE_URL:
        print("WARNING: DATABASE_URL not set! Using SQLite fallback.", file=sys.stderr)
        print("For production, set DATABASE_URL environment variable.", file=sys.stderr)
        SQLALCHEMY_DATABASE_URI = 'sqlite:///gas_masters.db'
    else:
        # Render PostgreSQL - fix the URL if needed
        if DATABASE_URL.startswith('postgres://'):
            DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
        print(f"Using database: {SQLALCHEMY_DATABASE_URI.split('@')[0]}@...", file=sys.stderr)
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_size': 10,
        'max_overflow': 20
    }
    
    # Session security
    SESSION_COOKIE_SECURE = os.environ.get('FLASK_ENV') == 'production'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour
    
    # CSRF Protection
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None
    
    # Application settings
    LOW_INVENTORY_THRESHOLD = 100
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file upload