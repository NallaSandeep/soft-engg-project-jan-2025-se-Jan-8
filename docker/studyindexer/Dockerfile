# studyindexer/Dockerfile
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    curl \
    git \
    redis-tools \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first
COPY studyindexer/requirements/indexer.txt requirements.txt

# Install Python dependencies with BuildKit cache
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY studyindexer/app/ ./app/
COPY studyindexer/main.py .

# Create necessary directories
RUN mkdir -p data/uploads data/processed data/temp data/chroma logs

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV APP_ENV=development
ENV CHROMA_HOST=chromadb
ENV CHROMA_PORT=8000
ENV REDIS_HOST=redis
ENV REDIS_PORT=6379

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start the FastAPI application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]