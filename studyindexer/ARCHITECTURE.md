# StudyIndexer Architecture Documentation

## System Overview

StudyIndexer is a document processing and search system built with a microservices architecture using Docker. The system comprises four main Docker services that work together to provide document processing, vector storage, and search capabilities.

## Docker Services

### 1. StudyIndexer (FastAPI Service)
- **Purpose**: Main API service handling HTTP requests
- **Port**: 8000
- **Dependencies**: Redis, ChromaDB
- **Key Responsibilities**:
  - Document upload handling
  - Search operations
  - Status tracking
  - API endpoint management

### 2. Celery Worker
- **Purpose**: Asynchronous task processing
- **Dependencies**: Redis (broker), ChromaDB
- **Key Responsibilities**:
  - Document processing
  - ML operations (embeddings)
  - Maintenance tasks
  - Background jobs

### 3. ChromaDB
- **Purpose**: Vector database
- **Port**: 8001
- **Key Responsibilities**:
  - Vector storage
  - Similarity search
  - Document metadata storage

### 4. Redis
- **Purpose**: Message broker and result backend
- **Port**: 6379
- **Key Responsibilities**:
  - Task queue management
  - Result storage
  - Service communication

## API Endpoints and Their Flows

### Document Management (`/api/documents/`)

1. **Upload Document** `POST /`
   ```
   Client → FastAPI → DocumentIndexer.prepare_document()
                   → Celery Task (process_document)
                   → ChromaDB
   ```
   - FastAPI: Initial file handling
   - Celery: Async processing
   - Direct DB Operations: No

2. **List Documents** `GET /my`
   ```
   Client → FastAPI → DocumentIndexer.search()
                   → ChromaDB
   ```
   - FastAPI: Direct handling
   - Celery: No involvement
   - Direct DB Operations: Yes

3. **Delete Document** `DELETE /{document_id}`
   ```
   Client → FastAPI → DocumentIndexer.delete_document()
                   → ChromaDB
   ```
   - FastAPI: Direct handling
   - Celery: No involvement
   - Direct DB Operations: Yes

### Search Operations (`/api/search/`)

1. **Search Documents** `POST /`
   ```
   Client → FastAPI → DocumentIndexer.search()
                   → ChromaDB
   ```
   - FastAPI: Direct handling
   - Celery: No involvement
   - Direct DB Operations: Yes

2. **Similar Documents** `GET /similar/{document_id}`
   ```
   Client → FastAPI → DocumentIndexer.search()
                   → ChromaDB
   ```
   - FastAPI: Direct handling
   - Celery: No involvement
   - Direct DB Operations: Yes

### Personal Knowledge Base (`/api/personal/`)

All endpoints handled directly by FastAPI:
- `GET /folders`
- `GET /documents`
- `PATCH /documents/{document_id}/metadata`
- `GET /documents/{document_id}/related`

### Admin Operations (`/api/admin/`)

All endpoints handled directly by FastAPI:
- `GET /documents`
- `GET /stats`
- `POST /reindex`

## Service Layer Components

### 1. ChromaService (chroma.py)
```python
class ChromaService:
    # Vector database operations
    def get_or_create_collection()  # Collection management
    def add_documents()             # Document storage
    def search()                    # Vector search
    def update_metadata()           # Metadata management
```

### 2. DocumentIndexer (indexer.py)
```python
class DocumentIndexer:
    # Main coordination service
    def prepare_document()  # Upload handling
    def index_document()    # Processing
    def search()           # Search operations
    def delete_document()  # Deletion
```

### 3. DocumentTracker (tracker.py)
```python
class DocumentTracker:
    # Status management
    def update_status()    # Status updates
    def get_status()       # Status retrieval
```

## Celery Tasks

### Main Tasks (indexing_tasks.py)
```python
@celery_app.task
def process_document():
    # Document processing workflow:
    # 1. Load document
    # 2. Generate embeddings
    # 3. Store in ChromaDB
    # 4. Update status

@celery_app.task
def cleanup_old_documents():
    # Maintenance (runs daily)
    # Cleans up failed documents

@celery_app.task
def check_stuck_tasks():
    # Monitoring (runs every 15 min)
    # Checks for stuck processes
```

## Data Flow Patterns

### 1. Synchronous Operations
- Search queries
- Document listing
- Status checks
- Metadata updates

### 2. Asynchronous Operations
- Document processing
- Vector generation
- Maintenance tasks
- Background jobs

## Directory Structure
```
studyindexer/
├── app/
│   ├── api/          # FastAPI endpoints
│   ├── core/         # Core configurations
│   ├── schemas/      # Data models
│   ├── services/     # Business logic
│   └── tasks/        # Celery tasks
├── data/
│   ├── chroma/       # Vector DB storage
│   ├── processed/    # Processed documents
│   ├── temp/         # Temporary files
│   └── uploads/      # Uploaded documents
```

## Shared Resources

### 1. Data Directories
- `/app/data/uploads`: Document uploads
- `/app/data/processed`: Processing status
- `/app/data/chroma`: Vector database
- `/app/data/temp`: Temporary files

### 2. Environment Variables
- `REDIS_HOST`: Redis connection
- `CHROMA_HOST`: ChromaDB connection
- `*_DIR`: Directory paths

## Error Handling

1. **FastAPI Endpoints**
   - HTTP exceptions
   - Status codes
   - Error messages

2. **Celery Tasks**
   - Automatic retries
   - Error logging
   - Status updates

3. **Services**
   - Custom exceptions
   - Error propagation
   - Status tracking

## Logging

Each component has its own logging:
1. FastAPI: Request/Response logging
2. Celery: Task logging
3. Services: Operation logging
4. ChromaDB: Database logging

## Future Considerations

1. **Scalability**
   - Multiple workers
   - Load balancing
   - Caching

2. **Monitoring**
   - Task monitoring
   - Performance metrics
   - Error tracking

3. **Optimization**
   - Query optimization
   - Resource usage
   - Cache implementation 