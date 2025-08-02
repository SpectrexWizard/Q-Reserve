"""
User models for Q-Reserve application.

This module defines the User model with role-based access control,
profile management, and authentication features.
"""

from datetime import datetime
from enum import Enum
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import event

from core.extensions import db


class UserRole(Enum):
    """User role enumeration."""
    END_USER = 'end_user'
    AGENT = 'agent'
    ADMIN = 'admin'


class UserStatus(Enum):
    """User status enumeration."""
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    SUSPENDED = 'suspended'
    PENDING = 'pending'


class User(UserMixin, db.Model):
    """User model with role-based access control."""
    
    __tablename__ = 'users'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Basic user information
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    
    # Authentication
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Role and status
    role = db.Column(db.Enum(UserRole), nullable=False, default=UserRole.END_USER)
    status = db.Column(db.Enum(UserStatus), nullable=False, default=UserStatus.ACTIVE)
    
    # Profile information
    phone = db.Column(db.String(20))
    department = db.Column(db.String(100))
    job_title = db.Column(db.String(100))
    bio = db.Column(db.Text)
    avatar_filename = db.Column(db.String(255))
    
    # Preferences
    theme = db.Column(db.String(20), default='light')  # light, dark
    language = db.Column(db.String(10), default='en')
    timezone = db.Column(db.String(50), default='UTC')
    email_notifications = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    email_verified_at = db.Column(db.DateTime)
    
    # Authentication tokens
    email_verification_token = db.Column(db.String(255))
    password_reset_token = db.Column(db.String(255))
    password_reset_expires = db.Column(db.DateTime)
    
    # Statistics (for gamification)
    points = db.Column(db.Integer, default=0)
    tickets_created = db.Column(db.Integer, default=0)
    tickets_resolved = db.Column(db.Integer, default=0)
    
    # Relationships
    created_tickets = db.relationship('Ticket', 
                                    foreign_keys='Ticket.created_by_id',
                                    backref='creator', 
                                    lazy='dynamic')
    assigned_tickets = db.relationship('Ticket', 
                                     foreign_keys='Ticket.assigned_to_id',
                                     backref='assignee', 
                                     lazy='dynamic')
    comments = db.relationship('Comment', backref='author', lazy='dynamic')
    votes = db.relationship('Vote', backref='user', lazy='dynamic')
    notifications = db.relationship('Notification', backref='user', lazy='dynamic')
    
    def __init__(self, **kwargs):
        """Initialize user with default values."""
        super(User, self).__init__(**kwargs)
        if not self.role:
            self.role = UserRole.END_USER
        if not self.status:
            self.status = UserStatus.ACTIVE
    
    @property
    def password(self):
        """Password property getter (raises AttributeError)."""
        raise AttributeError('password is not a readable attribute')
    
    @password.setter
    def password(self, password):
        """Password property setter."""
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        """Verify password against hash."""
        return check_password_hash(self.password_hash, password)
    
    @hybrid_property
    def full_name(self):
        """Get user's full name."""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def display_name(self):
        """Get user's display name (full name or username)."""
        if self.first_name and self.last_name:
            return self.full_name
        return self.username
    
    @property
    def is_admin(self):
        """Check if user is an admin."""
        return self.role == UserRole.ADMIN
    
    @property
    def is_agent(self):
        """Check if user is an agent."""
        return self.role == UserRole.AGENT
    
    @property
    def is_end_user(self):
        """Check if user is an end user."""
        return self.role == UserRole.END_USER
    
    @property
    def is_active_user(self):
        """Check if user account is active."""
        return self.status == UserStatus.ACTIVE
    
    @property
    def can_create_tickets(self):
        """Check if user can create tickets."""
        return self.is_active_user
    
    @property
    def can_assign_tickets(self):
        """Check if user can assign tickets."""
        return self.is_active_user and (self.is_agent or self.is_admin)
    
    @property
    def can_manage_users(self):
        """Check if user can manage other users."""
        return self.is_active_user and self.is_admin
    
    @property
    def can_manage_categories(self):
        """Check if user can manage categories."""
        return self.is_active_user and self.is_admin
    
    @property
    def can_view_all_tickets(self):
        """Check if user can view all tickets."""
        return self.is_active_user and (self.is_agent or self.is_admin)
    
    @property
    def avatar_url(self):
        """Get user's avatar URL."""
        if self.avatar_filename:
            return f"/static/uploads/avatars/{self.avatar_filename}"
        # TODO: Integrate with gravatar or use default avatar
        return f"https://www.gravatar.com/avatar/{hash(self.email)}?d=identicon&s=80"
    
    def update_last_login(self):
        """Update last login timestamp."""
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    def add_points(self, points):
        """Add points for gamification."""
        self.points += points
        db.session.commit()
    
    def can_edit_ticket(self, ticket):
        """Check if user can edit a specific ticket."""
        if not self.is_active_user:
            return False
        
        # Admins and agents can edit any ticket
        if self.is_admin or self.is_agent:
            return True
        
        # End users can only edit their own tickets
        return ticket.created_by_id == self.id
    
    def can_view_ticket(self, ticket):
        """Check if user can view a specific ticket."""
        if not self.is_active_user:
            return False
        
        # Admins and agents can view all tickets
        if self.is_admin or self.is_agent:
            return True
        
        # End users can only view their own tickets
        return ticket.created_by_id == self.id
    
    def get_accessible_tickets(self):
        """Get query for tickets accessible to this user."""
        from apps.tickets.models import Ticket
        
        if self.can_view_all_tickets:
            return Ticket.query
        else:
            return Ticket.query.filter_by(created_by_id=self.id)
    
    def to_dict(self, include_email=False):
        """Convert user to dictionary for API responses."""
        data = {
            'id': self.id,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'display_name': self.display_name,
            'role': self.role.value,
            'status': self.status.value,
            'avatar_url': self.avatar_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
        
        if include_email:
            data['email'] = self.email
        
        return data
    
    def __repr__(self):
        """String representation of user."""
        return f'<User {self.username}>'


# Event listeners for automatic updates
@event.listens_for(User, 'before_update')
def update_modified_time(mapper, connection, target):
    """Update the updated_at timestamp on user updates."""
    target.updated_at = datetime.utcnow()


# TODO: Add user activity logging
# TODO: Add user preferences management
# TODO: Add social login integration (OAuth)
# TODO: Add two-factor authentication support