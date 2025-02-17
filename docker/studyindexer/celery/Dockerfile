# studyindexer/celery/Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    curl \
    git \
    redis-tools \
    # ML and document processing dependencies
    poppler-utils \
    tesseract-ocr \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Create necessary directories with proper permissions
RUN mkdir -p /app/data/uploads /app/data/processed /app/data/temp /app/data/chroma /app/logs \
    && chmod -R 755 /app

# Copy only requirements first
COPY studyindexer/requirements/celery.txt requirements.txt

# Install Python dependencies with BuildKit cache
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir -r requirements.txt && \
    python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')" && \
    python -c "import torch; print(f'PyTorch version: {torch.__version__}')"

# Copy application files
COPY studyindexer/app/ ./app/
COPY studyindexer/worker.py .

# Copy and prepare entrypoint script
COPY docker/studyindexer/celery/docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV CELERY_BROKER_URL=redis://redis:6379/0
ENV CELERY_RESULT_BACKEND=redis://redis:6379/0
ENV CHROMA_HOST=chromadb
ENV CHROMA_PORT=8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD celery -A app.core.celery_app inspect ping -d celery@$HOSTNAME || exit 1

# Use entrypoint script
ENTRYPOINT ["/docker-entrypoint.sh"]