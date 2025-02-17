#!/bin/bash
set -e

# Wait for Redis to be ready
until redis-cli -h redis ping > /dev/null 2>&1; do
    echo "Waiting for Redis..."
    sleep 1
done

# Wait for ChromaDB to be ready
until curl -s http://chromadb:8000/api/v1/heartbeat > /dev/null; do
    echo "Waiting for ChromaDB..."
    sleep 1
done

# Create necessary directories
mkdir -p data/uploads data/processed data/temp data/chroma logs

# Start the FastAPI application
exec uvicorn main:app --host 0.0.0.0 --port 8000 --reload