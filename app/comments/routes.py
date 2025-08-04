from flask import Blueprint, request, jsonify, redirect, url_for, flash
from app.extensions import db
from app.models import Comment, Ticket
from app.utils import jwt_required_with_user, can_access_ticket
from app.notifications.email import send_new_comment_email
import json

comments_bp = Blueprint('comments', __name__)

@comments_bp.route('/create', methods=['POST'])
@jwt_required_with_user
def create_comment(user):
    """Create a new comment on a ticket"""
    try:
        # Handle both JSON and form data
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()
        
        ticket_id = data.get('ticket_id', type=int)
        content = data.get('content', '').strip()
        parent_id = data.get('parent_id', type=int) or None
        is_internal = data.get('is_internal', False)
        
        # Validation
        if not ticket_id or not content:
            error = 'Ticket ID and content are required'
            if request.is_json:
                return jsonify({'error': error}), 400
            flash(error, 'error')
            return redirect(url_for('tickets.view_ticket', ticket_id=ticket_id))
        
        # Verify ticket exists and user can access it
        ticket = Ticket.query.get(ticket_id)
        if not ticket:
            error = 'Ticket not found'
            if request.is_json:
                return jsonify({'error': error}), 404
            flash(error, 'error')
            return redirect(url_for('tickets.list_tickets'))
        
        if not can_access_ticket(user, ticket):
            error = 'Access denied'
            if request.is_json:
                return jsonify({'error': error}), 403
            flash(error, 'error')
            return redirect(url_for('tickets.list_tickets'))
        
        # Only agents and admins can create internal comments
        if is_internal and user.role not in ['agent', 'admin']:
            is_internal = False
        
        # Verify parent comment exists if specified
        if parent_id:
            parent_comment = Comment.query.get(parent_id)
            if not parent_comment or parent_comment.ticket_id != ticket_id:
                parent_id = None
        
        # Create comment
        comment = Comment(
            content=content,
            ticket_id=ticket_id,
            user_id=user.id,
            parent_id=parent_id,
            is_internal=is_internal
        )
        
        db.session.add(comment)
        
        # Update ticket's updated_at timestamp
        ticket.updated_at = db.func.now()
        
        db.session.commit()
        
        # Send email notification (only for non-internal comments)
        if not is_internal:
            try:
                send_new_comment_email(ticket, comment)
            except Exception as e:
                print(f"Failed to send comment notification: {e}")
        
        if request.is_json:
            return jsonify({
                'message': 'Comment created successfully',
                'comment': comment.to_dict()
            }), 201
        
        flash('Comment added successfully!', 'success')
        return redirect(url_for('tickets.view_ticket', ticket_id=ticket_id))
        
    except Exception as e:
        db.session.rollback()
        error = 'Failed to create comment. Please try again.'
        if request.is_json:
            return jsonify({'error': error}), 500
        flash(error, 'error')
        return redirect(url_for('tickets.view_ticket', ticket_id=ticket_id) if 'ticket_id' in locals() else url_for('tickets.list_tickets'))

@comments_bp.route('/<int:comment_id>/update', methods=['POST'])
@jwt_required_with_user
def update_comment(user, comment_id):
    """Update a comment (only by the author or admin)"""
    try:
        comment = Comment.query.get_or_404(comment_id)
        
        # Check permissions - only comment author or admin can edit
        if comment.user_id != user.id and user.role != 'admin':
            if request.is_json:
                return jsonify({'error': 'Access denied'}), 403
            flash('You can only edit your own comments.', 'error')
            return redirect(url_for('tickets.view_ticket', ticket_id=comment.ticket_id))
        
        # Handle both JSON and form data
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()
        
        content = data.get('content', '').strip()
        
        if not content:
            error = 'Content is required'
            if request.is_json:
                return jsonify({'error': error}), 400
            flash(error, 'error')
            return redirect(url_for('tickets.view_ticket', ticket_id=comment.ticket_id))
        
        comment.content = content
        comment.updated_at = db.func.now()
        
        db.session.commit()
        
        if request.is_json:
            return jsonify({
                'message': 'Comment updated successfully',
                'comment': comment.to_dict()
            }), 200
        
        flash('Comment updated successfully!', 'success')
        return redirect(url_for('tickets.view_ticket', ticket_id=comment.ticket_id))
        
    except Exception as e:
        db.session.rollback()
        error = 'Failed to update comment. Please try again.'
        if request.is_json:
            return jsonify({'error': error}), 500
        flash(error, 'error')
        return redirect(url_for('tickets.view_ticket', ticket_id=comment.ticket_id) if 'comment' in locals() else url_for('tickets.list_tickets'))

@comments_bp.route('/<int:comment_id>/delete', methods=['POST'])
@jwt_required_with_user
def delete_comment(user, comment_id):
    """Delete a comment (only by the author or admin)"""
    try:
        comment = Comment.query.get_or_404(comment_id)
        ticket_id = comment.ticket_id
        
        # Check permissions - only comment author or admin can delete
        if comment.user_id != user.id and user.role != 'admin':
            if request.is_json:
                return jsonify({'error': 'Access denied'}), 403
            flash('You can only delete your own comments.', 'error')
            return redirect(url_for('tickets.view_ticket', ticket_id=ticket_id))
        
        # Note: We don't actually delete comments to preserve thread integrity
        # Instead, we mark them as deleted by setting content to a placeholder
        comment.content = "[This comment has been deleted]"
        comment.updated_at = db.func.now()
        
        db.session.commit()
        
        if request.is_json:
            return jsonify({'message': 'Comment deleted successfully'}), 200
        
        flash('Comment deleted successfully!', 'success')
        return redirect(url_for('tickets.view_ticket', ticket_id=ticket_id))
        
    except Exception as e:
        db.session.rollback()
        error = 'Failed to delete comment. Please try again.'
        if request.is_json:
            return jsonify({'error': error}), 500
        flash(error, 'error')
        return redirect(url_for('tickets.view_ticket', ticket_id=comment.ticket_id) if 'comment' in locals() else url_for('tickets.list_tickets'))