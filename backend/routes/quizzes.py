# =============================================================================
# backend/routes/quizzes.py
# Blueprint for MCQ Quiz Generation Endpoints
# =============================================================================

from flask import Blueprint, request, jsonify
from quizzes.quiz_generator import generate_quiz_questions
from routes.summarize import _save_and_extract

quizzes_bp = Blueprint("quizzes", __name__)

@quizzes_bp.route("/api/quiz", methods=["POST"])
def generate_quiz_endpoint():
    """
    Generate multiple-choice quiz questions from an uploaded document.
    """
    if "file" not in request.files:
        return jsonify({"success": False, "error": "No file uploaded"}), 400

    file = request.files["file"]
    count = min(int(request.form.get("count", 5)), 15)

    # Extraction & clean text from file
    cleaned, ext, fname = _save_and_extract(file)
    
    # Run MCQ generator service
    questions = generate_quiz_questions(cleaned, count=count)

    return jsonify({
        "success":   True,
        "file_name": fname,
        "file_type": ext,
        "count":     len(questions),
        "questions": questions,
    })
