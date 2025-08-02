"""User models for the Q-Reserve helpdesk system."""

from datetime import datetime, timezone
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from core.extensions import db
from core.utils import generate_uuid


class User(db.Model, UserMixin):
    """User model with role-based authentication."""
    
    __tablename__ = 'users'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=generate_uuid, nullable=False)
    
    # Authentication fields
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Profile fields
    first_name = db.Column(db.String(50), nullable=True)
    last_name = db.Column(db.String(50), nullable=True)
    display_name = db.Column(db.String(100), nullable=True)
    avatar = db.Column(db.String(255), nullable=True)
    
    # Role and status
    role = db.Column(db.String(20), nullable=False, default='end_user', index=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    
    # Preferences
    theme_preference = db.Column(db.String(10), default='light', nullable=False)
    language = db.Column(db.String(10), default='en', nullable=False)
    timezone = db.Column(db.String(50), default='UTC', nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    tickets_created = db.relationship('Ticket', backref='creator', lazy='dynamic', foreign_keys='Ticket.creator_id')
    tickets_assigned = db.relationship('Ticket', backref='assigned_agent', lazy='dynamic', foreign_keys='Ticket.assigned_agent_id')
    comments = db.relationship('Comment', backref='author', lazy='dynamic')
    votes = db.relationship('Vote', backref='user', lazy='dynamic')
    notifications = db.relationship('Notification', backref='user', lazy='dynamic')
    
    # Role constants
    ROLES = {
        'end_user': 'End User',
        'agent': 'Support Agent',
        'admin': 'Administrator'
    }
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.uuid:
            self.uuid = generate_uuid()
    
    def set_password(self, password: str) -> None:
        """Set the user's password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password: str) -> bool:
        """Check if the provided password is correct."""
        return check_password_hash(self.password_hash, password)
    
    def get_full_name(self) -> str:
        """Get the user's full name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.display_name:
            return self.display_name
        else:
            return self.email
    
    def get_role_display(self) -> str:
        """Get the display name for the user's role."""
        return self.ROLES.get(self.role, self.role.title())
    
    def can_access_ticket(self, ticket) -> bool:
        """Check if user can access a specific ticket."""
        if self.role == 'admin':
            return True
        elif self.role == 'agent':
            return ticket.assigned_agent_id == self.id or ticket.creator_id == self.id
        else:  # end_user
            return ticket.creator_id == self.id
    
    def can_manage_users(self) -> bool:
        """Check if user can manage other users."""
        return self.role == 'admin'
    
    def can_manage_categories(self) -> bool:
        """Check if user can manage categories."""
        return self.role == 'admin'
    
    def can_assign_tickets(self) -> bool:
        """Check if user can assign tickets to agents."""
        return self.role in ['admin', 'agent']
    
    def can_view_analytics(self) -> bool:
        """Check if user can view analytics dashboard."""
        return self.role in ['admin', 'agent']
    
    def update_last_login(self) -> None:
        """Update the user's last login timestamp."""
        self.last_login = datetime.now(timezone.utc)
        db.session.commit()
    
    def get_stats(self) -> dict:
        """Get user statistics."""
        from apps.tickets.models import Ticket
        
        stats = {
            'tickets_created': self.tickets_created.count(),
            'tickets_assigned': self.tickets_assigned.count(),
            'comments_made': self.comments.count(),
            'votes_given': self.votes.count(),
        }
        
        if self.role in ['admin', 'agent']:
            stats['tickets_resolved'] = self.tickets_assigned.filter_by(status='resolved').count()
            stats['avg_resolution_time'] = self._calculate_avg_resolution_time()
        
        return stats
    
    def _calculate_avg_resolution_time(self) -> float:
        """Calculate average resolution time for assigned tickets."""
        from apps.tickets.models import Ticket
        
        resolved_tickets = self.tickets_assigned.filter_by(status='resolved').all()
        if not resolved_tickets:
            return 0.0
        
        total_time = 0
        for ticket in resolved_tickets:
            if ticket.resolved_at and ticket.created_at:
                total_time += (ticket.resolved_at - ticket.created_at).total_seconds()
        
        return total_time / len(resolved_tickets) / 3600  # Return hours
    
    def __repr__(self) -> str:
        return f'<User {self.email}>'


class UserProfile(db.Model):
    """Extended user profile information."""
    
    __tablename__ = 'user_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    
    # Additional profile fields
    bio = db.Column(db.Text, nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    company = db.Column(db.String(100), nullable=True)
    department = db.Column(db.String(100), nullable=True)
    location = db.Column(db.String(100), nullable=True)
    
    # Social links
    website = db.Column(db.String(255), nullable=True)
    linkedin = db.Column(db.String(255), nullable=True)
    twitter = db.Column(db.String(255), nullable=True)
    
    # Preferences
    email_notifications = db.Column(db.Boolean, default=True, nullable=False)
    in_app_notifications = db.Column(db.Boolean, default=True, nullable=False)
    weekly_digest = db.Column(db.Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationship
    user = db.relationship('User', backref=db.backref('profile', uselist=False))
    
    def __repr__(self) -> str:
        return f'<UserProfile {self.user_id}>'