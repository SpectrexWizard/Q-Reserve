"""Error handling for the application."""

from flask import render_template, request, jsonify
from werkzeug.exceptions import HTTPException
from core.extensions import db


def register_error_handlers(app):
    """Register error handlers for the application."""
    
    @app.errorhandler(404)
    def not_found_error(error):
        if request.accept_mimetypes.accept_json and \
           not request.accept_mimetypes.accept_html:
            return jsonify({'error': 'Not found'}), 404
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        if request.accept_mimetypes.accept_json and \
           not request.accept_mimetypes.accept_html:
            return jsonify({'error': 'Internal server error'}), 500
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(403)
    def forbidden_error(error):
        if request.accept_mimetypes.accept_json and \
           not request.accept_mimetypes.accept_html:
            return jsonify({'error': 'Forbidden'}), 403
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(413)
    def too_large_error(error):
        if request.accept_mimetypes.accept_json and \
           not request.accept_mimetypes.accept_html:
            return jsonify({'error': 'File too large'}), 413
        return render_template('errors/413.html'), 413
    
    @app.errorhandler(429)
    def too_many_requests_error(error):
        if request.accept_mimetypes.accept_json and \
           not request.accept_mimetypes.accept_html:
            return jsonify({'error': 'Too many requests'}), 429
        return render_template('errors/429.html'), 429


class ValidationError(Exception):
    """Custom validation error."""
    def __init__(self, message, status_code=400, payload=None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.payload = payload
    
    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        rv['error'] = True
        return rv


class PermissionError(Exception):
    """Custom permission error."""
    def __init__(self, message="You don't have permission to perform this action"):
        super().__init__()
        self.message = message
        self.status_code = 403
    
    def to_dict(self):
        return {
            'message': self.message,
            'error': True
        }


class ResourceNotFoundError(Exception):
    """Custom resource not found error."""
    def __init__(self, message="Resource not found"):
        super().__init__()
        self.message = message
        self.status_code = 404
    
    def to_dict(self):
        return {
            'message': self.message,
            'error': True
        }