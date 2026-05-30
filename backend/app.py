# =============================================================================
# backend/app.py
# Production Flask Application Factory Pattern
# =============================================================================

import os
from flask import Flask, request, jsonify
from flask_cors import CORS

# Import layers
from config.config import config_by_name
from database.db import init_db
from utils.errors import register_error_handlers
from routes import (
    health_bp,
    summarize_bp,
    flashcards_bp,
    quizzes_bp,
    summaries_bp
)

def create_app(config_name=None):
    """
    Application factory pattern.
    Configures CORS, registers blueprints, establishes DB contexts, 
    and handles Firebase/Cognito configurations.
    """
    app = Flask(__name__)
    
    # 1. Resolve environment configuration (default to development)
    if not config_name:
        config_name = os.getenv("FLASK_ENV", "development")
    app.config.from_object(config_by_name.get(config_name, config_by_name["default"]))
    
    # 2. Configure CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)
    
    # Configure custom OPTIONS preflight header hooks
    @app.before_request
    def handle_preflight():
        if request.method == "OPTIONS":
            res = jsonify({"success": True})
            res.headers.add("Access-Control-Allow-Origin", "*")
            res.headers.add("Access-Control-Allow-Headers", "*")
            res.headers.add("Access-Control-Allow-Methods", "*")
            return res

    # 3. Initialize Database session (creates SQL schemas if absent)
    init_db(app)
    
    # 4. Initialize Auth providers softly (Firebase Admin SDK)
    _init_auth_providers(app)
    
    # 5. Register Global Exception / Error Handlers
    register_error_handlers(app)
    
    # 6. Register Blueprints (Modular Routers)
    app.register_blueprint(health_bp)
    app.register_blueprint(summarize_bp)
    app.register_blueprint(flashcards_bp)
    app.register_blueprint(quizzes_bp)
    app.register_blueprint(summaries_bp)
    
    print(f"[Server] Application factory successfully booted in [{config_name}] mode.")
    return app


def _init_auth_providers(app):
    """Safe initializer for Firebase Admin SDK (fails softly if keys are missing)"""
    auth_provider = app.config.get("AUTH_PROVIDER", "firebase").lower()
    
    if auth_provider == "firebase":
        try:
            import firebase_admin
            from firebase_admin import credentials
            
            # If already initialized in context, skip
            if firebase_admin._apps:
                return
                
            cred_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_KEY")
            if cred_path and os.path.exists(cred_path):
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
                app.logger.info("[Firebase] Admin SDK initialized successfully via certificate.")
            else:
                firebase_admin.initialize_app()
                app.logger.info("[Firebase] Admin SDK initialized via default implicit credentials.")
                
        except ImportError:
            app.logger.warning("[Firebase] firebase-admin is not installed. Firebase token verification is inactive.")
        except Exception as e:
            app.logger.warning(f"[Firebase] Implicit initialization skipped: {str(e)}. Using local bypasses in development.")