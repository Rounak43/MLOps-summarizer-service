# =============================================================================
# backend/routes/summarize.py
# Blueprint for Core Summarization and All-in-One Pipelines
# =============================================================================

import os
import requests
import tempfile
from flask import Blueprint, request, jsonify, current_app

# Import core summarization services
from summarization import (
    clean_text,
    is_text_valid,
    run_extractive_pipeline,
    refine_abstractively,
)

# Import other core domain services for full pipeline
from flashcards.flashcard_generator import generate_flashcards
from quizzes.quiz_generator import generate_quiz_questions

# Import validators & storage
from utils.validation import validate_uploaded_file, validate_text_input
from storage.storage_manager import get_storage_provider

summarize_bp = Blueprint("summarize", __name__)

def _save_and_extract(file) -> tuple[str, str, str]:
    """
    Save uploaded file locally or in S3, extract its text, and clean it.
    Cleans up all intermediate files automatically.
    """
    filename, ext = validate_uploaded_file(file)
    
    # Save file stream via storage provider
    storage = get_storage_provider(current_app)
    saved_identifier = storage.save(file, ext)
    
    local_path = saved_identifier
    is_s3 = saved_identifier.startswith("http")
    
    # If saved to S3, download temporarily to local temp folder for extraction
    if is_s3:
        temp_dir = tempfile.gettempdir()
        local_path = os.path.join(temp_dir, f"temp_{os.path.basename(saved_identifier)}")
        try:
            response = requests.get(saved_identifier, stream=True)
            response.raise_for_status()
            with open(local_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
        except Exception as e:
            # Clean up S3 file if it was uploaded
            storage.delete(saved_identifier)
            raise ValueError(f"Failed to fetch uploaded file from S3: {str(e)}")
            
    try:
        # Re-import dynamically to avoid circular references during init
        from summarization.extractor import extract_text
        from summarization.exceptions import ExtractionError
        raw_text = extract_text(local_path)
    except ExtractionError as e:
        raise ValueError(str(e))
    finally:
        # Clean up download if S3 was used
        if is_s3 and os.path.exists(local_path):
            try:
                os.remove(local_path)
            except OSError:
                pass
        # Clean up storage (delete uploaded PDF immediately after extraction)
        storage.delete(saved_identifier)
        
    cleaned = clean_text(raw_text)
    if not is_text_valid(cleaned):
        raise ValueError("Extracted text is too short or too noisy to process.")
        
    return cleaned, ext, filename


def _run_summary(cleaned_text: str, mode: str, ratio: float | None, use_abstractive: bool) -> dict:
    """Helper method to execute core extraction/abstractive NLP models"""
    if mode not in {"short", "medium", "long"}:
        mode = "medium"

    try:
        result = run_extractive_pipeline(
            cleaned_text=cleaned_text,
            summary_mode=mode,
            summary_ratio=ratio,
        )
    except Exception as e:
        raise ValueError(f"Summarization pipeline failure: {str(e)}")

    summary_text = result["summary"]
    used_abstractive = False

    if use_abstractive:
        summary_text, used_abstractive = refine_abstractively(summary_text)

    return {
        "summary":                     summary_text,
        "detailedSummary":             result["summary"],
        "used_abstractive_refinement": used_abstractive,
        "keywords":                    result["keywords"],
        "entities":                    result["entities"],
        "original_word_count":         result["original_word_count"],
        "summary_word_count":          len(summary_text.split()),
        "compression_ratio":           round(
            len(summary_text.split()) / max(result["original_word_count"], 1), 4
        ),
        "top_sentences_count":         result["selected_sentences"],
        "total_sentences_found":       result["total_sentences"],
        "notes": (
            "Hybrid NLP: TF-IDF + Word Frequency + TextRank (PageRank) + "
            "Position + Keyword + NER scoring. Redundancy removed via cosine similarity."
        ),
    }


# ── Routes ────────────────────────────────────────────────────────────────────

@summarize_bp.route("/api/summarize", methods=["POST"])
def summarize_file():
    """
    Upload a document and receive a structured academic summary.
    """
    if "file" not in request.files:
        return jsonify({"success": False, "error": "No file uploaded"}), 400
        
    file = request.files["file"]
    if not file.filename:
        return jsonify({"success": False, "error": "No file selected"}), 400

    mode = request.form.get("summary_mode", "medium")
    ratio = request.form.get("summary_ratio", None)
    ratio = float(ratio) if ratio else None
    use_abs = request.form.get("use_abstractive_refinement", "false").lower() == "true"

    cleaned, ext, fname = _save_and_extract(file)
    result = _run_summary(cleaned, mode, ratio, use_abs)

    return jsonify({
        "success":   True,
        "file_name": fname,
        "file_type": ext,
        **result,
    })


@summarize_bp.route("/api/summarize-text", methods=["POST"])
def summarize_text():
    """
    Summarize raw text input directly.
    """
    data = request.get_json(silent=True) or {}
    raw_text = data.get("text", "")
    
    # Validate input
    text = validate_text_input(raw_text)
    
    mode = data.get("summary_mode", "medium")
    ratio = data.get("summary_ratio", None)
    ratio = float(ratio) if ratio else None

    cleaned = clean_text(text)
    if not is_text_valid(cleaned):
        return jsonify({"success": False, "error": "Text is too noisy to summarize"}), 400

    result = _run_summary(cleaned, mode, ratio, False)

    return jsonify({
        "success": True,
        "file_name": "text_input",
        **result
    })


@summarize_bp.route("/api/full", methods=["POST"])
def full_pipeline():
    """
    All-in-one endpoint: summary + flashcards + quiz from a single file upload.
    """
    if "file" not in request.files:
        return jsonify({"success": False, "error": "No file uploaded"}), 400

    file = request.files["file"]
    mode = request.form.get("summary_mode", "medium")
    flashcard_count = min(int(request.form.get("flashcard_count", 10)), 20)
    quiz_count = min(int(request.form.get("quiz_count", 5)), 15)
    use_transformer = request.form.get("use_transformer", "false").lower() == "true"

    cleaned, ext, fname = _save_and_extract(file)

    # Run three pipelines on the exact same cleaned text
    summary_result = _run_summary(cleaned, mode, None, False)
    flashcards = generate_flashcards(cleaned, count=flashcard_count, use_transformer=use_transformer)
    questions = generate_quiz_questions(cleaned, count=quiz_count)

    return jsonify({
        "success":      True,
        "file_name":    fname,
        "file_type":    ext,
        **summary_result,
        "flashcards":   flashcards,
        "quizQuestions": questions,
    })


@summarize_bp.route("/api/full-text", methods=["POST"])
def full_text_pipeline():
    """
    All-in-one endpoint: summary + flashcards + quiz from raw text.
    """
    data = request.get_json(silent=True) or {}
    raw_text = data.get("text", "")
    
    # Validate input
    text = validate_text_input(raw_text)

    mode = data.get("summary_mode", "medium")
    flashcard_count = min(int(data.get("flashcard_count", 10)), 20)
    quiz_count = min(int(data.get("quiz_count", 5)), 15)
    use_transformer = str(data.get("use_transformer", "false")).lower() == "true"

    cleaned = clean_text(text)
    if not is_text_valid(cleaned):
        return jsonify({"success": False, "error": "Text is too noisy to process"}), 400

    # Run three pipelines
    summary_result = _run_summary(cleaned, mode, None, False)
    flashcards = generate_flashcards(cleaned, count=flashcard_count, use_transformer=use_transformer)
    questions = generate_quiz_questions(cleaned, count=quiz_count)

    return jsonify({
        "success":       True,
        "file_name":     "text_input",
        "inputType":     "text",
        **summary_result,
        "flashcards":    flashcards,
        "quizQuestions": questions,
    })
