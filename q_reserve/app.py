"""
Q-Reserve Helpdesk Application

Main application entry point for the Q-Reserve helpdesk system.
This file creates the Flask application using the application factory pattern.
"""

import os
from core.factory import create_app
from core.extensions import socketio

# Create Flask application
app = create_app(os.environ.get('FLASK_ENV', 'development'))

if __name__ == '__main__':
    # Run with SocketIO for development
    socketio.run(app, 
                debug=app.config.get('DEBUG', False),
                host='0.0.0.0',
                port=int(os.environ.get('PORT', 5000)))