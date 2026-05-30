# =============================================================================
# backend/database/db.py
# SQLAlchemy Database Initialization Layer
# =============================================================================

from flask_sqlalchemy import SQLAlchemy

# Instantiate SQLAlchemy db object (will be bound in app factory create_app)
db = SQLAlchemy()

def init_db(app):
    """
    Bind SQLAlchemy instance to Flask application.
    Creates schema tables if they do not exist (useful for dev SQLite or RDS auto-migration).
    """
    db.init_app(app)
    
    with app.app_context():
        # Import models so SQLAlchemy knows to register them
        import models.user
        import models.summary
        
        db.create_all()
        print("[Database] Database initialized and schema tables verified.")
