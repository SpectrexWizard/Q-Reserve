"""
Utility functions and template filters for Q-Reserve application.

This module contains helper functions, template filters, and common utilities
used throughout the application.
"""

import os
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from flask import current_app, url_for
from werkzeug.utils import secure_filename
import magic


def generate_secure_token(length: int = 32) -> str:
    """Generate a cryptographically secure random token."""
    return secrets.token_urlsafe(length)


def hash_string(string: str, salt: str = None) -> str:
    """Hash a string with optional salt."""
    if salt is None:
        salt = secrets.token_hex(16)
    
    combined = f"{string}{salt}"
    hash_object = hashlib.sha256(combined.encode())
    return f"{salt}${hash_object.hexdigest()}"


def verify_hash(string: str, hashed: str) -> bool:
    """Verify a string against its hash."""
    try:
        salt, hash_value = hashed.split('$', 1)
        return hash_string(string, salt) == hashed
    except ValueError:
        return False


def allowed_file(filename: str) -> bool:
    """Check if uploaded file has allowed extension."""
    if not filename or '.' not in filename:
        return False
    
    extension = filename.rsplit('.', 1)[1].lower()
    return extension in current_app.config['ALLOWED_EXTENSIONS']


def get_file_type(filepath: str) -> str:
    """Get MIME type of file using python-magic."""
    try:
        return magic.from_file(filepath, mime=True)
    except Exception:
        return 'application/octet-stream'


def secure_file_upload(file, upload_folder: str, subfolder: str = None) -> Optional[str]:
    """
    Securely save uploaded file and return the relative path.
    
    Args:
        file: Uploaded file object
        upload_folder: Base upload folder
        subfolder: Optional subfolder (e.g., 'ticket_123')
        
    Returns:
        Relative path to saved file or None if failed
    """
    if not file or not file.filename or not allowed_file(file.filename):
        return None
    
    # Secure the filename
    filename = secure_filename(file.filename)
    if not filename:
        return None
    
    # Add timestamp to prevent conflicts
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S_')
    filename = f"{timestamp}{filename}"
    
    # Create full path
    if subfolder:
        full_folder = os.path.join(upload_folder, subfolder)
    else:
        full_folder = upload_folder
    
    # Ensure directory exists
    os.makedirs(full_folder, exist_ok=True)
    
    # Save file
    filepath = os.path.join(full_folder, filename)
    try:
        file.save(filepath)
        
        # Return relative path
        if subfolder:
            return os.path.join(subfolder, filename)
        return filename
    except Exception as e:
        current_app.logger.error(f"Failed to save file: {e}")
        return None


def calculate_sla_deadline(priority: str, created_at: datetime = None) -> datetime:
    """Calculate SLA deadline based on priority and creation time."""
    if created_at is None:
        created_at = datetime.utcnow()
    
    sla_hours = current_app.config['SLA_HOURS'].get(priority.lower(), 
                                                    current_app.config['SLA_HOURS']['default'])
    return created_at + timedelta(hours=sla_hours)


def is_sla_breached(deadline: datetime, resolved_at: datetime = None) -> bool:
    """Check if SLA has been breached."""
    check_time = resolved_at or datetime.utcnow()
    return check_time > deadline


def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format."""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to specified length with suffix."""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def time_ago(dt: datetime) -> str:
    """Return human-readable time difference."""
    now = datetime.utcnow()
    diff = now - dt
    
    if diff.days > 365:
        years = diff.days // 365
        return f"{years} year{'s' if years != 1 else ''} ago"
    elif diff.days > 30:
        months = diff.days // 30
        return f"{months} month{'s' if months != 1 else ''} ago"
    elif diff.days > 0:
        return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    else:
        return "Just now"


def get_gravatar_url(email: str, size: int = 80, default: str = 'identicon') -> str:
    """Generate Gravatar URL for email."""
    email_hash = hashlib.md5(email.lower().encode('utf-8')).hexdigest()
    return f"https://www.gravatar.com/avatar/{email_hash}?s={size}&d={default}"


def register_template_filters(app):
    """Register custom template filters and globals."""
    
    @app.template_filter('time_ago')
    def time_ago_filter(dt):
        """Template filter for time ago formatting."""
        return time_ago(dt) if dt else ''
    
    @app.template_filter('truncate')
    def truncate_filter(text, length=100):
        """Template filter for text truncation."""
        return truncate_text(text, length) if text else ''
    
    @app.template_filter('file_size')
    def file_size_filter(size):
        """Template filter for file size formatting."""
        return format_file_size(size) if size else ''
    
    @app.template_global('gravatar')
    def gravatar_global(email, size=80):
        """Template global for Gravatar URLs."""
        return get_gravatar_url(email, size) if email else ''
    
    @app.template_global('url_for_page')
    def url_for_page(endpoint, **kwargs):
        """Template global for pagination URLs."""
        from flask import request
        args = request.args.copy()
        args.update(kwargs)
        return url_for(endpoint, **args)
    
    @app.template_global('current_year')
    def current_year():
        """Template global for current year."""
        return datetime.utcnow().year


# TODO: Add text processing utilities (markdown, sanitization)
# TODO: Add image processing utilities (resize, thumbnail generation)
# TODO: Add caching decorators for expensive operations
# TODO: Add data export utilities (CSV, PDF generation)