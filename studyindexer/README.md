# StudyIndexer

## Overview

StudyIndexer is a document processing and indexing service that enables efficient search and retrieval of academic materials. It provides vector-based search capabilities and manages document collections for the StudyHub platform.

## Prerequisites

- Python 3.x
- WSL (Windows Subsystem for Linux) or Linux environment
- Virtual environment support
- 4GB+ RAM (for ML models)

## Key Components

- **ChromaDB**: Vector database (port 8000)
- **FastAPI**: REST API server (port 8081)
- **ML Model**: all-MiniLM-L6-v2 for document embedding

## API Tools

The StudyIndexer provides three ways to interact with the API:

1. **API Explorer** (http://127.0.0.1:8081/explorer)
   - Custom-built interactive testing interface
   - Features:
     - Document Management
       - Upload new documents with metadata
       - List and manage existing documents
       - Track document processing status
       - View parent-child document relationships
     - Search Capabilities
       - Text-based search with filters
       - Similarity search between documents
     - Authentication Support
       - JWT token-based authentication
       - Role-based access control
     - Visual Features
       - Tabular views for document lists
       - JSON/Table view toggle
       - Intuitive form-based input
     - Administrative Functions
       - System statistics
       - Collection management
       - User access control

2. **Swagger UI** (http://127.0.0.1:8081/docs)
   - OpenAPI documentation and testing interface
   - Features:
     - Complete API documentation
     - Request/response examples
     - Interactive testing
     - Schema definitions

3. **ReDoc** (http://127.0.0.1:8081/redoc)
   - Alternative API documentation viewer
   - Features:
     - Clean, organized documentation
     - Search functionality
     - Mobile-friendly view

## Setup Instructions

1. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/WSL
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Start the services:
   ```bash
   python manage_services.py start
   ```

4. Verify services are running:
   ```bash
   python manage_services.py status
   ```

## Service Management

### Starting Services
```bash
python manage_services.py start
```
- Starts ChromaDB and FastAPI services
- Initializes ML components
- Creates necessary collections

### Checking Status
```bash
python manage_services.py status
```
- Verifies health of all services
- Checks ChromaDB and FastAPI endpoints

### Service Information
```bash
python manage_services.py info
```
Displays detailed information about:
- Service configurations
- Environment variables
- Current status
- Available API endpoints and tools
- Gracefully stops all running services

## Service Architecture

- **ChromaDB Service**
  - Port: 8000
  - Purpose: Vector database for document embeddings
  - Health check: `/api/v2/heartbeat`

- **FastAPI Service**
  - Port: 8081
  - Purpose: REST API for document processing
  - Health check: `/api/health`

## Troubleshooting

1. **Service Startup Issues**
   - Initial health checks may fail as services take time to start
   - Wait 30 seconds and run `manage_services.py status` to verify
   - Check logs in `logs/` directory for specific errors

2. **ChromaDB Issues**
   - Ensure port 8000 is available
   - Check ChromaDB logs for initialization errors
   - Verify data directory permissions

3. **FastAPI Issues**
   - Ensure port 8081 is available
   - Check application logs for startup errors
   - Verify ML model initialization

4. **Common Solutions**
   - Restart services: `python manage_services.py restart`
   - Clear ChromaDB cache if needed
   - Check system resources (RAM, CPU)

## Environment Variables

Create a `.env` file with:
```
CHROMA_PORT=8000
FASTAPI_PORT=8081
LOG_LEVEL=INFO
ENVIRONMENT=development
```

## Development

### API Documentation
- Swagger UI: http://localhost:8081/docs
- ReDoc: http://localhost:8081/redoc

### Testing
```bash
pytest tests/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request 