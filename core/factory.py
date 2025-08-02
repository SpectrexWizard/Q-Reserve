"""Flask application factory."""

import os
from flask import Flask
from flask_limiter.util import get_remote_address

from core.config import config
from core.extensions import init_extensions
from core.errors import register_error_handlers


def create_app(config_name=None):
    """Application factory function."""
    
    app = Flask(__name__)
    
    # Load configuration
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    init_extensions(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Register CLI commands
    register_commands(app)
    
    # Configure logging
    configure_logging(app)
    
    return app


def register_blueprints(app):
    """Register Flask blueprints."""
    
    # TODO: Import and register all blueprints
    from apps.auth import auth_bp
    from apps.users import users_bp
    from apps.categories import categories_bp
    from apps.tickets import tickets_bp
    from apps.notifications import notifications_bp
    from apps.dashboard import dashboard_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(users_bp, url_prefix='/users')
    app.register_blueprint(categories_bp, url_prefix='/categories')
    app.register_blueprint(tickets_bp, url_prefix='/tickets')
    app.register_blueprint(notifications_bp, url_prefix='/notifications')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')


def register_commands(app):
    """Register Flask CLI commands."""
    
    @app.cli.command('init-db')
    def init_db():
        """Initialize the database."""
        from core.extensions import db
        db.create_all()
        print('Database initialized!')
    
    @app.cli.command('seed-data')
    def seed_data():
        """Seed the database with sample data."""
        from scripts.seed_data import seed_all
        seed_all()
        print('Database seeded!')
    
    @app.cli.command('create-admin')
    def create_admin():
        """Create an admin user."""
        from apps.users.models import User
        from apps.users.services import create_user
        from core.extensions import db
        
        email = input('Enter admin email: ')
        password = input('Enter admin password: ')
        
        user = create_user(
            email=email,
            password=password,
            role='admin',
            is_active=True
        )
        
        db.session.commit()
        print(f'Admin user {email} created successfully!')


def configure_logging(app):
    """Configure application logging."""
    
    import logging
    from logging.handlers import RotatingFileHandler
    import os
    
    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        file_handler = RotatingFileHandler(
            'logs/q_reserve.log',
            maxBytes=10240000,
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('Q-Reserve startup')