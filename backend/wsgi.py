# =============================================================================
# backend/wsgi.py
# Production WSGI Server Entry Point (Elastic Beanstalk / Gunicorn compatible)
# =============================================================================

import os
from app import create_app

# Resolve config name (default to development, set to production in cloud)
config_name = os.getenv("FLASK_ENV", "development")
app = create_app(config_name=config_name)

if __name__ == "__main__":
    # If running directly, default to local port 5000
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
