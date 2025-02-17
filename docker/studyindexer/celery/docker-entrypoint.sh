#!/bin/sh
set -ex

# Wait for Redis to be ready
echo "Starting Redis connection test..."
redis-cli -h redis ping || echo "Initial Redis ping failed with code: $?"

echo "Starting Redis wait loop..."
until redis-cli -h redis ping; do
    echo "Waiting for Redis... (last exit code: $?)"
    sleep 1
done
echo "Redis is ready!"

# Wait for ChromaDB to be ready
echo "Starting ChromaDB wait loop..."
until curl -s http://chromadb:8000/api/v1/heartbeat; do
    echo "Waiting for ChromaDB... (last exit code: $?)"
    sleep 1
done
echo "ChromaDB is ready!"

# Initialize ChromaDB collections
echo "Initializing ChromaDB collections..."
python -c "
from app.services.chroma import ChromaService
from app.core.config import settings

# Initialize ChromaDB service
chroma = ChromaService()

# Create general collection
general_metadata = {
    'description': 'General collection for all documents',
    'created_by': 'StudyIndexer',
    'version': settings.VERSION,
    'collection_type': 'general'
}
chroma.get_or_create_collection('general', general_metadata)
print('General collection initialized')
"

# Start Celery worker
echo "Starting Celery worker..."
celery -A app.core.celery_app worker \
    --loglevel=info \
    --concurrency=4 \
    --max-tasks-per-child=100 \
    -Q default,indexing,maintenance \
    -n worker@%h