from flask import Blueprint, request, jsonify, redirect, url_for, flash
from sqlalchemy.exc import IntegrityError
from app.extensions import db
from app.models import Vote, Ticket
from app.utils import jwt_required_with_user, can_access_ticket

votes_bp = Blueprint('votes', __name__)

@votes_bp.route('/toggle', methods=['POST'])
@jwt_required_with_user
def toggle_vote(user):
    """Toggle upvote/downvote on a ticket"""
    try:
        # Handle both JSON and form data
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()
        
        ticket_id = data.get('ticket_id', type=int)
        is_upvote = data.get('is_upvote', type=bool)
        
        # Validation
        if not ticket_id or is_upvote is None:
            error = 'Ticket ID and vote type are required'
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
        
        # Check if user already has a vote on this ticket
        existing_vote = Vote.query.filter_by(
            ticket_id=ticket_id,
            user_id=user.id
        ).first()
        
        if existing_vote:
            if existing_vote.is_upvote == is_upvote:
                # Same vote type - remove the vote (toggle off)
                db.session.delete(existing_vote)
                message = 'Vote removed'
                vote_status = 'removed'
            else:
                # Different vote type - update the vote
                existing_vote.is_upvote = is_upvote
                existing_vote.updated_at = db.func.now()
                message = f'Vote changed to {"upvote" if is_upvote else "downvote"}'
                vote_status = 'changed'
        else:
            # No existing vote - create new vote
            try:
                new_vote = Vote(
                    ticket_id=ticket_id,
                    user_id=user.id,
                    is_upvote=is_upvote
                )
                db.session.add(new_vote)
                message = f'{"Upvoted" if is_upvote else "Downvoted"} successfully'
                vote_status = 'created'
            except IntegrityError:
                # Handle race condition where vote was created between check and insert
                db.session.rollback()
                error = 'Vote already exists'
                if request.is_json:
                    return jsonify({'error': error}), 400
                flash(error, 'error')
                return redirect(url_for('tickets.view_ticket', ticket_id=ticket_id))
        
        db.session.commit()
        
        # Get updated vote counts
        upvotes = Vote.query.filter_by(ticket_id=ticket_id, is_upvote=True).count()
        downvotes = Vote.query.filter_by(ticket_id=ticket_id, is_upvote=False).count()
        vote_score = upvotes - downvotes
        
        # Get user's current vote status
        user_vote = Vote.query.filter_by(ticket_id=ticket_id, user_id=user.id).first()
        user_vote_status = None
        if user_vote:
            user_vote_status = 'upvote' if user_vote.is_upvote else 'downvote'
        
        if request.is_json:
            return jsonify({
                'message': message,
                'vote_status': vote_status,
                'vote_score': vote_score,
                'upvotes': upvotes,
                'downvotes': downvotes,
                'user_vote': user_vote_status
            }), 200
        
        flash(message, 'success')
        return redirect(url_for('tickets.view_ticket', ticket_id=ticket_id))
        
    except Exception as e:
        db.session.rollback()
        error = 'Failed to process vote. Please try again.'
        if request.is_json:
            return jsonify({'error': error}), 500
        flash(error, 'error')
        return redirect(url_for('tickets.view_ticket', ticket_id=ticket_id) if 'ticket_id' in locals() else url_for('tickets.list_tickets'))

@votes_bp.route('/ticket/<int:ticket_id>')
@jwt_required_with_user
def get_ticket_votes(user, ticket_id):
    """Get vote information for a ticket"""
    try:
        # Verify ticket exists and user can access it
        ticket = Ticket.query.get(ticket_id)
        if not ticket:
            return jsonify({'error': 'Ticket not found'}), 404
        
        if not can_access_ticket(user, ticket):
            return jsonify({'error': 'Access denied'}), 403
        
        # Get vote counts
        upvotes = Vote.query.filter_by(ticket_id=ticket_id, is_upvote=True).count()
        downvotes = Vote.query.filter_by(ticket_id=ticket_id, is_upvote=False).count()
        vote_score = upvotes - downvotes
        
        # Get user's current vote
        user_vote = Vote.query.filter_by(ticket_id=ticket_id, user_id=user.id).first()
        user_vote_status = None
        if user_vote:
            user_vote_status = 'upvote' if user_vote.is_upvote else 'downvote'
        
        return jsonify({
            'ticket_id': ticket_id,
            'vote_score': vote_score,
            'upvotes': upvotes,
            'downvotes': downvotes,
            'user_vote': user_vote_status
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get vote information'}), 500