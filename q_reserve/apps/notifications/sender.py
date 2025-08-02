"""
Notification sender functions for Q-Reserve.

This module handles sending various types of notifications including emails.
"""

from flask import current_app, url_for, render_template
from flask_mail import Message
from core.extensions import mail


def send_welcome_email(user):
    """
    Send welcome email to new user.
    
    Args:
        user: User object
    """
    if not current_app.config.get('ENABLE_EMAIL_NOTIFICATIONS', True):
        current_app.logger.info(f"Email notifications disabled, skipping welcome email for {user.email}")
        return
    
    subject = "Welcome to Q-Reserve!"
    
    # Generate verification URL if user has verification token
    verification_url = None
    if user.email_verification_token:
        verification_url = url_for('auth.verify_email', 
                                 token=user.email_verification_token, 
                                 _external=True)
    
    # Render email templates
    html_body = render_template('emails/welcome.html', 
                               user=user, 
                               verification_url=verification_url)
    
    text_body = f"""
    Welcome to Q-Reserve, {user.display_name}!
    
    Thank you for creating an account with Q-Reserve. You can now:
    - Create and manage support tickets
    - Track ticket progress
    - Communicate with our support team
    
    {'Please verify your email address by visiting: ' + verification_url if verification_url else ''}
    
    If you have any questions, feel free to contact our support team.
    
    Best regards,
    Q-Reserve Team
    """
    
    try:
        msg = Message(
            subject=subject,
            recipients=[user.email],
            html=html_body,
            body=text_body
        )
        mail.send(msg)
        current_app.logger.info(f"Welcome email sent to {user.email}")
        
    except Exception as e:
        current_app.logger.error(f"Failed to send welcome email to {user.email}: {e}")
        raise


def send_ticket_notification(ticket, action, recipient_user):
    """
    Send ticket-related notification email.
    
    Args:
        ticket: Ticket object
        action: Action type (created, updated, assigned, etc.)
        recipient_user: User to receive notification
    """
    if not current_app.config.get('ENABLE_EMAIL_NOTIFICATIONS', True):
        return
    
    if not recipient_user.email_notifications:
        return
    
    # TODO: Implement ticket notification emails
    current_app.logger.info(f"TODO: Send {action} notification for ticket {ticket.id} to {recipient_user.email}")


def send_comment_notification(comment, recipient_user):
    """
    Send notification for new comment on ticket.
    
    Args:
        comment: Comment object
        recipient_user: User to receive notification
    """
    if not current_app.config.get('ENABLE_EMAIL_NOTIFICATIONS', True):
        return
    
    if not recipient_user.email_notifications:
        return
    
    # TODO: Implement comment notification emails
    current_app.logger.info(f"TODO: Send comment notification for ticket {comment.ticket_id} to {recipient_user.email}")


def send_status_change_notification(ticket, old_status, new_status, recipient_user):
    """
    Send notification for ticket status change.
    
    Args:
        ticket: Ticket object
        old_status: Previous status
        new_status: New status
        recipient_user: User to receive notification
    """
    if not current_app.config.get('ENABLE_EMAIL_NOTIFICATIONS', True):
        return
    
    if not recipient_user.email_notifications:
        return
    
    # TODO: Implement status change notification emails
    current_app.logger.info(f"TODO: Send status change notification for ticket {ticket.id} to {recipient_user.email}")


# TODO: Add SMS notifications
# TODO: Add push notifications
# TODO: Add Slack/Teams integration
# TODO: Add bulk notification functions