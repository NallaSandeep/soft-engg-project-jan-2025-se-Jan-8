# StudyIndexer Setup Guide

## Prerequisites

1. Windows 10/11 with WSL2 installed
2. Python 3.8 or higher
3. Redis server (in WSL)
4. Git
5. Visual Studio Code (recommended)

## Project Structure

The StudyIndexer service is part of the StudyHub platform and consists of:

```plaintext
studyindexer/
├── app/                    # Main application package
│   ├── api/               # API endpoints
│   ├── core/              # Core functionality
│   ├── schemas/           # Data models
│   ├── services/          # Business logic
│   ├── tasks/             # Celery tasks
│   └── utils/             # Utility functions
├── data/                  # Data storage
│   ├── uploads/           # Document uploads
│   ├── processed/         # Processed documents
│   ├── temp/             # Temporary files
│   └── chroma/           # Vector database
├── logs/                  # Application logs
└── scripts/              # Utility scripts
```

## Initial Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd studyindexer
```

2. Create and activate virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/WSL
# OR
.\.venv\Scripts\Activate   # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create environment file:
```bash
cp .env.example .env
```

5. Update `.env` with appropriate values:
```env
# Core Settings
APP_ENV=development
DEBUG=true
VERSION=0.1.0

# Security Settings
API_KEY=your_api_key_here
JWT_SECRET=your_jwt_secret_key_here_min_32_chars

# Vector Database (ChromaDB)
CHROMA_HOST=localhost
CHROMA_PORT=8000
CHROMA_PERSIST_DIR=./data/chroma

# Redis Configuration (WSL)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=
```

## WSL Redis Setup

1. Install Redis in WSL:
```bash
sudo apt update
sudo apt install redis-server
```

2. Configure Redis:
```bash
sudo nano /etc/redis/redis.conf
```
   - Set `bind 127.0.0.1`
   - Set `protected-mode yes`

3. Start Redis service:
```bash
sudo service redis-server start
```

4. Test Redis connection:
```bash
redis-cli ping
# Should return "PONG"
```

## Starting the Service

### Initial Setup

1. Windows Setup (PowerShell as Administrator):
```powershell
cd E:\SEPROJECT\beta\studyindexer
.\setup.ps1
```

2. WSL Worker Setup (Ubuntu Terminal):
```bash
cd /mnt/e/SEPROJECT/beta/studyindexer
./setup_workers.sh
# Choose 'n' for ML packages if you only need task processing
# Choose 'y' if you need document processing and search
```

### Starting the Service

The service must be started in the correct sequence:

1. First, start Redis and Celery workers (Ubuntu Terminal):
```bash
cd /mnt/e/SEPROJECT/beta/studyindexer
./start_workers.sh
# Wait until you see "All workers started successfully!"
```

2. Then, start the main service (PowerShell):
```powershell
cd E:\SEPROJECT\beta\studyindexer
.\start.ps1
```

### Stopping the Service

1. Stop the main service:
   - Press Ctrl+C in the PowerShell window

2. Stop the workers:
   - Press Ctrl+C in the Ubuntu Terminal, or
   - Run `./stop_workers.sh`

### Available Modes

1. **Task-Only Mode**:
   - Basic task processing only
   - No document processing or search
   - Choose 'n' during `setup_workers.sh`

2. **Full Mode**:
   - Includes document processing and search
   - Requires more memory and disk space
   - Choose 'y' during `setup_workers.sh`

### Troubleshooting

If you encounter issues:

1. Check the logs:
   ```bash
   tail -f logs/celery_maintenance.log
   tail -f logs/celery_indexing.log  # If ML enabled
   ```

2. Restart in sequence:
   ```bash
   ./stop_workers.sh
   ./start_workers.sh
   # Then restart start.ps1
   ```

3. Common issues:
   - Redis connection: Check if Redis is running
   - Worker errors: Check worker logs
   - ML imports: Ensure ML packages are installed if needed

## Service Components

### 1. FastAPI Application
- Main API service
- Handles document uploads and search requests
- Runs on port 8000
- API documentation: http://localhost:8000/api/v1/docs

### 2. Celery Workers
- `indexing`: Processes document uploads and indexing
- `maintenance`: Handles cleanup and maintenance tasks
- Configured in `app/core/celery_app.py`

### 3. Redis
- Message broker for Celery
- Task result backend
- Runs in WSL on localhost:6379

### 4. ChromaDB
- Vector database for document embeddings
- Persistent storage in `data/chroma`
- Automatically initialized on startup

## Log Files

- `logs/celery_indexing.log`: Document processing logs
- `logs/celery_maintenance.log`: Maintenance task logs
- `logs/celery_beat.log`: Scheduled task logs
- `logs/info.log`: General application logs
- `logs/error.log`: Error logs

## Development Workflow

1. Start Redis in WSL:
```bash
sudo service redis-server start
```

2. Start Celery workers:
```bash
cd /path/to/studyindexer
./start_workers.sh
```

3. Start the FastAPI application:
```bash
python main.py
```

4. Monitor logs:
```bash
tail -f logs/celery_indexing.log
tail -f logs/info.log
```

## API Integration

### Authentication
All requests require a JWT token in the Authorization header:
```bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/documents/' \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@document.pdf'
```

### Document Upload
```bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/documents/?title=example&course_id=CS101&document_type=text&tags=example&collection=general' \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@document.txt'
```

### Search Documents
```bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/search' \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "text": "search query",
    "page": 1,
    "page_size": 10,
    "collection": "general"
  }'
```

## Troubleshooting

### Redis Connection Issues
1. Check Redis service status:
```bash
sudo service redis-server status
```

2. Verify Redis connection:
```bash
redis-cli ping
```

3. Check Redis logs:
```bash
sudo tail -f /var/log/redis/redis-server.log
```

### Celery Worker Issues
1. Stop existing workers:
```bash
./stop_workers.sh
```

2. Clear Redis:
```bash
redis-cli flushall
```

3. Restart workers:
```bash
./start_workers.sh
```

### Document Processing Issues
1. Check document status:
```bash
curl -X 'GET' \
  'http://localhost:8000/api/v1/documents/{document_id}' \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN'
```

2. Monitor processing logs:
```bash
tail -f logs/celery_indexing.log
```

## Maintenance

### Cleanup
1. Stop all services:
```bash
./stop_workers.sh
sudo service redis-server stop
```

2. Clear data (if needed):
```bash
rm -rf data/chroma/*
rm -rf data/processed/*
rm -rf data/uploads/*
```

### Backup
1. Stop services
2. Backup important directories:
```bash
tar -czf backup.tar.gz data/chroma data/processed
```

## Security Notes

1. Never expose Redis directly to the internet
2. Keep JWT secret keys secure
3. Regularly update dependencies
4. Monitor log files for suspicious activity
5. Use HTTPS in production

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| APP_ENV | Environment (development/production) | development |
| DEBUG | Enable debug mode | true |
| JWT_SECRET | JWT signing key | - |
| REDIS_HOST | Redis host | localhost |
| REDIS_PORT | Redis port | 6379 |
| CHROMA_HOST | ChromaDB host | localhost |
| CHROMA_PORT | ChromaDB port | 8000 |

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Celery Documentation](https://docs.celeryq.dev/)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [Redis Documentation](https://redis.io/docs/) 