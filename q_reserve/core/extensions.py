"""
Flask extensions initialization module.

This module initializes all Flask extensions used in the Q-Reserve application.
Extensions are initialized here and imported by the application factory.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_socketio import SocketIO
import redis
from celery import Celery

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
mail = Mail()
csrf = CSRFProtect()
limiter = Limiter(key_func=get_remote_address)
socketio = SocketIO()

# Redis connection
redis_client = None

# Celery instance
celery = Celery(__name__)


def init_extensions(app):
    """Initialize Flask extensions with app instance."""
    global redis_client
    
    # Database
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Authentication
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    # Email
    mail.init_app(app)
    
    # CSRF Protection
    csrf.init_app(app)
    
    # Rate Limiting
    limiter.init_app(app)
    
    # WebSocket Support
    socketio.init_app(app, 
                     cors_allowed_origins="*",
                     async_mode='threading',
                     logger=True,
                     engineio_logger=True)
    
    # Redis
    redis_client = redis.from_url(app.config['REDIS_URL'])
    
    # Celery
    init_celery(app)


def init_celery(app):
    """Initialize Celery with Flask app context."""
    celery.conf.update(
        broker_url=app.config['CELERY_BROKER_URL'],
        result_backend=app.config['CELERY_RESULT_BACKEND'],
        task_serializer='json',
        result_serializer='json',
        accept_content=['json'],
        timezone='UTC',
        enable_utc=True,
        task_routes={
            'apps.notifications.tasks.*': {'queue': 'notifications'},
            'apps.ai.tasks.*': {'queue': 'ai'},
            'apps.tickets.tasks.*': {'queue': 'tickets'}
        }
    )
    
    class ContextTask(celery.Task):
        """Make celery tasks work with Flask app context."""
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask
    return celery


@login_manager.user_loader
def load_user(user_id):
    """Load user for Flask-Login."""
    # Import here to avoid circular imports
    from apps.users.models import User
    return User.query.get(int(user_id))


# TODO: Add health check endpoints for extensions
# TODO: Add extension monitoring and metrics
# TODO: Add graceful degradation when extensions fail