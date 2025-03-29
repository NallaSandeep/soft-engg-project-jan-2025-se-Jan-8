# StudyIndexer

## Overview

StudyIndexer is a Retrieval Augmented Generation (RAG) backend for the StudyHub learning platform. It provides vector-based search capabilities for course content, personal resources, and academic integrity checking using embedding models and vector databases.

## Key Features

- **Course Content Retrieval**: Semantic search for course materials
- **Personal Resource Management**: Student-specific resource indexing and retrieval
- **Academic Integrity Checking**: Detection of potential violations in submissions
- **Course Selection**: Identifying relevant courses for student queries
- **Sync Tools**: Scripts for synchronizing with StudyHub database

## Architecture

The system uses:
- **FastAPI** for API development
- **ChromaDB** for vector database storage
- **Sentence-Transformers** for embedding generation
- **Pydantic** for data validation

## Installation

### Prerequisites

- Python 3.9+
- ChromaDB
- Required Python packages (see `requirements.txt`)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/your-repo/StudyIndexer.git
cd StudyIndexer
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Setup environment variables (create `.env` file):
```
PORT=8081
CHROMA_PORT=8000
CHROMA_PERSIST_DIR=./data/chroma
DEBUG=true
```

4. Start the services:
```bash
python manage_services.py start
```

## API Documentation

The API documentation is available at `/docs` when running the server:

```
http://localhost:8081/docs
```

### Main API Endpoints

- **CourseSelector API**: `/api/v1/course-selector/search`
- **CourseContent API**: `/api/v1/course-content/search`
- **PersonalResource API**: `/api/v1/personal-resource/*`
- **IntegrityCheck API**: `/api/v1/integrity-check/*`

## Integration with StudyHub

StudyIndexer is designed to integrate with StudyHub through:

1. **Automatic Sync**: During database initialization via `init_db.py`
2. **Manual Sync**: Through dedicated scripts:
   - `sync_resources.py`: Sync personal resources
   - `sync_assignments.py`: Sync graded assignments

## Development

### Service Management

The `manage_services.py` script provides commands for managing the services:

```bash
# Start all services
python manage_services.py start

# Stop all services
python manage_services.py stop

# Restart services
python manage_services.py restart

# Check status
python manage_services.py status

# Show information
python manage_services.py info

# Start FastAPI in debug mode
python manage_services.py debug-fastapi
```

### Project Structure

```
StudyIndexer/
├── app/
│   ├── api/              # API endpoints
│   ├── models/           # Pydantic models
│   ├── services/         # Business logic
│   └── utils/            # Utility functions
├── data/                 # Data storage
│   └── chroma/           # ChromaDB persistence
├── docs/                 # Documentation
├── tests/                # Unit and integration tests
├── main.py               # Application entry point
├── manage_services.py    # Service management script
└── requirements.txt      # Python dependencies
```

## Documentation

For detailed documentation, see:
- [Features Documentation](docs/FEATURES.md)
- [API Specifications](docs/API-SPECS.md)
- [Implemented APIs](docs/implemented_apis.md)
- [IntegrityCheck API Samples](docs/IntegrityCheck_API_Samples.md)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- StudyHub development team
- ChromaDB for vector search capabilities
- Sentence-Transformers for embedding models 