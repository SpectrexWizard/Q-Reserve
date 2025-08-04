from flask import render_template, jsonify, request

def register_error_handlers(app):
    """Register error handlers for the application"""
    
    @app.errorhandler(403)
    def forbidden(error):
        if request.is_json:
            return jsonify({'error': 'Forbidden - Insufficient permissions'}), 403
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(404)
    def not_found(error):
        if request.is_json:
            return jsonify({'error': 'Resource not found'}), 404
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        if request.is_json:
            return jsonify({'error': 'Internal server error'}), 500
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(413)
    def request_entity_too_large(error):
        if request.is_json:
            return jsonify({'error': 'File too large'}), 413
        return render_template('errors/500.html', 
                             error_message='File too large. Please upload a smaller file.'), 413