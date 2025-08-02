#!/usr/bin/env python3
"""Seed data script for Q-Reserve helpdesk system."""

import os
import sys
from datetime import datetime, timezone, timedelta
from werkzeug.security import generate_password_hash

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import create_app, db
from apps.users.models import User, UserProfile
from apps.tickets.models import Category, Ticket, Comment, Vote
from apps.notifications.models import Notification


def seed_categories():
    """Seed categories data."""
    categories = [
        {
            'name': 'Technical Support',
            'slug': 'technical-support',
            'description': 'Technical issues and troubleshooting',
            'color': '#3B82F6'
        },
        {
            'name': 'Billing & Payments',
            'slug': 'billing-payments',
            'description': 'Billing, payments, and account issues',
            'color': '#10B981'
        },
        {
            'name': 'Feature Requests',
            'slug': 'feature-requests',
            'description': 'New feature requests and suggestions',
            'color': '#F59E0B'
        },
        {
            'name': 'Bug Reports',
            'slug': 'bug-reports',
            'description': 'Bug reports and software issues',
            'color': '#EF4444'
        },
        {
            'name': 'General Inquiry',
            'slug': 'general-inquiry',
            'description': 'General questions and inquiries',
            'color': '#8B5CF6'
        },
        {
            'name': 'Account Management',
            'slug': 'account-management',
            'description': 'Account setup, changes, and management',
            'color': '#06B6D4'
        }
    ]
    
    for cat_data in categories:
        category = Category.query.filter_by(slug=cat_data['slug']).first()
        if not category:
            category = Category(**cat_data)
            db.session.add(category)
    
    db.session.commit()
    print(f"✅ Seeded {len(categories)} categories")


