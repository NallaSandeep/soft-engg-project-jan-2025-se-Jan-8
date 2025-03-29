### Setup Guide ###

This document explains how to install and configure the Study Indexer application.

## Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- At least 4GB of available RAM
- Ports 8080 and 8081 available on your system

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-repo/study-indexer.git
cd study-indexer
```

### 2. Create a Virtual Environment (Optional but Recommended)

```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## Configuration

### 1. Environment Variables

Create a `.env` file in the project root directory with the following contents:

```
# API Configuration
PORT=8081
HOST=127.0.0.1
DEBUG=False

# ChromaDB Configuration
CHROMA_PORT=8080
CHROMA_HOST=127.0.0.1

# Embedding Configuration
EMBEDDING_MODEL=all-MiniLM-L6-v2
```

### 2. Directory Structure

Ensure the following directories exist:

```bash
mkdir -p data/chromadb
mkdir -p logs
```

## Running the Application

### 1. Start All Services

```bash
python manage_services.py start
```

### 2. Check Service Status

```bash
python manage_services.py status
```

You should see both services (ChromaDB and FastAPI) reported as running.

### 3. Accessing the API

The API will be available at:
```
http://127.0.0.1:8081/
```

API documentation is available at:
```
http://127.0.0.1:8081/docs
```

## Troubleshooting

### Port Conflicts

If you receive errors about ports being in use:

```bash
# Check processes using the ports
# On Windows
netstat -ano | findstr :8080
netstat -ano | findstr :8081

# On macOS/Linux
lsof -i :8080
lsof -i :8081

# Kill the process (replace PID with the actual process ID)
# On Windows
taskkill /F /PID PID

# On macOS/Linux
kill -9 PID
```

Alternatively, you can change the ports in the `.env` file.

### ChromaDB Connection Issues

If FastAPI reports that it can't connect to ChromaDB:

1. Check that ChromaDB is running:
```bash
python manage_services.py status
```

2. Try restarting ChromaDB:
```bash
python manage_services.py restart chromadb
```

3. Verify ChromaDB data directory permissions:
```bash
# Make sure the data directory is accessible
chmod -R 755 data/chromadb
```

### Debug Mode

For detailed logs and direct console output from FastAPI:

```bash
python manage_services.py debug-fastapi
```

This will start FastAPI in the foreground with detailed output.

## Initial Data Import

To populate the system with initial FAQ data:

1. Prepare a JSONL file with FAQ items (see API_USAGE.md for format)
2. Use the import API:
```bash
curl -X 'POST' \
  'http://127.0.0.1:8081/api/v1/faq/import' \
  -H 'accept: application/json' \
  -F 'file=@your_data.jsonl' \
  -F 'source=Initial Import'
```

## Upgrading

When upgrading to a new version:

1. Pull the latest changes
```bash
git pull
```

2. Install any new dependencies
```bash
pip install -r requirements.txt
```

3. Restart the services
```bash
python manage_services.py restart
``` 