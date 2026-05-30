# =============================================================================
# backend/routes/flashcards.py
# Blueprint for Active Recall Flashcard Endpoints
# =============================================================================

from flask import Blueprint, request, jsonify
from flashcards.flashcard_generator import generate_flashcards
from routes.summarize import _save_and_extract

flashcards_bp = Blueprint("flashcards", __name__)

@flashcards_bp.route("/api/flashcards", methods=["POST"])
def generate_flashcards_endpoint():
    """
    Generate active recall Q&A flashcards from an uploaded document.
    """
    if "file" not in request.files:
        return jsonify({"success": False, "error": "No file uploaded"}), 400

    file = request.files["file"]
    count = min(int(request.form.get("count", 10)), 20)
    use_transformer = request.form.get("use_transformer", "false").lower() == "true"

    # Extraction & clean text from file
    cleaned, ext, fname = _save_and_extract(file)
    
    # Run flashcard generator service
    flashcards = generate_flashcards(cleaned, count=count, use_transformer=use_transformer)

    return jsonify({
        "success":    True,
        "file_name":  fname,
        "file_type":  ext,
        "count":      len(flashcards),
        "flashcards": flashcards,
    })
