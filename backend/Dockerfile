# =============================================================================
# backend/Dockerfile
# Lightweight production Docker recipe for Flask NLP backend
# =============================================================================

FROM python:3.10-slim

# Enforce clean terminal outputs and block buffering
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=5000

WORKDIR /app

# Install standard system libraries needed for psycopg2 compilation if compiling from source
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy and install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Download NLTK and SpaCy NLP models during build (caches them inside image layer)
RUN python -m nltk.downloader punkt punkt_tab stopwords \
    && python -m spacy download en_core_web_sm

# Copy remaining source code
COPY . .

# Expose server port
EXPOSE 5000

# Execute Gunicorn WSGI server
CMD gunicorn --bind 0.0.0.0:5000 --workers 2 --threads 4 wsgi:app
