# StudyHub Setup Guide

## Prerequisites

### Development Environment
- Python 3.10 or higher
- Node.js 18 or higher
- Docker Desktop
- Git
- Visual Studio Code (recommended)

### System Requirements
- 16GB RAM minimum (32GB recommended)
- 50GB free disk space
- Windows 10/11, macOS, or Linux
- NVIDIA GPU (optional, for ML acceleration)

## Quick Start

```bash
# Clone the repository
git clone <repository-url>
cd studyhub

# Start all services
cd docker
docker compose up -d
```

Visit:
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000
- StudyIndexer API: http://localhost:8000
- API Documentation: http://localhost:5000/api/v1/docs

## Detailed Setup

### 1. Backend Service

```bash
# Create virtual environment
cd studyhub/backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt

# Initialize database
python scripts/init_db.py

# Start development server
python wsgi.py
```

### 2. Frontend Application

```bash
# Install dependencies
cd studyhub/frontend
npm install

# Start development server
npm start
```

### 3. StudyIndexer Service

```bash
# Create virtual environment
cd studyindexer
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt

# Start development server
uvicorn main:app --reload
```

### 4. Development Database

We use SQLite for development. The database file is automatically created at:
```
studyhub/backend/instance/studyhub.db
```

Important: We use `init_db.py` instead of Flask migrations. See [Database Standards](STANDARDS.md#database-practices) for details.

## Docker Development

### 1. Building Images

```bash
# Build all services
docker compose build

# Build specific service
docker compose build studyindexer
```

### 2. Starting Services

```bash
# Start all services
docker compose up -d

# Start specific service
docker compose up -d backend

# View logs
docker compose logs -f
```

### 3. Common Docker Commands

```bash
# Check service status
docker compose ps

# Restart service
docker compose restart backend

# Stop all services
docker compose down

# Clean up volumes
docker compose down -v
```

## Environment Configuration

### 1. Backend Configuration
```env
# .env
FLASK_ENV=development
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///instance/studyhub.db
INDEXER_URL=http://localhost:8000
```

### 2. Frontend Configuration
```env
# .env
REACT_APP_API_URL=http://localhost:5000/api/v1
REACT_APP_INDEXER_URL=http://localhost:8000
```

### 3. StudyIndexer Configuration
```env
# .env
APP_ENV=development
CHROMA_HOST=localhost
CHROMA_PORT=8001
REDIS_HOST=localhost
REDIS_PORT=6379
```

## IDE Setup

### Visual Studio Code

1. **Extensions**
   - Python
   - Pylance
   - ESLint
   - Prettier
   - Docker
   - REST Client

2. **Settings**
```json
{
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    }
}
```

3. **Launch Configurations**
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Flask",
            "type": "python",
            "request": "launch",
            "module": "flask",
            "env": {
                "FLASK_APP": "wsgi.py",
                "FLASK_ENV": "development"
            },
            "args": [
                "run",
                "--no-debugger"
            ],
            "jinja": true
        }
    ]
}
```

## Troubleshooting

### 1. Docker Issues

```bash
# Reset Docker environment
docker compose down -v
docker system prune -f
docker compose up -d
```

### 2. Database Issues

```bash
# Reset database
rm backend/instance/studyhub.db
python scripts/init_db.py
```

### 3. Dependencies Issues

```bash
# Clean Python environment
deactivate
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Clean Node modules
rm -rf node_modules
npm cache clean --force
npm install
```

## Development Workflow

1. **Start Infrastructure**
   ```bash
   docker compose up -d redis chromadb
   ```

2. **Start Services**
   ```bash
   # Terminal 1 - Backend
   cd backend
   python wsgi.py

   # Terminal 2 - Frontend
   cd frontend
   npm start

   # Terminal 3 - StudyIndexer
   cd studyindexer
   uvicorn main:app --reload
   ```

3. **Access Services**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5000
   - StudyIndexer: http://localhost:8000

## Next Steps

1. Read the [Architecture Overview](ARCHITECTURE.md)
2. Review [Coding Standards](STANDARDS.md)
3. Set up [Development Workflow](DEVELOPMENT_WORKFLOW.md)

## Common Issues

1. **Port Conflicts**
   - Check if ports 3000, 5000, 8000, 8001, 6379 are available
   - Use `lsof -i :<port>` (Unix) or `netstat -ano | findstr :<port>` (Windows)

2. **Memory Issues**
   - Increase Docker memory limit
   - Close unnecessary applications
   - Monitor with Docker Desktop

3. **ML Model Loading**
   - First run may take time to download models
   - Ensure good internet connection
   - Check GPU availability if configured

## Version History
- v1.0 (Feb 2025) - Initial setup guide
- v1.1 (Feb 2025) - Added IDE configuration and troubleshooting 