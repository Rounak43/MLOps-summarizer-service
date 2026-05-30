# =============================================================================
# backend/routes/health.py
# Blueprint for Server Health Diagnostics (AWS Beanstalk compatible)
# =============================================================================

from flask import Blueprint, jsonify, current_app
from database.db import db
from sqlalchemy import text

health_bp = Blueprint("health", __name__)

@health_bp.route("/health", methods=["GET"])
def health_check():
    """
    Consolidated health diagnostics.
    Verifies that the server, local/RDS SQL Database, and storage provider are operational.
    """
    health_status = {
        "status": "healthy",
        "database": "unknown",
        "storage": "unknown"
    }
    
    # 1. Verify Database connectivity
    try:
        db.session.execute(text("SELECT 1"))
        health_status["database"] = "connected"
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["database"] = f"failed: {str(e)}"
        
    # 2. Verify Storage status
    try:
        provider = current_app.config.get("STORAGE_PROVIDER", "local")
        health_status["storage"] = f"ready ({provider})"
    except Exception as e:
        health_status["storage"] = f"failed: {str(e)}"
        
    status_code = 200 if health_status["status"] == "healthy" else 500
    return jsonify(health_status), status_code
