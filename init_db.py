#!/usr/bin/env python3
"""
Database initialization script for production deployment
"""
import os
from app import create_app, db

def init_db():
    """Initialize database tables"""
    app = create_app()
    with app.app_context():
        # Create all tables
        db.create_all()
        print("✅ Database tables created successfully!")
        
        # Run seed data
        from app import seed_if_empty
        seed_if_empty()
        print("✅ Initial data seeded!")

if __name__ == '__main__':
    init_db()