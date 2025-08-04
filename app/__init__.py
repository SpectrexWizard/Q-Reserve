import os
from flask import Flask
from config import config
from app.extensions import db, jwt
from app.error_handlers import register_error_handlers

def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    
    # Register blueprints
    from app.auth.routes import auth_bp
    from app.tickets.routes import tickets_bp
    from app.categories.routes import categories_bp
    from app.comments.routes import comments_bp
    from app.votes.routes import votes_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(tickets_bp, url_prefix='/tickets')
    app.register_blueprint(categories_bp, url_prefix='/categories')
    app.register_blueprint(comments_bp, url_prefix='/comments')
    app.register_blueprint(votes_bp, url_prefix='/votes')
    
    # Main route
    @app.route('/')
    def index():
        from flask import redirect, url_for
        return redirect(url_for('tickets.list_tickets'))
    
    # Register error handlers
    register_error_handlers(app)
    
    # Template context processors
    @app.context_processor
    def inject_user():
        from flask import session
        from app.models import User
        user = None
        if 'user_id' in session:
            user = User.query.get(session['user_id'])
        return dict(user=user)
    
    # Create tables
    with app.app_context():
        db.create_all()
        
        # Create default admin user if it doesn't exist
        from app.models import User, Category
        from app.auth.utils import hash_password
        
        admin = User.query.filter_by(email='admin@helpdesk.local').first()
        if not admin:
            admin = User(
                email='admin@helpdesk.local',
                username='admin',
                password_hash=hash_password('admin123'),
                role='admin'
            )
            db.session.add(admin)
        
        # Create default categories if they don't exist
        default_categories = ['General', 'Technical', 'Billing', 'Feature Request']
        for cat_name in default_categories:
            if not Category.query.filter_by(name=cat_name).first():
                category = Category(name=cat_name, description=f'{cat_name} support tickets')
                db.session.add(category)
        
        db.session.commit()
    
    return app