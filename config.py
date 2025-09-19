import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-change-me-in-production'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD') or 'changeme'

class DevelopmentConfig(Config):
    DEBUG = True
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'sqlite:///blog.db'
    SQLALCHEMY_DATABASE_URI = DATABASE_URL

class ProductionConfig(Config):
    DEBUG = False
    # For Vercel, use environment variable or fallback to SQLite
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if not DATABASE_URL:
        # Vercel serverless doesn't persist files, use environment variable or in-memory
        if os.environ.get('VERCEL_URL'):
            DATABASE_URL = 'sqlite:///:memory:'
        else:
            DATABASE_URL = 'sqlite:///blog.db'
    SQLALCHEMY_DATABASE_URI = DATABASE_URL

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}