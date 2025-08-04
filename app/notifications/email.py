import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app, render_template
from jinja2 import Template

def send_email(to_email, subject, html_content, text_content=None):
    """Send email using SMTP"""
    try:
        # For development, just print to console
        if not current_app.config.get('SMTP_USERNAME') or not current_app.config.get('SMTP_PASSWORD'):
            print(f"\n=== EMAIL NOTIFICATION ===")
            print(f"To: {to_email}")
            print(f"Subject: {subject}")
            print(f"Content:\n{text_content or html_content}")
            print(f"=========================\n")
            return True
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = current_app.config['FROM_EMAIL']
        msg['To'] = to_email
        
        # Add text and HTML parts
        if text_content:
            text_part = MIMEText(text_content, 'plain')
            msg.attach(text_part)
        
        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)
        
        # Send email
        server = smtplib.SMTP(current_app.config['SMTP_SERVER'], current_app.config['SMTP_PORT'])
        if current_app.config['SMTP_USE_TLS']:
            server.starttls()
        
        server.login(current_app.config['SMTP_USERNAME'], current_app.config['SMTP_PASSWORD'])
        server.send_message(msg)
        server.quit()
        
        return True
        
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

def send_ticket_created_email(ticket):
    """Send notification when a ticket is created"""
    try:
        subject = f"Ticket #{ticket.id} Created: {ticket.subject}"
        
        # Simple text template for now
        text_content = f"""
Dear {ticket.owner.username},

Your support ticket has been created successfully.

Ticket Details:
- ID: #{ticket.id}
- Subject: {ticket.subject}
- Category: {ticket.category.name}
- Status: {ticket.status.replace('_', ' ').title()}
- Priority: {ticket.priority.title()}

You can view your ticket and add comments by logging into the helpdesk system.

Thank you,
Helpdesk Team
        """
        
        html_content = f"""
<html>
<body>
    <h2>Ticket Created Successfully</h2>
    <p>Dear {ticket.owner.username},</p>
    
    <p>Your support ticket has been created successfully.</p>
    
    <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
        <h3>Ticket Details:</h3>
        <ul>
            <li><strong>ID:</strong> #{ticket.id}</li>
            <li><strong>Subject:</strong> {ticket.subject}</li>
            <li><strong>Category:</strong> {ticket.category.name}</li>
            <li><strong>Status:</strong> {ticket.status.replace('_', ' ').title()}</li>
            <li><strong>Priority:</strong> {ticket.priority.title()}</li>
        </ul>
    </div>
    
    <p>You can view your ticket and add comments by logging into the helpdesk system.</p>
    
    <p>Thank you,<br>Helpdesk Team</p>
</body>
</html>
        """
        
        return send_email(ticket.owner.email, subject, html_content, text_content)
        
    except Exception as e:
        print(f"Failed to send ticket created email: {e}")
        return False

def send_status_changed_email(ticket, old_status, new_status):
    """Send notification when ticket status changes"""
    try:
        subject = f"Ticket #{ticket.id} Status Changed: {new_status.replace('_', ' ').title()}"
        
        text_content = f"""
Dear {ticket.owner.username},

The status of your support ticket has been updated.

Ticket Details:
- ID: #{ticket.id}
- Subject: {ticket.subject}
- Previous Status: {old_status.replace('_', ' ').title()}
- New Status: {new_status.replace('_', ' ').title()}

You can view your ticket by logging into the helpdesk system.

Thank you,
Helpdesk Team
        """
        
        html_content = f"""
<html>
<body>
    <h2>Ticket Status Updated</h2>
    <p>Dear {ticket.owner.username},</p>
    
    <p>The status of your support ticket has been updated.</p>
    
    <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
        <h3>Ticket Details:</h3>
        <ul>
            <li><strong>ID:</strong> #{ticket.id}</li>
            <li><strong>Subject:</strong> {ticket.subject}</li>
            <li><strong>Previous Status:</strong> {old_status.replace('_', ' ').title()}</li>
            <li><strong>New Status:</strong> <span style="color: #007bff; font-weight: bold;">{new_status.replace('_', ' ').title()}</span></li>
        </ul>
    </div>
    
    <p>You can view your ticket by logging into the helpdesk system.</p>
    
    <p>Thank you,<br>Helpdesk Team</p>
</body>
</html>
        """
        
        return send_email(ticket.owner.email, subject, html_content, text_content)
        
    except Exception as e:
        print(f"Failed to send status changed email: {e}")
        return False

def send_new_comment_email(ticket, comment):
    """Send notification when a new comment is added"""
    try:
        # Don't send email to the comment author
        if comment.user_id == ticket.user_id:
            return True
        
        subject = f"New Comment on Ticket #{ticket.id}: {ticket.subject}"
        
        text_content = f"""
Dear {ticket.owner.username},

A new comment has been added to your support ticket.

Ticket Details:
- ID: #{ticket.id}
- Subject: {ticket.subject}

New Comment by {comment.author.username}:
{comment.content}

You can view the full ticket and reply by logging into the helpdesk system.

Thank you,
Helpdesk Team
        """
        
        html_content = f"""
<html>
<body>
    <h2>New Comment Added</h2>
    <p>Dear {ticket.owner.username},</p>
    
    <p>A new comment has been added to your support ticket.</p>
    
    <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
        <h3>Ticket Details:</h3>
        <ul>
            <li><strong>ID:</strong> #{ticket.id}</li>
            <li><strong>Subject:</strong> {ticket.subject}</li>
        </ul>
    </div>
    
    <div style="background-color: #e9f4ff; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #007bff;">
        <h4>New Comment by {comment.author.username}:</h4>
        <p>{comment.content}</p>
    </div>
    
    <p>You can view the full ticket and reply by logging into the helpdesk system.</p>
    
    <p>Thank you,<br>Helpdesk Team</p>
</body>
</html>
        """
        
        return send_email(ticket.owner.email, subject, html_content, text_content)
        
    except Exception as e:
        print(f"Failed to send new comment email: {e}")
        return False