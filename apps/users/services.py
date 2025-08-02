"""User services for business logic."""

from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from flask import current_app
from core.extensions import db
from core.errors import ValidationError, PermissionError
from .models import User, UserProfile


def create_user(
    email: str,
    password: str,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    display_name: Optional[str] = None,
    role: str = 'end_user',
    is_active: bool = True,
    **kwargs
) -> User:
    """Create a new user."""
    
    # Validate email
    if not email or '@' not in email:
        raise ValidationError("Valid email is required")
    
    # Check if user already exists
    if User.query.filter_by(email=email).first():
        raise ValidationError("User with this email already exists")
    
    # Validate role
    if role not in User.ROLES:
        raise ValidationError("Invalid role")
    
    # Create user
    user = User(
        email=email,
        first_name=first_name,
        last_name=last_name,
        display_name=display_name,
        role=role,
        is_active=is_active,
        **kwargs
    )
    user.set_password(password)
    
    # Create profile
    profile = UserProfile(user=user)
    
    db.session.add(user)
    db.session.add(profile)
    db.session.commit()
    
    return user


def get_user_by_id(user_id: int) -> Optional[User]:
    """Get user by ID."""
    return User.query.get(user_id)


def get_user_by_email(email: str) -> Optional[User]:
    """Get user by email."""
    return User.query.filter_by(email=email).first()


def get_user_by_uuid(uuid: str) -> Optional[User]:
    """Get user by UUID."""
    return User.query.filter_by(uuid=uuid).first()


def update_user(user: User, **kwargs) -> User:
    """Update user information."""
    
    # Prevent updating certain fields directly
    protected_fields = ['id', 'uuid', 'password_hash', 'created_at']
    for field in protected_fields:
        kwargs.pop(field, None)
    
    for key, value in kwargs.items():
        if hasattr(user, key):
            setattr(user, key, value)
    
    user.updated_at = datetime.now(timezone.utc)
    db.session.commit()
    
    return user


def update_user_profile(user: User, **kwargs) -> UserProfile:
    """Update user profile information."""
    
    if not user.profile:
        profile = UserProfile(user=user)
        db.session.add(profile)
    else:
        profile = user.profile
    
    # Update profile fields
    for key, value in kwargs.items():
        if hasattr(profile, key):
            setattr(profile, key, value)
    
    profile.updated_at = datetime.now(timezone.utc)
    db.session.commit()
    
    return profile


def change_password(user: User, current_password: str, new_password: str) -> bool:
    """Change user password."""
    
    if not user.check_password(current_password):
        raise ValidationError("Current password is incorrect")
    
    if len(new_password) < 8:
        raise ValidationError("Password must be at least 8 characters long")
    
    user.set_password(new_password)
    user.updated_at = datetime.now(timezone.utc)
    db.session.commit()
    
    return True


def activate_user(user: User) -> User:
    """Activate a user account."""
    user.is_active = True
    user.updated_at = datetime.now(timezone.utc)
    db.session.commit()
    return user


def deactivate_user(user: User) -> User:
    """Deactivate a user account."""
    user.is_active = False
    user.updated_at = datetime.now(timezone.utc)
    db.session.commit()
    return user


def delete_user(user: User) -> bool:
    """Delete a user account."""
    # TODO: Implement soft delete instead of hard delete
    db.session.delete(user)
    db.session.commit()
    return True


def get_users_by_role(role: str, page: int = 1, per_page: int = 20) -> List[User]:
    """Get users by role with pagination."""
    return User.query.filter_by(role=role).paginate(
        page=page, per_page=per_page, error_out=False
    )


def get_active_agents() -> List[User]:
    """Get all active support agents."""
    return User.query.filter_by(role='agent', is_active=True).all()


def search_users(
    query: str,
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
    page: int = 1,
    per_page: int = 20
) -> List[User]:
    """Search users with filters."""
    
    search_query = User.query
    
    # Apply search filter
    if query:
        search_query = search_query.filter(
            db.or_(
                User.email.ilike(f'%{query}%'),
                User.first_name.ilike(f'%{query}%'),
                User.last_name.ilike(f'%{query}%'),
                User.display_name.ilike(f'%{query}%')
            )
        )
    
    # Apply role filter
    if role:
        search_query = search_query.filter_by(role=role)
    
    # Apply active filter
    if is_active is not None:
        search_query = search_query.filter_by(is_active=is_active)
    
    return search_query.paginate(
        page=page, per_page=per_page, error_out=False
    )


def get_user_stats(user: User) -> Dict[str, Any]:
    """Get comprehensive user statistics."""
    stats = user.get_stats()
    
    # Add additional stats
    stats['days_since_registration'] = (datetime.now(timezone.utc) - user.created_at).days
    stats['last_activity'] = user.last_login.isoformat() if user.last_login else None
    
    return stats


def update_user_preferences(
    user: User,
    theme_preference: Optional[str] = None,
    language: Optional[str] = None,
    timezone: Optional[str] = None
) -> User:
    """Update user preferences."""
    
    if theme_preference and theme_preference not in ['light', 'dark', 'auto']:
        raise ValidationError("Invalid theme preference")
    
    if theme_preference:
        user.theme_preference = theme_preference
    
    if language:
        user.language = language
    
    if timezone:
        user.timezone = timezone
    
    user.updated_at = datetime.now(timezone.utc)
    db.session.commit()
    
    return user


def verify_user_email(user: User) -> User:
    """Mark user email as verified."""
    user.is_verified = True
    user.updated_at = datetime.now(timezone.utc)
    db.session.commit()
    return user


def get_user_notifications(user: User, unread_only: bool = False, limit: int = 50) -> List:
    """Get user notifications."""
    from apps.notifications.models import Notification
    
    query = Notification.query.filter_by(user_id=user.id)
    
    if unread_only:
        query = query.filter_by(is_read=False)
    
    return query.order_by(Notification.created_at.desc()).limit(limit).all()


def mark_notifications_read(user: User, notification_ids: List[int] = None) -> int:
    """Mark notifications as read."""
    from apps.notifications.models import Notification
    
    query = Notification.query.filter_by(user_id=user.id, is_read=False)
    
    if notification_ids:
        query = query.filter(Notification.id.in_(notification_ids))
    
    count = query.update({'is_read': True})
    db.session.commit()
    
    return count