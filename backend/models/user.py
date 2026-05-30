# =============================================================================
# backend/models/user.py
# SQLAlchemy Model for Users Table
# =============================================================================

from database.db import db
from datetime import datetime

class User(db.Model):
    """User Model representing authenticated users (Firebase/Cognito)"""
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(128), unique=True, nullable=False, index=True)  # Firebase UID or Cognito Sub ID
    email = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(128), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relational mapping to summaries
    summaries = db.relationship("Summary", backref="user_ref", cascade="all, delete-orphan", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "uid": self.uid,
            "email": self.email,
            "name": self.name,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None
        }
