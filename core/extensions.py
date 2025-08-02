"""Flask extensions initialization."""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_socketio import SocketIO
from celery import Celery

# Database
db = SQLAlchemy()
migrate = Migrate()

# Authentication
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

# Email
mail = Mail()

# Rate Limiting
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Real-time notifications
socketio = SocketIO()

# Background tasks
celery = Celery()

def init_extensions(app):
    """Initialize all Flask extensions."""
    
    # Database
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Authentication
    login_manager.init_app(app)
    
    # Email
    mail.init_app(app)
    
    # Rate Limiting
    limiter.init_app(app)
    
    # Real-time notifications
    socketio.init_app(app, cors_allowed_origins="*")
    
    # Background tasks
    celery.conf.update(app.config)
    
    # TODO: Configure Celery to use Flask app context
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask