"""Ticket models for the Q-Reserve helpdesk system."""

from datetime import datetime, timezone, timedelta
from sqlalchemy import text
from core.extensions import db
from core.utils import generate_uuid


class Category(db.Model):
    """Ticket category model."""
    
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    slug = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    color = db.Column(db.String(7), default='#3B82F6')  # Hex color
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    tickets = db.relationship('Ticket', backref='category', lazy='dynamic')
    
    def __repr__(self) -> str:
        return f'<Category {self.name}>'


class Ticket(db.Model):
    """Ticket model for the helpdesk system."""
    
    __tablename__ = 'tickets'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=generate_uuid, nullable=False)
    
    # Basic information
    subject = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    
    # Status and priority
    status = db.Column(db.String(20), default='open', nullable=False, index=True)
    priority = db.Column(db.String(20), default='medium', nullable=False, index=True)
    
    # Relationships
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    assigned_agent_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    
    # AI enhancements
    ai_category = db.Column(db.String(100), nullable=True)  # AI-suggested category
    ai_priority = db.Column(db.String(20), nullable=True)   # AI-suggested priority
    ai_sentiment = db.Column(db.Float, nullable=True)       # Sentiment score
    ai_duplicate_of = db.Column(db.Integer, db.ForeignKey('tickets.id'), nullable=True)  # Duplicate ticket
    
    # SLA tracking
    sla_hours = db.Column(db.Integer, default=24, nullable=False)
    due_date = db.Column(db.DateTime, nullable=True)
    resolved_at = db.Column(db.DateTime, nullable=True)
    closed_at = db.Column(db.DateTime, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    comments = db.relationship('Comment', backref='ticket', lazy='dynamic', cascade='all, delete-orphan')
    attachments = db.relationship('Attachment', backref='ticket', lazy='dynamic', cascade='all, delete-orphan')
    votes = db.relationship('Vote', backref='ticket', lazy='dynamic', cascade='all, delete-orphan')
    notifications = db.relationship('Notification', backref='ticket', lazy='dynamic', cascade='all, delete-orphan')
    
    # Status constants
    STATUS_CHOICES = {
        'open': 'Open',
        'in_progress': 'In Progress',
        'resolved': 'Resolved',
        'closed': 'Closed',
        'cancelled': 'Cancelled'
    }
    
    # Priority constants
    PRIORITY_CHOICES = {
        'low': 'Low',
        'medium': 'Medium',
        'high': 'High',
        'urgent': 'Urgent',
        'critical': 'Critical'
    }
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.uuid:
            self.uuid = generate_uuid()
        self._calculate_due_date()
    
    def _calculate_due_date(self):
        """Calculate the due date based on SLA hours."""
        if self.sla_hours and not self.due_date:
            self.due_date = datetime.now(timezone.utc) + timedelta(hours=self.sla_hours)
    
    def get_status_display(self) -> str:
        """Get the display name for the ticket status."""
        return self.STATUS_CHOICES.get(self.status, self.status.title())
    
    def get_priority_display(self) -> str:
        """Get the display name for the ticket priority."""
        return self.PRIORITY_CHOICES.get(self.priority, self.priority.title())
    
    def is_overdue(self) -> bool:
        """Check if the ticket is overdue."""
        if not self.due_date or self.status in ['resolved', 'closed', 'cancelled']:
            return False
        return datetime.now(timezone.utc) > self.due_date
    
    def get_time_until_due(self) -> str:
        """Get time until due in human-readable format."""
        if not self.due_date:
            return "No due date"
        
        now = datetime.now(timezone.utc)
        if self.due_date < now:
            return "Overdue"
        
        diff = self.due_date - now
        if diff.days > 0:
            return f"{diff.days} day{'s' if diff.days != 1 else ''} remaining"
        elif diff.seconds >= 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours != 1 else ''} remaining"
        else:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes != 1 else ''} remaining"
    
    def can_be_accessed_by(self, user) -> bool:
        """Check if a user can access this ticket."""
        if user.role == 'admin':
            return True
        elif user.role == 'agent':
            return self.assigned_agent_id == user.id or self.creator_id == user.id
        else:  # end_user
            return self.creator_id == user.id
    
    def can_be_edited_by(self, user) -> bool:
        """Check if a user can edit this ticket."""
        if user.role == 'admin':
            return True
        elif user.role == 'agent':
            return self.assigned_agent_id == user.id
        else:  # end_user
            return self.creator_id == user.id and self.status == 'open'
    
    def assign_to(self, agent_id: int) -> None:
        """Assign ticket to an agent."""
        self.assigned_agent_id = agent_id
        self.updated_at = datetime.now(timezone.utc)
        db.session.commit()
    
    def update_status(self, status: str, user) -> None:
        """Update ticket status."""
        if status not in self.STATUS_CHOICES:
            raise ValueError("Invalid status")
        
        old_status = self.status
        self.status = status
        self.updated_at = datetime.now(timezone.utc)
        
        # Set resolved_at timestamp
        if status == 'resolved' and not self.resolved_at:
            self.resolved_at = datetime.now(timezone.utc)
        elif status == 'closed' and not self.closed_at:
            self.closed_at = datetime.now(timezone.utc)
        
        db.session.commit()
        
        # TODO: Send notification about status change
        from apps.notifications.sender import send_status_change_notification
        send_status_change_notification.delay(self.id, old_status, status, user.id)
    
    def get_vote_count(self) -> dict:
        """Get vote counts for the ticket."""
        upvotes = self.votes.filter_by(vote_type='upvote').count()
        downvotes = self.votes.filter_by(vote_type='downvote').count()
        return {'upvotes': upvotes, 'downvotes': downvotes, 'total': upvotes - downvotes}
    
    def has_user_voted(self, user_id: int) -> bool:
        """Check if a user has voted on this ticket."""
        return self.votes.filter_by(user_id=user_id).first() is not None
    
    def get_user_vote(self, user_id: int) -> str:
        """Get the vote type for a user."""
        vote = self.votes.filter_by(user_id=user_id).first()
        return vote.vote_type if vote else None
    
    def __repr__(self) -> str:
        return f'<Ticket {self.id}: {self.subject}>'


