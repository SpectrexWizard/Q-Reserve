#!/usr/bin/env python3
"""
Development entry point for the Helpdesk System.
Run this file to start the development server.
"""

import os
from app import create_app

if __name__ == '__main__':
    # Create the Flask application
    app = create_app('development')
    
    # Run the development server
    app.run(
        host='127.0.0.1',
        port=5000,
        debug=True,
        use_reloader=True
    )