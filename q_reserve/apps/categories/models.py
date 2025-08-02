"""
Category models for Q-Reserve application.

This module defines the Category model for organizing and classifying tickets.
"""

from datetime import datetime
from core.extensions import db


class Category(db.Model):
    """Category model for organizing tickets."""
    
    __tablename__ = 'categories'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Basic information
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    color = db.Column(db.String(7), default='#007bff')  # Hex color code
    icon = db.Column(db.String(50), default='folder')  # Icon class name
    
    # Organization
    parent_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    sort_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tickets = db.relationship('Ticket', backref='category', lazy='dynamic')
    children = db.relationship('Category', 
                             backref=db.backref('parent', remote_side=[id]),
                             lazy='dynamic')
    
    def __init__(self, **kwargs):
        """Initialize category with default values."""
        super(Category, self).__init__(**kwargs)
        if not self.color:
            self.color = '#007bff'
        if not self.icon:
            self.icon = 'folder'
    
    @property
    def ticket_count(self):
        """Get number of tickets in this category."""
        return self.tickets.count()
    
    @property
    def active_ticket_count(self):
        """Get number of active tickets in this category."""
        from apps.tickets.models import TicketStatus
        return self.tickets.filter(
            ~db.and_(
                db.or_(
                    db.text("status = 'resolved'"),
                    db.text("status = 'closed'")
                )
            )
        ).count()
    
    @property
    def full_path(self):
        """Get full category path (for nested categories)."""
        if self.parent:
            return f"{self.parent.full_path} > {self.name}"
        return self.name
    
    def get_all_children(self):
        """Get all child categories recursively."""
        children = []
        for child in self.children:
            children.append(child)
            children.extend(child.get_all_children())
        return children
    
    def can_be_deleted(self):
        """Check if category can be safely deleted."""
        # Cannot delete if it has tickets or child categories
        return self.ticket_count == 0 and self.children.count() == 0
    
    def to_dict(self):
        """Convert category to dictionary for API responses."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'color': self.color,
            'icon': self.icon,
            'parent_id': self.parent_id,
            'sort_order': self.sort_order,
            'is_active': self.is_active,
            'ticket_count': self.ticket_count,
            'active_ticket_count': self.active_ticket_count,
            'full_path': self.full_path,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        """String representation of category."""
        return f'<Category {self.name}>'
    
    @classmethod
    def get_active_categories(cls):
        """Get all active categories ordered by sort_order and name."""
        return cls.query.filter_by(is_active=True).order_by(cls.sort_order, cls.name)
    
    @classmethod
    def get_root_categories(cls):
        """Get all root categories (no parent)."""
        return cls.query.filter_by(parent_id=None, is_active=True).order_by(cls.sort_order, cls.name)


# TODO: Add category-based permissions
# TODO: Add category templates for quick ticket creation
# TODO: Add category-specific SLA rules
# TODO: Add category analytics and reporting