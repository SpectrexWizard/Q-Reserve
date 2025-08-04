import os
from datetime import datetime
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, current_app
from sqlalchemy import or_, desc, asc
from app.extensions import db
from app.models import Ticket, Category, User, AuditLog, Attachment
from app.utils import jwt_required_with_user, can_access_ticket, can_modify_ticket, validate_file_upload, sanitize_filename
from app.notifications.email import send_ticket_created_email, send_status_changed_email
import json

tickets_bp = Blueprint('tickets', __name__)

@tickets_bp.route('/')
@jwt_required_with_user
def list_tickets(user):
    """List tickets with filtering and search"""
    try:
        # Get query parameters
        status = request.args.get('status', '')
        category_id = request.args.get('category_id', '', type=int)
        search = request.args.get('search', '')
        sort_by = request.args.get('sort_by', 'updated_at')
        sort_order = request.args.get('sort_order', 'desc')
        page = request.args.get('page', 1, type=int)
        per_page = 20
        
        # Build query
        query = Ticket.query
        
        # Role-based filtering
        if user.role == 'end_user':
            query = query.filter(Ticket.user_id == user.id)
        elif user.role == 'agent':
            # Agents can see all tickets or filter by assigned to them
            assigned_filter = request.args.get('assigned_to_me', '')
            if assigned_filter:
                query = query.filter(Ticket.assigned_to == user.id)
        # Admins can see all tickets without filtering
        
        # Apply filters
        if status:
            query = query.filter(Ticket.status == status)
        
        if category_id:
            query = query.filter(Ticket.category_id == category_id)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Ticket.subject.ilike(search_term),
                    Ticket.description.ilike(search_term)
                )
            )
        
        # Apply sorting
        if sort_by == 'created_at':
            sort_column = Ticket.created_at
        elif sort_by == 'updated_at':
            sort_column = Ticket.updated_at
        elif sort_by == 'status':
            sort_column = Ticket.status
        elif sort_by == 'priority':
            sort_column = Ticket.priority
        else:
            sort_column = Ticket.updated_at
        
        if sort_order == 'asc':
            query = query.order_by(asc(sort_column))
        else:
            query = query.order_by(desc(sort_column))
        
        # Paginate
        tickets_pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        tickets = tickets_pagination.items
        
        # Get categories for filter dropdown
        categories = Category.query.filter_by(is_active=True).all()
        
        if request.is_json:
            return jsonify({
                'tickets': [ticket.to_dict() for ticket in tickets],
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': tickets_pagination.total,
                    'pages': tickets_pagination.pages,
                    'has_next': tickets_pagination.has_next,
                    'has_prev': tickets_pagination.has_prev
                },
                'categories': [cat.to_dict() for cat in categories]
            }), 200
        
        return render_template('tickets/list.html', 
                             tickets=tickets, 
                             pagination=tickets_pagination,
                             categories=categories,
                             user=user,
                             current_filters={
                                 'status': status,
                                 'category_id': category_id,
                                 'search': search,
                                 'sort_by': sort_by,
                                 'sort_order': sort_order
                             })
    
    except Exception as e:
        if request.is_json:
            return jsonify({'error': 'Failed to list tickets'}), 500
        flash('Failed to load tickets.', 'error')
        return render_template('tickets/list.html', tickets=[], categories=[], user=user)

@tickets_bp.route('/create', methods=['GET', 'POST'])
@jwt_required_with_user
def create_ticket(user):
    """Create a new ticket"""
    if request.method == 'GET':
        categories = Category.query.filter_by(is_active=True).all()
        return render_template('tickets/create.html', categories=categories, user=user)
    
    try:
        # Handle both JSON and form data
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()
        
        subject = data.get('subject', '').strip()
        description = data.get('description', '').strip()
        category_id = data.get('category_id', type=int)
        priority = data.get('priority', 'medium')
        
        # Validation
        if not subject or not description or not category_id:
            error = 'Subject, description, and category are required'
            if request.is_json:
                return jsonify({'error': error}), 400
            flash(error, 'error')
            categories = Category.query.filter_by(is_active=True).all()
            return render_template('tickets/create.html', categories=categories, user=user)
        
        # Validate category exists
        category = Category.query.get(category_id)
        if not category or not category.is_active:
            error = 'Invalid category selected'
            if request.is_json:
                return jsonify({'error': error}), 400
            flash(error, 'error')
            categories = Category.query.filter_by(is_active=True).all()
            return render_template('tickets/create.html', categories=categories, user=user)
        
        # Validate priority
        if priority not in ['low', 'medium', 'high', 'urgent']:
            priority = 'medium'
        
        # Create ticket
        ticket = Ticket(
            subject=subject,
            description=description,
            category_id=category_id,
            priority=priority,
            user_id=user.id,
            status='open'
        )
        
        db.session.add(ticket)
        db.session.flush()  # Get the ticket ID
        
        # Handle file upload if present
        if 'attachment' in request.files:
            file = request.files['attachment']
            if file and file.filename:
                is_valid, result = validate_file_upload(file)
                if is_valid:
                    file_info = result
                    filename = sanitize_filename(file.filename)
                    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                    
                    # Save file
                    file.save(file_path)
                    
                    # Create attachment record
                    attachment = Attachment(
                        filename=filename,
                        original_filename=file_info['filename'],
                        file_size=file_info['size'],
                        mime_type=file_info['mime_type'],
                        file_path=file_path,
                        ticket_id=ticket.id,
                        user_id=user.id
                    )
                    db.session.add(attachment)
        
        # Create audit log
        audit_log = AuditLog(
            action='created',
            details=json.dumps({
                'subject': subject,
                'category': category.name,
                'priority': priority
            }),
            ticket_id=ticket.id,
            user_id=user.id
        )
        db.session.add(audit_log)
        
        db.session.commit()
        
        # Send email notification
        try:
            send_ticket_created_email(ticket)
        except Exception as e:
            print(f"Failed to send email notification: {e}")
        
        if request.is_json:
            return jsonify({
                'message': 'Ticket created successfully',
                'ticket': ticket.to_dict()
            }), 201
        
        flash('Ticket created successfully!', 'success')
        return redirect(url_for('tickets.view_ticket', ticket_id=ticket.id))
        
    except Exception as e:
        db.session.rollback()
        error = 'Failed to create ticket. Please try again.'
        if request.is_json:
            return jsonify({'error': error}), 500
        flash(error, 'error')
        categories = Category.query.filter_by(is_active=True).all()
        return render_template('tickets/create.html', categories=categories, user=user)