class Comment(db.Model):
    """Comment model for ticket discussions."""
    
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id'), nullable=False, index=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Content
    content = db.Column(db.Text, nullable=False)
    is_internal = db.Column(db.Boolean, default=False, nullable=False)  # Private agent notes
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    attachments = db.relationship('Attachment', backref='comment', lazy='dynamic', cascade='all, delete-orphan')
    
    def can_be_viewed_by(self, user) -> bool:
        """Check if a user can view this comment."""
        if not self.is_internal:
            return self.ticket.can_be_accessed_by(user)
        else:
            # Internal comments only visible to agents and admins
            return user.role in ['agent', 'admin']
    
    def can_be_edited_by(self, user) -> bool:
        """Check if a user can edit this comment."""
        return self.author_id == user.id and user.role in ['agent', 'admin']
    
    def __repr__(self) -> str:
        return f'<Comment {self.id} on Ticket {self.ticket_id}>'


class Attachment(db.Model):
    """Attachment model for files."""
    
    __tablename__ = 'attachments'
    
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id'), nullable=True)
    comment_id = db.Column(db.Integer, db.ForeignKey('comments.id'), nullable=True)
    
    # File information
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    mime_type = db.Column(db.String(100), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def get_file_url(self) -> str:
        """Get the URL for the file."""
        from flask import url_for
        return url_for('static', filename=f'uploads/attachments/{self.filename}')
    
    def __repr__(self) -> str:
        return f'<Attachment {self.original_filename}>'


class Vote(db.Model):
    """Vote model for ticket voting."""
    
    __tablename__ = 'votes'
    
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Vote information
    vote_type = db.Column(db.String(10), nullable=False)  # 'upvote' or 'downvote'
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Unique constraint to prevent duplicate votes
    __table_args__ = (db.UniqueConstraint('ticket_id', 'user_id', name='unique_user_ticket_vote'),)
    
    def __repr__(self) -> str:
        return f'<Vote {self.vote_type} by User {self.user_id} on Ticket {self.ticket_id}>'


class Notification(db.Model):
    """Notification model for in-app notifications."""
    
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id'), nullable=True)
    
    # Notification content
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(50), nullable=False)  # 'ticket_created', 'comment_added', etc.
    
    # Status
    is_read = db.Column(db.Boolean, default=False, nullable=False, index=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    def mark_as_read(self) -> None:
        """Mark notification as read."""
        self.is_read = True
        db.session.commit()
    
    def __repr__(self) -> str:
        return f'<Notification {self.id} for User {self.user_id}>'