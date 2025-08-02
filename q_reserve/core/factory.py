"""
Flask application factory module.

This module implements the application factory pattern for creating Flask apps
with proper configuration, extension initialization, and blueprint registration.
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.middleware.proxy_fix import ProxyFix
import click

from core.config import get_config
from core.extensions import init_extensions
from core.errors import register_error_handlers
from core.utils import register_template_filters


def create_app(config_name=None):
    """
    Create and configure Flask application instance.
    
    Args:
        config_name: Configuration name (development, testing, production)
        
    Returns:
        Flask application instance
    """
    app = Flask(__name__, 
                instance_relative_config=True,
                static_folder='../static',
                template_folder='../templates')
    
    # Load configuration
    config_class = get_config(config_name)
    app.config.from_object(config_class)
    
    # Handle proxy headers in production
    if not app.config.get('DEBUG'):
        app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    
    # Initialize extensions
    init_extensions(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register template filters and globals
    register_template_filters(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Configure logging
    configure_logging(app)
    
    # Register CLI commands
    register_cli_commands(app)
    
    # Add request hooks
    register_request_hooks(app)
    
    return app


def register_blueprints(app):
    """Register all application blueprints."""
    
    # Authentication blueprint
    from apps.auth.routes import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    # Users blueprint
    from apps.users.routes import bp as users_bp
    app.register_blueprint(users_bp, url_prefix='/users')
    
    # Categories blueprint
    from apps.categories.routes import bp as categories_bp
    app.register_blueprint(categories_bp, url_prefix='/categories')
    
    # Tickets blueprint
    from apps.tickets.routes import bp as tickets_bp
    app.register_blueprint(tickets_bp, url_prefix='/tickets')
    
    # Notifications blueprint
    from apps.notifications.routes import bp as notifications_bp
    app.register_blueprint(notifications_bp, url_prefix='/notifications')
    
    # Dashboard blueprint
    from apps.dashboard.routes import bp as dashboard_bp
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    
    # Main routes (home page, etc.)
    register_main_routes(app)


def register_main_routes(app):
    """Register main application routes."""
    
    @app.route('/')
    def index():
        """Home page route."""
        from flask_login import current_user
        if current_user.is_authenticated:
            if current_user.role == 'admin':
                return redirect(url_for('dashboard.admin'))
            elif current_user.role == 'agent':
                return redirect(url_for('dashboard.agent'))
            else:
                return redirect(url_for('tickets.list'))
        return render_template('auth/login.html')
    
    @app.route('/health')
    def health_check():
        """Health check endpoint."""
        return {'status': 'healthy'}, 200


def configure_logging(app):
    """Configure application logging."""
    if not app.debug and not app.testing:
        # Create logs directory if it doesn't exist
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        # Configure file handler
        file_handler = RotatingFileHandler(
            'logs/q_reserve.log',
            maxBytes=10240000,  # 10MB
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('Q-Reserve startup')


def register_cli_commands(app):
    """Register CLI commands."""
    
    @app.cli.command()
    def init_db():
        """Initialize the database."""
        from core.extensions import db
        from scripts.init_db import init_database
        init_database()
        click.echo('Database initialized.')
    
    @app.cli.command()
    def seed_data():
        """Seed the database with sample data."""
        from scripts.seed_data import seed_database
        seed_database()
        click.echo('Database seeded with sample data.')


def register_request_hooks(app):
    """Register request hooks for logging and monitoring."""
    
    @app.before_request
    def log_request_info():
        """Log request information."""
        if app.config.get('DEBUG'):
            app.logger.debug('Request: %s %s', request.method, request.url)
    
    @app.after_request
    def log_response_info(response):
        """Log response information."""
        if app.config.get('DEBUG'):
            app.logger.debug('Response: %s', response.status_code)
        return response


# TODO: Add application metrics collection
# TODO: Add security headers middleware
# TODO: Add API versioning support
# TODO: Add request tracing for debugging