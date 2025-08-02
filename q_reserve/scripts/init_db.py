#!/usr/bin/env python3
"""
Database initialization script for Q-Reserve.

This script creates all database tables and sets up the initial database structure.
"""

import os
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import current_app
from core.extensions import db
from core.factory import create_app


def init_database():
    """Initialize the database with all tables."""
    
    print("Initializing Q-Reserve database...")
    
    # Create all tables
    db.create_all()
    
    # Create upload directories
    create_upload_directories()
    
    # Install pgvector extension if using PostgreSQL
    install_pgvector_extension()
    
    print("Database initialization completed successfully!")


def create_upload_directories():
    """Create necessary upload directories."""
    
    upload_dirs = [
        'static/uploads',
        'static/uploads/attachments',
        'static/uploads/avatars',
        'static/uploads/temp'
    ]
    
    for directory in upload_dirs:
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            print(f"Created directory: {directory}")
            
            # Create .gitkeep file
            gitkeep_path = os.path.join(directory, '.gitkeep')
            with open(gitkeep_path, 'w') as f:
                f.write('')


def install_pgvector_extension():
    """Install pgvector extension for PostgreSQL if available."""
    
    try:
        # Check if we're using PostgreSQL
        if 'postgresql' in current_app.config.get('SQLALCHEMY_DATABASE_URI', ''):
            db.session.execute('CREATE EXTENSION IF NOT EXISTS vector;')
            db.session.commit()
            print("pgvector extension installed/verified")
    except Exception as e:
        print(f"Note: pgvector extension not available: {e}")
        print("AI features requiring vector similarity will be disabled")


def drop_all_tables():
    """Drop all database tables. USE WITH CAUTION!"""
    
    print("WARNING: This will delete all data!")
    confirm = input("Type 'yes' to confirm: ")
    
    if confirm.lower() == 'yes':
        db.drop_all()
        print("All tables dropped")
    else:
        print("Operation cancelled")


def reset_database():
    """Reset the database by dropping and recreating all tables."""
    
    print("Resetting database...")
    drop_all_tables()
    init_database()


if __name__ == '__main__':
    # Create Flask app context
    app = create_app()
    
    with app.app_context():
        if len(sys.argv) > 1:
            command = sys.argv[1]
            
            if command == 'reset':
                reset_database()
            elif command == 'drop':
                drop_all_tables()
            else:
                print(f"Unknown command: {command}")
                print("Available commands: reset, drop")
        else:
            init_database()