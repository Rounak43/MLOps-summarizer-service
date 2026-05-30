# =============================================================================
# backend/routes/summaries.py
# Blueprint for SQL Database Historical Summaries CRUD Endpoints
# =============================================================================

from flask import Blueprint, request, jsonify, g
from auth.auth_middleware import token_required
from database.db import db
from models.summary import Summary

summaries_bp = Blueprint("summaries", __name__)

@summaries_bp.route("/api/summaries", methods=["POST"])
@token_required
def create_summary():
    """
    Save a new generated summary record to SQL database history.
    Accessible only to authenticated users (Firebase/Cognito).
    """
    data = request.get_json(silent=True) or {}
    
    # Validation
    if "summary" not in data or "title" not in data:
        return jsonify({"success": False, "error": "Missing required fields (summary, title)"}), 400

    try:
        # Create summary record
        record = Summary(
            user_id=g.user_id,
            type=data.get("type", "pdf"),
            title=data.get("title", "Untitled Analysis"),
            summary=data.get("summary", ""),
            detailed_summary=data.get("detailedSummary", ""),
            key_concepts=data.get("keyConcepts", []),
            flashcards=data.get("flashcards", []),
            quiz_questions=data.get("quizQuestions", []),
            words=int(data.get("words", 0))
        )
        
        db.session.add(record)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "id": record.id,
            "message": "Summary saved to database history successfully"
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": f"Failed to save summary: {str(e)}"}), 500


@summaries_bp.route("/api/summaries", methods=["GET"])
@token_required
def get_user_summaries():
    """
    Retrieve all historical summary records for the currently logged-in user.
    """
    try:
        # Query matching summaries ordered by created timestamp descending
        records = Summary.query.filter_by(user_id=g.user_id).order_by(Summary.created_at.desc()).all()
        return jsonify([record.to_dict() for record in records])
        
    except Exception as e:
        return jsonify({"success": False, "error": f"Failed to retrieve history: {str(e)}"}), 500


@summaries_bp.route("/api/summaries/<int:summary_id>", methods=["DELETE"])
@token_required
def delete_user_summary(summary_id):
    """
    Delete a specific historical summary record belonging to the authenticated user.
    """
    try:
        # Find matching summary record for security (ensure user owns it)
        record = Summary.query.filter_by(id=summary_id, user_id=g.user_id).first()
        
        if not record:
            return jsonify({"success": False, "error": "Record not found or unauthorized"}), 404
            
        db.session.delete(record)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Summary record deleted successfully"
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": f"Failed to delete record: {str(e)}"}), 500
