"""Utility functions for the core module."""

import os
import uuid
import hashlib
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from werkzeug.utils import secure_filename
from flask import current_app


def generate_uuid() -> str:
    """Generate a UUID string."""
    return str(uuid.uuid4())


def hash_password(password: str) -> str:
    """Hash a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash."""
    return hash_password(password) == hashed


def allowed_file(filename: str) -> bool:
    """Check if a file extension is allowed."""
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in current_app.config['ALLOWED_EXTENSIONS']


def save_uploaded_file(file, folder: str = 'attachments') -> Optional[str]:
    """Save an uploaded file and return the filename."""
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Add timestamp to prevent conflicts
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        name, ext = os.path.splitext(filename)
        unique_filename = f"{name}_{timestamp}{ext}"
        
        upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], folder)
        os.makedirs(upload_path, exist_ok=True)
        
        file_path = os.path.join(upload_path, unique_filename)
        file.save(file_path)
        
        return unique_filename
    return None


def format_datetime(dt: datetime, format_str: str = '%Y-%m-%d %H:%M:%S') -> str:
    """Format a datetime object to string."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.strftime(format_str)


def parse_datetime(date_str: str, format_str: str = '%Y-%m-%d %H:%M:%S') -> datetime:
    """Parse a datetime string."""
    return datetime.strptime(date_str, format_str)


def get_time_ago(dt: datetime) -> str:
    """Get a human-readable time ago string."""
    now = datetime.now(timezone.utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    
    diff = now - dt
    
    if diff.days > 0:
        return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
    elif diff.seconds >= 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif diff.seconds >= 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    else:
        return "Just now"


def sanitize_html(text: str) -> str:
    """Sanitize HTML content to prevent XSS."""
    import re
    # Remove script tags and their content
    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
    # Remove other potentially dangerous tags
    dangerous_tags = ['iframe', 'object', 'embed', 'form', 'input', 'button']
    for tag in dangerous_tags:
        text = re.sub(rf'<{tag}[^>]*>.*?</{tag}>', '', text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(rf'<{tag}[^>]*/?>', '', text, flags=re.IGNORECASE)
    
    return text


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to a maximum length."""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."


def generate_slug(text: str) -> str:
    """Generate a URL-friendly slug from text."""
    import re
    # Convert to lowercase and replace spaces with hyphens
    slug = re.sub(r'[^\w\s-]', '', text.lower())
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug.strip('-')


def paginate_query(query, page: int = 1, per_page: int = 20):
    """Paginate a SQLAlchemy query."""
    return query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )


def get_client_ip() -> str:
    """Get the client's IP address."""
    from flask import request
    
    # Check for forwarded headers (for proxy setups)
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    else:
        return request.remote_addr


def is_ajax_request() -> bool:
    """Check if the request is an AJAX request."""
    from flask import request
    return request.headers.get('X-Requested-With') == 'XMLHttpRequest'


def json_response(data: Dict[str, Any], status_code: int = 200):
    """Create a JSON response."""
    from flask import jsonify
    response = jsonify(data)
    response.status_code = status_code
    return response


def error_response(message: str, status_code: int = 400):
    """Create an error JSON response."""
    return json_response({'error': True, 'message': message}, status_code)


def success_response(data: Dict[str, Any] = None, message: str = None):
    """Create a success JSON response."""
    response = {'success': True}
    if data:
        response.update(data)
    if message:
        response['message'] = message
    return json_response(response)