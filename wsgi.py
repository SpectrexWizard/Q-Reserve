"""
WSGI entry point for production deployment.
This file is used by web servers like Gunicorn, uWSGI, or Apache.
"""

import os
from app import create_app

# Create the Flask application
application = create_app('production')

if __name__ == "__main__":
    application.run()