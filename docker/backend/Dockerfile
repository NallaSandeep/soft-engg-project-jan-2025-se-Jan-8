# backend/Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    curl \
    git \
    dos2unix \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY studyhub/backend/requirements.txt .

# Install dependencies (excluding development packages)
RUN pip install --no-cache-dir flask flask-sqlalchemy flask-migrate flask-jwt-extended \
    flask-cors python-dotenv gunicorn requests celery redis \
    email-validator python-jose[cryptography] passlib[bcrypt] \
    pydantic pydantic-settings

# Copy application code
COPY studyhub/backend/ .

# Create necessary directories with proper permissions
RUN mkdir -p instance logs uploads \
    && chmod -R 755 /app

# Copy and prepare entrypoint script
COPY docker/backend/docker-entrypoint.sh /docker-entrypoint.sh
RUN dos2unix /docker-entrypoint.sh && chmod +x /docker-entrypoint.sh

EXPOSE 5000

# Set environment variables
ENV FLASK_APP=wsgi.py
ENV FLASK_ENV=development
ENV PYTHONUNBUFFERED=1
ENV DATABASE_URL=sqlite:///instance/studyhub.db
ENV INDEXER_URL=http://studyindexer:8000

ENTRYPOINT ["/bin/sh", "/docker-entrypoint.sh"]