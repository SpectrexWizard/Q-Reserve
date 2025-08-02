"""
Authentication utility functions for Q-Reserve application.

This module contains helper functions for authentication-related operations.
"""

from functools import wraps
from flask import abort, current_app, url_for
from flask_login import current_user
from flask_mail import Message

from core.extensions import mail
from apps.users.models import UserRole


def role_required(*roles):
    """
    Decorator to require specific user roles.
    
    Args:
        *roles: Required user roles (admin, agent, end_user)
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            
            user_role = current_user.role.value
            if user_role not in [role.value if hasattr(role, 'value') else role for role in roles]:
                abort(403)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):
    """Decorator to require admin role."""
    return role_required(UserRole.ADMIN)(f)


def agent_required(f):
    """Decorator to require agent or admin role."""
    return role_required(UserRole.AGENT, UserRole.ADMIN)(f)


def send_password_reset_email(user):
    """
    Send password reset email to user.
    
    Args:
        user: User object with password reset token
    """
    if not user.password_reset_token:
        raise ValueError("User must have a password reset token")
    
    reset_url = url_for('auth.reset_password', token=user.password_reset_token, _external=True)
    
    subject = "Password Reset - Q-Reserve"
    
    html_body = f"""
    <h2>Password Reset Request</h2>
    <p>Hello {user.display_name},</p>
    <p>You have requested to reset your password for your Q-Reserve account.</p>
    <p>Click the link below to reset your password:</p>
    <p><a href="{reset_url}" style="color: #007bff;">Reset Password</a></p>
    <p>This link will expire in 1 hour.</p>
    <p>If you did not request this password reset, please ignore this email.</p>
    <br>
    <p>Best regards,<br>Q-Reserve Team</p>
    """
    
    text_body = f"""
    Password Reset Request
    
    Hello {user.display_name},
    
    You have requested to reset your password for your Q-Reserve account.
    
    Visit the following link to reset your password:
    {reset_url}
    
    This link will expire in 1 hour.
    
    If you did not request this password reset, please ignore this email.
    
    Best regards,
    Q-Reserve Team
    """
    
    msg = Message(
        subject=subject,
        recipients=[user.email],
        html=html_body,
        body=text_body
    )
    
    mail.send(msg)


def check_password_strength(password):
    """
    Check password strength and return feedback.
    
    Args:
        password: Password string to check
        
    Returns:
        tuple: (is_strong, feedback_list)
    """
    feedback = []
    is_strong = True
    
    if len(password) < 8:
        feedback.append("Password must be at least 8 characters long")
        is_strong = False
    
    if not any(c.islower() for c in password):
        feedback.append("Password must contain at least one lowercase letter")
        is_strong = False
    
    if not any(c.isupper() for c in password):
        feedback.append("Password must contain at least one uppercase letter")
        is_strong = False
    
    if not any(c.isdigit() for c in password):
        feedback.append("Password must contain at least one number")
        is_strong = False
    
    if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        feedback.append("Password should contain at least one special character")
    
    if len(password) > 20:
        feedback.append("Password should be less than 20 characters for better usability")
    
    return is_strong, feedback


def generate_username_suggestions(first_name, last_name, email):
    """
    Generate username suggestions based on user information.
    
    Args:
        first_name: User's first name
        last_name: User's last name
        email: User's email address
        
    Returns:
        list: List of username suggestions
    """
    suggestions = []
    
    # Clean names (remove spaces, convert to lowercase)
    first_clean = first_name.lower().replace(' ', '')
    last_clean = last_name.lower().replace(' ', '')
    email_prefix = email.split('@')[0].lower()
    
    # Generate suggestions
    suggestions.extend([
        f"{first_clean}{last_clean}",
        f"{first_clean}.{last_clean}",
        f"{first_clean}_{last_clean}",
        f"{first_clean[0]}{last_clean}",
        f"{first_clean}{last_clean[0]}",
        email_prefix
    ])
    
    # Add numbered variations
    base_suggestions = suggestions.copy()
    for base in base_suggestions[:3]:  # Only for first few suggestions
        for i in range(1, 4):
            suggestions.append(f"{base}{i}")
    
    # Remove duplicates while preserving order
    seen = set()
    unique_suggestions = []
    for suggestion in suggestions:
        if suggestion not in seen and len(suggestion) >= 3:
            seen.add(suggestion)
            unique_suggestions.append(suggestion)
    
    return unique_suggestions[:10]  # Return top 10 suggestions


def is_safe_redirect_url(target):
    """
    Check if a redirect URL is safe (same domain).
    
    Args:
        target: Target URL to check
        
    Returns:
        bool: True if safe, False otherwise
    """
    from urllib.parse import urlparse, urljoin
    from flask import request
    
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


def get_user_ip_address():
    """Get user's IP address from request headers."""
    from flask import request
    
    # Check for forwarded IP first (in case of proxy/load balancer)
    ip = request.headers.get('X-Forwarded-For')
    if ip:
        ip = ip.split(',')[0].strip()
    else:
        ip = request.headers.get('X-Real-IP') or request.remote_addr
    
    return ip


def log_authentication_attempt(username_or_email, success, ip_address=None):
    """
    Log authentication attempts for security monitoring.
    
    Args:
        username_or_email: Login identifier used
        success: Whether the attempt was successful
        ip_address: IP address of the attempt
    """
    if ip_address is None:
        ip_address = get_user_ip_address()
    
    status = "SUCCESS" if success else "FAILED"
    current_app.logger.info(
        f"Login attempt: {status} | User: {username_or_email} | IP: {ip_address}"
    )
    
    # TODO: Store in database for analysis and rate limiting
    # TODO: Implement account lockout after multiple failed attempts
    # TODO: Add alerting for suspicious patterns


# TODO: Add OAuth integration utilities
# TODO: Add two-factor authentication utilities
# TODO: Add session management utilities
# TODO: Add brute force protection utilities