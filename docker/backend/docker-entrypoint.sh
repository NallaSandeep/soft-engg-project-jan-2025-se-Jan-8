# backend/docker-entrypoint.sh
#!/bin/sh
set -e

# Wait for StudyIndexer to be ready
until curl -s http://studyindexer:8000/health > /dev/null; do
    echo "Waiting for StudyIndexer..."
    sleep 1
done

# Check if database exists and has data
if [ ! -f "instance/studyhub.db" ] || [ ! -s "instance/studyhub.db" ]; then
    echo "Database not found or empty. Initializing with sample data..."
    python scripts/init_db.py
else
    echo "Database already exists. Skipping initialization."
fi

# Start the Flask application with gunicorn
exec gunicorn --bind 0.0.0.0:5000 --workers 4 --threads 2 wsgi:app