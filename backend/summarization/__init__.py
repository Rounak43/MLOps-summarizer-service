# =============================================================================
# backend/summarization/__init__.py
# Package API for Summarization Service
# =============================================================================

from summarization.extractor import extract_text
from summarization.cleaner import clean_text, is_text_valid
from summarization.extractive import run_extractive_pipeline
from summarization.abstractive import refine_abstractively
from summarization.exceptions import ExtractionError, PipelineError
