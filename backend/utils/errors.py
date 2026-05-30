# =============================================================================
# backend/utils/errors.py
# Centralized API Error Handling Middleware
# =============================================================================

import traceback
from flask import jsonify
from werkzeug.exceptions import HTTPException

def register_error_handlers(app):
    """Register application-wide JSON error handlers"""
    
    @app.errorhandler(ValueError)
    def handle_value_error(e):
        """Handle validation value mismatches"""
        app.logger.warning(f"Validation failure: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400

    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        """Handle standard HTTP exceptions (e.g. 404, 405)"""
        return jsonify({
            "success": False,
            "error": e.description
        }), e.code

    @app.errorhandler(Exception)
    def handle_generic_exception(e):
        """Catch-all for unexpected database, network or logic exceptions"""
        app.logger.error(f"Unhandled Exception: {str(e)}\n{traceback.format_exc()}")
        return jsonify({
            "success": False,
            "error": "An unexpected internal server error occurred"
        }), 500
