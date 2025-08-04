import bcrypt
from flask import current_app

def hash_password(password):
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(password, password_hash):
    """Check password against hash"""
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

def is_valid_role(role):
    """Check if role is valid"""
    valid_roles = ['end_user', 'agent', 'admin']
    return role in valid_roles

def get_role_permissions(role):
    """Get permissions for a role"""
    permissions = {
        'end_user': [
            'create_ticket',
            'view_own_tickets',
            'comment_on_own_tickets',
            'vote_on_tickets'
        ],
        'agent': [
            'create_ticket',
            'view_own_tickets',
            'view_all_tickets',
            'comment_on_tickets',
            'modify_ticket_status',
            'assign_tickets',
            'vote_on_tickets'
        ],
        'admin': [
            'create_ticket',
            'view_own_tickets',
            'view_all_tickets',
            'comment_on_tickets',
            'modify_ticket_status',
            'assign_tickets',
            'vote_on_tickets',
            'manage_categories',
            'manage_users',
            'view_audit_logs'
        ]
    }
    return permissions.get(role, [])