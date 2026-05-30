# =============================================================================
# backend/models/summary.py
# SQLAlchemy Model for Summaries Table
# =============================================================================

from database.db import db
from datetime import datetime

class Summary(db.Model):
    """Summary Model representing document analysis runs and materials"""
    __tablename__ = "summaries"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(128), db.ForeignKey("users.uid", ondelete="CASCADE"), nullable=False, index=True)
    type = db.Column(db.String(32), nullable=False, default="pdf")  # 'pdf' or 'text'
    title = db.Column(db.String(256), nullable=False)
    summary = db.Column(db.Text, nullable=False)
    detailed_summary = db.Column(db.Text, nullable=True)
    key_concepts = db.Column(db.JSON, nullable=True)  # List of keywords/entities
    flashcards = db.Column(db.JSON, nullable=True)      # List of generated flashcards
    quiz_questions = db.Column(db.JSON, nullable=True)  # List of MCQ quiz questions
    words = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        """Convert SQLAlchemy object to dictionary matching the expected frontend schema"""
        return {
            "id": self.id,
            "userId": self.user_id,
            "type": self.type,
            "title": self.title,
            "summary": self.summary,
            "detailedSummary": self.detailed_summary,
            "keyConcepts": self.key_concepts or [],
            "flashcards": self.flashcards or [],
            "quizQuestions": self.quiz_questions or [],
            "words": self.words,
            "createdAt": {
                "seconds": int(self.created_at.timestamp()),
                "nanoseconds": 0
            } if self.created_at else None
        }
