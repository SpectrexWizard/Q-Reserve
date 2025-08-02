"""
Error handlers for Q-Reserve application.

This module defines custom error handlers for HTTP errors and application-specific exceptions.
"""

from flask import render_template, request, jsonify, current_app
from werkzeug.exceptions import HTTPException
import logging


class QReserveException(Exception):
    """Base exception class for Q-Reserve application."""
    
    def __init__(self, message, status_code=500, payload=None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        """Convert exception to dictionary."""
        rv = dict(self.payload or ())
        rv['message'] = self.message
        rv['status_code'] = self.status_code
        return rv


class ValidationError(QReserveException):
    """Exception for validation errors."""
    
    def __init__(self, message, field=None):
        super().__init__(message, status_code=400)
        self.field = field


class AuthenticationError(QReserveException):
    """Exception for authentication errors."""
    
    def __init__(self, message='Authentication required'):
        super().__init__(message, status_code=401)


class AuthorizationError(QReserveException):
    """Exception for authorization errors."""
    
    def __init__(self, message='Access denied'):
        super().__init__(message, status_code=403)


class ResourceNotFound(QReserveException):
    """Exception for resource not found errors."""
    
    def __init__(self, message='Resource not found', resource_type=None):
        super().__init__(message, status_code=404)
        self.resource_type = resource_type


class ConflictError(QReserveException):
    """Exception for conflict errors."""
    
    def __init__(self, message='Resource conflict'):
        super().__init__(message, status_code=409)


class RateLimitError(QReserveException):
    """Exception for rate limit errors."""
    
    def __init__(self, message='Rate limit exceeded'):
        super().__init__(message, status_code=429)


def register_error_handlers(app):
    """Register error handlers with Flask app."""
    
    @app.errorhandler(QReserveException)
    def handle_qreserve_exception(error):
        """Handle custom Q-Reserve exceptions."""
        current_app.logger.error(f'QReserve exception: {error.message}')
        
        if request.content_type == 'application/json' or request.is_json:
            return jsonify(error.to_dict()), error.status_code
        
        return render_template('errors/error.html',
                             error=error,
                             title=f'Error {error.status_code}'), error.status_code
    
    @app.errorhandler(400)
    def bad_request(error):
        """Handle 400 Bad Request errors."""
        current_app.logger.warning(f'Bad request: {request.url}')
        
        if request.content_type == 'application/json' or request.is_json:
            return jsonify({
                'message': 'Bad request',
                'status_code': 400
            }), 400
        
        return render_template('errors/400.html'), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        """Handle 401 Unauthorized errors."""
        current_app.logger.warning(f'Unauthorized access: {request.url}')
        
        if request.content_type == 'application/json' or request.is_json:
            return jsonify({
                'message': 'Authentication required',
                'status_code': 401
            }), 401
        
        return render_template('errors/401.html'), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        """Handle 403 Forbidden errors."""
        current_app.logger.warning(f'Forbidden access: {request.url}')
        
        if request.content_type == 'application/json' or request.is_json:
            return jsonify({
                'message': 'Access forbidden',
                'status_code': 403
            }), 403
        
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 Not Found errors."""
        current_app.logger.info(f'Not found: {request.url}')
        
        if request.content_type == 'application/json' or request.is_json:
            return jsonify({
                'message': 'Resource not found',
                'status_code': 404
            }), 404
        
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        """Handle 405 Method Not Allowed errors."""
        current_app.logger.warning(f'Method not allowed: {request.method} {request.url}')
        
        if request.content_type == 'application/json' or request.is_json:
            return jsonify({
                'message': 'Method not allowed',
                'status_code': 405
            }), 405
        
        return render_template('errors/405.html'), 405
    
    @app.errorhandler(429)
    def rate_limit_exceeded(error):
        """Handle 429 Rate Limit Exceeded errors."""
        current_app.logger.warning(f'Rate limit exceeded: {request.url}')
        
        if request.content_type == 'application/json' or request.is_json:
            return jsonify({
                'message': 'Rate limit exceeded',
                'status_code': 429
            }), 429
        
        return render_template('errors/429.html'), 429
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 Internal Server Error."""
        current_app.logger.error(f'Server error: {error}', exc_info=True)
        
        if request.content_type == 'application/json' or request.is_json:
            return jsonify({
                'message': 'Internal server error',
                'status_code': 500
            }), 500
        
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(503)
    def service_unavailable(error):
        """Handle 503 Service Unavailable errors."""
        current_app.logger.error(f'Service unavailable: {error}')
        
        if request.content_type == 'application/json' or request.is_json:
            return jsonify({
                'message': 'Service temporarily unavailable',
                'status_code': 503
            }), 503
        
        return render_template('errors/503.html'), 503


# TODO: Add custom error pages with user-friendly messages
# TODO: Add error reporting to external services (Sentry, etc.)
# TODO: Add error rate monitoring and alerting