# =============================================================================
# backend/utils/validation.py
# Request Fields and File Validation Layer
# =============================================================================

import os

ALLOWED_EXTENSIONS = {"pdf", "txt", "docx"}
MAX_FILE_MB = 20

def allowed_file(filename: str) -> bool:
    """Verify that the uploaded file type is supported"""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_uploaded_file(file):
    """
    Validate size, extension, and presence of an uploaded file.
    Raises ValueError if invalid.
    """
    if not file:
        raise ValueError("No file uploaded")
    
    filename = file.filename or ""
    if not filename or not allowed_file(filename):
        raise ValueError(f"Unsupported file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}")
    
    # Read size
    file.seek(0, os.SEEK_END)
    size_bytes = file.tell()
    file.seek(0)  # Reset stream position for downstream consumers
    
    size_mb = size_bytes / (1024 * 1024)
    if size_mb > MAX_FILE_MB:
        raise ValueError(f"File too large. Maximum: {MAX_FILE_MB} MB")
    
    return filename, filename.rsplit(".", 1)[1].lower()


def validate_text_input(text: str, min_words: int = 50):
    """
    Validate direct pasted text input size constraints.
    Raises ValueError if invalid.
    """
    if not text or not text.strip():
        raise ValueError("No text content provided")
        
    words = text.strip().split()
    if len(words) < min_words:
        raise ValueError(f"Text too short (minimum {min_words} words)")
    
    return text.strip()
