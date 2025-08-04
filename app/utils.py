import os
import uuid
import mimetypes
from functools import wraps
from werkzeug.utils import secure_filename
from flask import request, jsonify, current_app
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app.models import User

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def sanitize_filename(filename):
    """Sanitize and generate unique filename"""
    secure_name = secure_filename(filename)
    name, ext = os.path.splitext(secure_name)
    unique_name = f"{name}_{uuid.uuid4().hex[:8]}{ext}"
    return unique_name

def get_file_info(file):
    """Get file information for validation"""
    filename = file.filename
    file_size = 0
    
    # Get file size
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)  # Reset to beginning
    
    # Get MIME type
    mime_type, _ = mimetypes.guess_type(filename)
    if not mime_type:
        mime_type = 'application/octet-stream'
    
    return {
        'filename': filename,
        'size': file_size,
        'mime_type': mime_type
    }

def validate_file_upload(file):
    """Validate uploaded file"""
    if not file or file.filename == '':
        return False, "No file selected"
    
    if not allowed_file(file.filename):
        return False, f"File type not allowed. Allowed types: {', '.join(current_app.config['ALLOWED_EXTENSIONS'])}"
    
    file_info = get_file_info(file)
    
    if file_info['size'] > current_app.config['MAX_CONTENT_LENGTH']:
        return False, f"File too large. Maximum size: {current_app.config['MAX_CONTENT_LENGTH'] // (1024*1024)}MB"
    
    return True, file_info

# RBAC Decorators
def jwt_required_with_user(f):
    """JWT required decorator that also loads the user"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask import session, redirect, url_for
        
        # Check for session-based authentication first (for web interface)
        if 'user_id' in session:
            user = User.query.get(session['user_id'])
            if user and user.is_active:
                return f(user, *args, **kwargs)
        
        # Fall back to JWT authentication (for API)
        try:
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            
            if not user or not user.is_active:
                if request.is_json:
                    return jsonify({'error': 'User not found or inactive'}), 401
                return redirect(url_for('auth.login'))
            
            return f(user, *args, **kwargs)
        except:
            if request.is_json:
                return jsonify({'error': 'Authentication required'}), 401
            return redirect(url_for('auth.login'))
    
    return decorated_function

def role_required(*allowed_roles):
    """Decorator to check user role"""
    def decorator(f):
        @wraps(f)
        @jwt_required_with_user
        def decorated_function(user, *args, **kwargs):
            if user.role not in allowed_roles:
                return jsonify({'error': 'Insufficient permissions'}), 403
            return f(user, *args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    """Decorator for admin-only routes"""
    @wraps(f)
    @role_required('admin')
    def decorated_function(user, *args, **kwargs):
        return f(user, *args, **kwargs)
    return decorated_function

def agent_required(f):
    """Decorator for agent and admin routes"""
    @wraps(f)
    @role_required('agent', 'admin')
    def decorated_function(user, *args, **kwargs):
        return f(user, *args, **kwargs)
    return decorated_function

def can_access_ticket(user, ticket):
    """Check if user can access a specific ticket"""
    if user.role in ['admin', 'agent']:
        return True
    return ticket.user_id == user.id

def can_modify_ticket(user, ticket):
    """Check if user can modify a specific ticket"""
    if user.role == 'admin':
        return True
    if user.role == 'agent':
        return True  # Agents can modify any ticket
    return ticket.user_id == user.id  # Users can only modify their own tickets

def format_file_size(size_bytes):
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0B"
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    return f"{size_bytes:.1f}{size_names[i]}"