@tickets_bp.route('/<int:ticket_id>')
@jwt_required_with_user
def view_ticket(user, ticket_id):
    """View ticket details"""
    try:
        ticket = Ticket.query.get_or_404(ticket_id)
        
        # Check access permissions
        if not can_access_ticket(user, ticket):
            if request.is_json:
                return jsonify({'error': 'Access denied'}), 403
            flash('You do not have permission to view this ticket.', 'error')
            return redirect(url_for('tickets.list_tickets'))
        
        # Get comments (excluding internal comments for end users)
        comments_query = ticket.comments
        if user.role == 'end_user':
            comments_query = comments_query.filter_by(is_internal=False)
        
        comments = comments_query.order_by(db.asc('created_at')).all()
        
        # Get attachments
        attachments = ticket.attachments.all()
        
        # Get agents for assignment (for agents/admins)
        agents = []
        if user.role in ['agent', 'admin']:
            agents = User.query.filter(User.role.in_(['agent', 'admin'])).all()
        
        if request.is_json:
            return jsonify({
                'ticket': ticket.to_dict(include_comments=True),
                'attachments': [att.to_dict() for att in attachments],
                'agents': [agent.to_dict() for agent in agents] if agents else []
            }), 200
        
        return render_template('tickets/detail.html', 
                             ticket=ticket, 
                             comments=comments,
                             attachments=attachments,
                             agents=agents,
                             user=user)
    
    except Exception as e:
        if request.is_json:
            return jsonify({'error': 'Ticket not found'}), 404
        flash('Ticket not found.', 'error')
        return redirect(url_for('tickets.list_tickets'))

@tickets_bp.route('/<int:ticket_id>/update', methods=['POST'])
@jwt_required_with_user
def update_ticket(user, ticket_id):
    """Update ticket status, assignment, etc."""
    try:
        ticket = Ticket.query.get_or_404(ticket_id)
        
        # Check modification permissions
        if not can_modify_ticket(user, ticket):
            if request.is_json:
                return jsonify({'error': 'Access denied'}), 403
            flash('You do not have permission to modify this ticket.', 'error')
            return redirect(url_for('tickets.view_ticket', ticket_id=ticket_id))
        
        # Handle both JSON and form data
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()
        
        old_status = ticket.status
        old_assigned_to = ticket.assigned_to
        
        # Update fields
        if 'status' in data and user.role in ['agent', 'admin']:
            new_status = data['status']
            if new_status in ['open', 'in_progress', 'resolved', 'closed']:
                ticket.status = new_status
                
                # Set timestamps based on status
                if new_status == 'resolved' and old_status != 'resolved':
                    ticket.resolved_at = datetime.utcnow()
                elif new_status == 'closed' and old_status != 'closed':
                    ticket.closed_at = datetime.utcnow()
        
        if 'assigned_to' in data and user.role in ['agent', 'admin']:
            assigned_to = data.get('assigned_to', type=int)
            if assigned_to:
                # Verify the user exists and is an agent/admin
                assignee = User.query.get(assigned_to)
                if assignee and assignee.role in ['agent', 'admin']:
                    ticket.assigned_to = assigned_to
            else:
                ticket.assigned_to = None
        
        if 'priority' in data and user.role in ['agent', 'admin']:
            priority = data['priority']
            if priority in ['low', 'medium', 'high', 'urgent']:
                ticket.priority = priority
        
        # Create audit log for changes
        changes = {}
        if ticket.status != old_status:
            changes['status'] = {'from': old_status, 'to': ticket.status}
        if ticket.assigned_to != old_assigned_to:
            changes['assigned_to'] = {'from': old_assigned_to, 'to': ticket.assigned_to}
        
        if changes:
            audit_log = AuditLog(
                action='updated',
                details=json.dumps(changes),
                ticket_id=ticket.id,
                user_id=user.id
            )
            db.session.add(audit_log)
        
        db.session.commit()
        
        # Send email notification for status changes
        if ticket.status != old_status:
            try:
                send_status_changed_email(ticket, old_status, ticket.status)
            except Exception as e:
                print(f"Failed to send status change email: {e}")
        
        if request.is_json:
            return jsonify({
                'message': 'Ticket updated successfully',
                'ticket': ticket.to_dict()
            }), 200
        
        flash('Ticket updated successfully!', 'success')
        return redirect(url_for('tickets.view_ticket', ticket_id=ticket_id))
        
    except Exception as e:
        db.session.rollback()
        error = 'Failed to update ticket. Please try again.'
        if request.is_json:
            return jsonify({'error': error}), 500
        flash(error, 'error')
        return redirect(url_for('tickets.view_ticket', ticket_id=ticket_id))