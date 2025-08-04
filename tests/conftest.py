"""
Test configuration for the helpdesk application.
This file contains pytest fixtures and test setup.
"""

import pytest
from app import create_app
from app.extensions import db

@pytest.fixture
def app():
    """Create application for testing."""
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Create test CLI runner."""
    return app.test_cli_runner()

# TODO: Add more test fixtures as needed
# - Sample users with different roles
# - Sample tickets and comments
# - Authentication helpers