def seed_users():
    """Seed users data."""
    users_data = [
        {
            'email': 'admin@qreserve.com',
            'password': 'admin123',
            'first_name': 'Admin',
            'last_name': 'User',
            'display_name': 'System Administrator',
            'role': 'admin',
            'is_active': True,
            'is_verified': True
        },
        {
            'email': 'agent1@qreserve.com',
            'password': 'agent123',
            'first_name': 'Sarah',
            'last_name': 'Johnson',
            'display_name': 'Sarah Johnson',
            'role': 'agent',
            'is_active': True,
            'is_verified': True
        },
        {
            'email': 'agent2@qreserve.com',
            'password': 'agent123',
            'first_name': 'Michael',
            'last_name': 'Chen',
            'display_name': 'Michael Chen',
            'role': 'agent',
            'is_active': True,
            'is_verified': True
        },
        {
            'email': 'user1@example.com',
            'password': 'user123',
            'first_name': 'John',
            'last_name': 'Doe',
            'display_name': 'John Doe',
            'role': 'end_user',
            'is_active': True,
            'is_verified': True
        },
        {
            'email': 'user2@example.com',
            'password': 'user123',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'display_name': 'Jane Smith',
            'role': 'end_user',
            'is_active': True,
            'is_verified': True
        },
        {
            'email': 'user3@example.com',
            'password': 'user123',
            'first_name': 'Bob',
            'last_name': 'Wilson',
            'display_name': 'Bob Wilson',
            'role': 'end_user',
            'is_active': True,
            'is_verified': True
        }
    ]
    
    for user_data in users_data:
        user = User.query.filter_by(email=user_data['email']).first()
        if not user:
            user = User(
                email=user_data['email'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                display_name=user_data['display_name'],
                role=user_data['role'],
                is_active=user_data['is_active'],
                is_verified=user_data['is_verified']
            )
            user.set_password(user_data['password'])
            db.session.add(user)
            
            # Create user profile
            profile = UserProfile(user=user)
            db.session.add(profile)
    
    db.session.commit()
    print(f"✅ Seeded {len(users_data)} users")


def seed_tickets():
    """Seed tickets data."""
    # Get users and categories
    admin = User.query.filter_by(email='admin@qreserve.com').first()
    agent1 = User.query.filter_by(email='agent1@qreserve.com').first()
    agent2 = User.query.filter_by(email='agent2@qreserve.com').first()
    user1 = User.query.filter_by(email='user1@example.com').first()
    user2 = User.query.filter_by(email='user2@example.com').first()
    user3 = User.query.filter_by(email='user3@example.com').first()
    
    tech_support = Category.query.filter_by(slug='technical-support').first()
    billing = Category.query.filter_by(slug='billing-payments').first()
    feature_requests = Category.query.filter_by(slug='feature-requests').first()
    bug_reports = Category.query.filter_by(slug='bug-reports').first()
    general = Category.query.filter_by(slug='general-inquiry').first()
    
    tickets_data = [
        {
            'subject': 'Cannot login to my account',
            'description': 'I\'m trying to login to my account but I keep getting an error message. I\'ve tried resetting my password but it\'s still not working.',
            'category': tech_support,
            'creator': user1,
            'assigned_agent': agent1,
            'status': 'in_progress',
            'priority': 'high',
            'created_at': datetime.now(timezone.utc) - timedelta(days=2)
        },
        {
            'subject': 'Billing issue - charged twice',
            'description': 'I was charged twice for my subscription this month. I can see two charges on my credit card statement.',
            'category': billing,
            'creator': user2,
            'assigned_agent': agent2,
            'status': 'open',
            'priority': 'urgent',
            'created_at': datetime.now(timezone.utc) - timedelta(hours=6)
        },
        {
            'subject': 'Feature request: Dark mode',
            'description': 'I would love to see a dark mode option for the application. It would be much easier on the eyes, especially when working late at night.',
            'category': feature_requests,
            'creator': user3,
            'assigned_agent': None,
            'status': 'open',
            'priority': 'medium',
            'created_at': datetime.now(timezone.utc) - timedelta(days=1)
        },
        {
            'subject': 'App crashes on iOS 17',
            'description': 'The mobile app crashes immediately when I try to open it on my iPhone with iOS 17. This started happening after the latest update.',
            'category': bug_reports,
            'creator': user1,
            'assigned_agent': agent1,
            'status': 'resolved',
            'priority': 'critical',
            'created_at': datetime.now(timezone.utc) - timedelta(days=5),
            'resolved_at': datetime.now(timezone.utc) - timedelta(days=3)
        },
        {
            'subject': 'How to export my data?',
            'description': 'I need to export all my data for backup purposes. Is there a way to do this through the interface?',
            'category': general,
            'creator': user2,
            'assigned_agent': agent2,
            'status': 'closed',
            'priority': 'low',
            'created_at': datetime.now(timezone.utc) - timedelta(days=7),
            'resolved_at': datetime.now(timezone.utc) - timedelta(days=6),
            'closed_at': datetime.now(timezone.utc) - timedelta(days=6)
        },
        {
            'subject': 'Performance issues on large datasets',
            'description': 'The application becomes very slow when working with large datasets. It takes several minutes to load and process data.',
            'category': bug_reports,
            'creator': user3,
            'assigned_agent': agent1,
            'status': 'open',
            'priority': 'high',
            'created_at': datetime.now(timezone.utc) - timedelta(hours=12)
        }
    ]
    
    for ticket_data in tickets_data:
        ticket = Ticket(
            subject=ticket_data['subject'],
            description=ticket_data['description'],
            category=ticket_data['category'],
            creator=ticket_data['creator'],
            assigned_agent=ticket_data['assigned_agent'],
            status=ticket_data['status'],
            priority=ticket_data['priority'],
            created_at=ticket_data['created_at']
        )
        
        if 'resolved_at' in ticket_data:
            ticket.resolved_at = ticket_data['resolved_at']
        if 'closed_at' in ticket_data:
            ticket.closed_at = ticket_data['closed_at']
        
        db.session.add(ticket)
    
    db.session.commit()
    print(f"✅ Seeded {len(tickets_data)} tickets")


def seed_comments():
    """Seed comments data."""
    tickets = Ticket.query.all()
    users = User.query.all()
    
    comments_data = [
        {
            'ticket': tickets[0],  # Cannot login to my account
            'author': users[3],  # agent1
            'content': 'I can see the issue in our logs. It appears to be related to a recent security update. Let me investigate further.',
            'is_internal': False,
            'created_at': datetime.now(timezone.utc) - timedelta(days=1, hours=12)
        },
        {
            'ticket': tickets[0],
            'author': users[0],  # user1
            'content': 'Thank you for looking into this. I\'m still unable to access my account.',
            'is_internal': False,
            'created_at': datetime.now(timezone.utc) - timedelta(days=1, hours=6)
        },
        {
            'ticket': tickets[1],  # Billing issue
            'author': users[4],  # agent2
            'content': 'I can see the duplicate charge in our system. I\'ve initiated a refund for the second charge. You should see it in your account within 3-5 business days.',
            'is_internal': False,
            'created_at': datetime.now(timezone.utc) - timedelta(hours=4)
        },
        {
            'ticket': tickets[2],  # Feature request
            'author': users[3],  # agent1
            'content': 'This is a great suggestion! I\'ve added it to our feature roadmap. We\'re planning to implement dark mode in the next major release.',
            'is_internal': False,
            'created_at': datetime.now(timezone.utc) - timedelta(hours=18)
        },
        {
            'ticket': tickets[3],  # App crashes
            'author': users[3],  # agent1
            'content': 'We\'ve identified and fixed the iOS 17 compatibility issue. The fix will be available in version 2.1.3, which should be released tomorrow.',
            'is_internal': False,
            'created_at': datetime.now(timezone.utc) - timedelta(days=4)
        },
        {
            'ticket': tickets[4],  # Export data
            'author': users[4],  # agent2
            'content': 'You can export your data by going to Settings > Data Export. This will generate a ZIP file with all your data in JSON format.',
            'is_internal': False,
            'created_at': datetime.now(timezone.utc) - timedelta(days=6, hours=2)
        }
    ]
    
    for comment_data in comments_data:
        comment = Comment(
            ticket=comment_data['ticket'],
            author=comment_data['author'],
            content=comment_data['content'],
            is_internal=comment_data['is_internal'],
            created_at=comment_data['created_at']
        )
        db.session.add(comment)
    
    db.session.commit()
    print(f"✅ Seeded {len(comments_data)} comments")


def seed_votes():
    """Seed votes data."""
    tickets = Ticket.query.all()
    users = User.query.filter_by(role='end_user').all()
    
    votes_data = [
        # User votes on tickets
        {'ticket': tickets[2], 'user': users[0], 'vote_type': 'upvote'},  # Feature request
        {'ticket': tickets[2], 'user': users[1], 'vote_type': 'upvote'},
        {'ticket': tickets[2], 'user': users[2], 'vote_type': 'upvote'},
        {'ticket': tickets[5], 'user': users[0], 'vote_type': 'upvote'},  # Performance issue
        {'ticket': tickets[5], 'user': users[1], 'vote_type': 'upvote'},
        {'ticket': tickets[0], 'user': users[1], 'vote_type': 'downvote'},  # Login issue
    ]
    
    for vote_data in votes_data:
        # Check if user already voted on this ticket
        existing_vote = Vote.query.filter_by(
            ticket_id=vote_data['ticket'].id,
            user_id=vote_data['user'].id
        ).first()
        
        if not existing_vote:
            vote = Vote(
                ticket=vote_data['ticket'],
                user=vote_data['user'],
                vote_type=vote_data['vote_type']
            )
            db.session.add(vote)
    
    db.session.commit()
    print(f"✅ Seeded votes")


def seed_notifications():
    """Seed notifications data."""
    users = User.query.all()
    tickets = Ticket.query.all()
    
    notifications_data = [
        {
            'user': users[3],  # agent1
            'ticket': tickets[0],
            'title': 'New ticket assigned',
            'message': 'You have been assigned to ticket: Cannot login to my account',
            'notification_type': 'ticket_assigned',
            'created_at': datetime.now(timezone.utc) - timedelta(days=2)
        },
        {
            'user': users[4],  # agent2
            'ticket': tickets[1],
            'title': 'New ticket assigned',
            'message': 'You have been assigned to ticket: Billing issue - charged twice',
            'notification_type': 'ticket_assigned',
            'created_at': datetime.now(timezone.utc) - timedelta(hours=6)
        },
        {
            'user': users[0],  # user1
            'ticket': tickets[0],
            'title': 'Comment added',
            'message': 'Sarah Johnson added a comment to your ticket: Cannot login to my account',
            'notification_type': 'comment_added',
            'created_at': datetime.now(timezone.utc) - timedelta(days=1, hours=12)
        },
        {
            'user': users[1],  # user2
            'ticket': tickets[1],
            'title': 'Status updated',
            'message': 'Your ticket "Billing issue - charged twice" has been updated',
            'notification_type': 'status_changed',
            'created_at': datetime.now(timezone.utc) - timedelta(hours=4)
        }
    ]
    
    for notification_data in notifications_data:
        notification = Notification(
            user=notification_data['user'],
            ticket=notification_data['ticket'],
            title=notification_data['title'],
            message=notification_data['message'],
            notification_type=notification_data['notification_type'],
            created_at=notification_data['created_at']
        )
        db.session.add(notification)
    
    db.session.commit()
    print(f"✅ Seeded {len(notifications_data)} notifications")


def seed_all():
    """Seed all data."""
    print("🌱 Starting database seeding...")
    
    try:
        seed_categories()
        seed_users()
        seed_tickets()
        seed_comments()
        seed_votes()
        seed_notifications()
        
        print("✅ Database seeding completed successfully!")
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.session.rollback()
        raise


if __name__ == '__main__':
    app = create_app('development')
    with app.app_context():
        seed_all()