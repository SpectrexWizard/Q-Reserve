import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration class."""
    
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f"postgresql://{os.environ.get('POSTGRES_USER', 'q_reserve_user')}:" \
        f"{os.environ.get('POSTGRES_PASSWORD', 'password')}@" \
        f"{os.environ.get('POSTGRES_HOST', 'localhost')}:" \
        f"{os.environ.get('POSTGRES_PORT', '5432')}/" \
        f"{os.environ.get('POSTGRES_DB', 'q_reserve_db')}"
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # Redis Configuration
    REDIS_URL = os.environ.get('REDIS_URL') or \
        f"redis://{os.environ.get('REDIS_HOST', 'localhost')}:" \
        f"{os.environ.get('REDIS_PORT', '6379')}/" \
        f"{os.environ.get('REDIS_DB', '0')}"
    
    # Email Configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'False').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    
    # AI Configuration
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    DEEPL_API_KEY = os.environ.get('DEEPL_API_KEY')
    GOOGLE_TRANSLATE_API_KEY = os.environ.get('GOOGLE_TRANSLATE_API_KEY')
    
    # File Upload Configuration
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 16777216))  # 16MB
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'static/uploads')
    ALLOWED_EXTENSIONS = os.environ.get('ALLOWED_EXTENSIONS', 'jpg,jpeg,png,gif,pdf,doc,docx,txt').split(',')
    
    # Rate Limiting
    RATELIMIT_STORAGE_URL = os.environ.get('RATELIMIT_STORAGE_URL') or REDIS_URL
    RATELIMIT_DEFAULT = os.environ.get('RATELIMIT_DEFAULT', '200 per day;50 per hour;10 per minute')
    
    # External Integrations
    SLACK_WEBHOOK_URL = os.environ.get('SLACK_WEBHOOK_URL')
    TEAMS_WEBHOOK_URL = os.environ.get('TEAMS_WEBHOOK_URL')
    
    # Monitoring
    SENTRY_DSN = os.environ.get('SENTRY_DSN')
    
    # Security
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = os.environ.get('SESSION_COOKIE_HTTPONLY', 'True').lower() == 'true'
    PERMANENT_SESSION_LIFETIME = timedelta(
        seconds=int(os.environ.get('PERMANENT_SESSION_LIFETIME', 3600))
    )
    
    # Feature Flags
    ENABLE_AI_FEATURES = os.environ.get('ENABLE_AI_FEATURES', 'True').lower() == 'true'
    ENABLE_REAL_TIME_NOTIFICATIONS = os.environ.get('ENABLE_REAL_TIME_NOTIFICATIONS', 'True').lower() == 'true'
    ENABLE_FILE_UPLOADS = os.environ.get('ENABLE_FILE_UPLOADS', 'True').lower() == 'true'
    ENABLE_VOTING = os.environ.get('ENABLE_VOTING', 'True').lower() == 'true'
    ENABLE_TRANSLATION = os.environ.get('ENABLE_TRANSLATION', 'True').lower() == 'true'
    
    # Celery Configuration
    CELERY_BROKER_URL = REDIS_URL
    CELERY_RESULT_BACKEND = REDIS_URL
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_ACCEPT_CONTENT = ['json']
    CELERY_TIMEZONE = 'UTC'
    CELERY_ENABLE_UTC = True
    
    # Pagination
    TICKETS_PER_PAGE = 20
    COMMENTS_PER_PAGE = 10
    
    # SLA Configuration
    DEFAULT_SLA_HOURS = 24
    URGENT_SLA_HOURS = 4
    CRITICAL_SLA_HOURS = 1


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    ENABLE_AI_FEATURES = False
    ENABLE_REAL_TIME_NOTIFICATIONS = False


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    
    # TODO: Configure Sentry for production error tracking
    if SENTRY_DSN:
        import sentry_sdk
        from sentry_sdk.integrations.flask import FlaskIntegration
        sentry_sdk.init(
            dsn=SENTRY_DSN,
            integrations=[FlaskIntegration()],
            traces_sample_rate=0.1,
        )


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}