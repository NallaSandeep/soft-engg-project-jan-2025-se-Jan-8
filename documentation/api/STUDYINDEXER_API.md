# StudyIndexer API Reference

## Base URL
```
http://localhost:8000/api/v1
```

## Authentication
All endpoints require JWT authentication:
```http
Authorization: Bearer <token>
```

## Endpoints

### Document Management

#### Upload Document
```http
POST /documents
Content-Type: multipart/form-data
```

**Parameters:**
- `file`: Document file (PDF, DOCX, TXT, MD)
- `title`: Document title (optional)
- `course_id`: Course identifier (optional)
- `document_type`: Type of document (pdf, text, docx, markdown)
- `tags`: Comma-separated tags (optional)
- `collection`: Collection type (general, course, personal)

**Response:**
```json
{
    "document_id": "uuid",
    "status": "processing",
    "message": "Document queued for indexing"
}
```

#### Get Document Status
```http
GET /documents/{document_id}
```

**Response:**
```json
{
    "document_id": "uuid",
    "status": "completed",
    "metadata": {
        "title": "Example Document",
        "course_id": "CS101",
        "document_type": "pdf",
        "tags": ["lecture", "notes"],
        "collection": "course"
    }
}
```

#### Delete Document
```http
DELETE /documents/{document_id}
```

**Response:**
```json
{
    "message": "Document deleted successfully"
}
```

### Search

#### Search Documents
```http
POST /search
Content-Type: application/json
```

**Request Body:**
```json
{
    "text": "search query",
    "page": 1,
    "page_size": 10,
    "filters": {
        "course_id": "CS101",
        "document_type": "pdf"
    },
    "collection": "general",
    "min_score": 0.5
}
```

**Response:**
```json
{
    "results": [
        {
            "document_id": "uuid",
            "score": 0.85,
            "content": "Matching content...",
            "metadata": {
                "title": "Document Title",
                "course_id": "CS101"
            },
            "highlight": {
                "text": ["...matching context..."]
            }
        }
    ],
    "pagination": {
        "current_page": 1,
        "total_pages": 5,
        "total_results": 45
    }
}
```

#### Find Similar Documents
```http
GET /search/similar/{document_id}
```

**Parameters:**
- `limit`: Number of similar documents (default: 5)
- `min_score`: Minimum similarity score (default: 0.5)

**Response:**
```json
{
    "results": [
        {
            "document_id": "uuid",
            "score": 0.78,
            "content": "Similar content...",
            "metadata": {
                "title": "Similar Document"
            }
        }
    ]
}
```

### Admin Endpoints

#### List All Documents
```http
GET /admin/documents
```

**Parameters:**
- `limit`: Results per page (default: 100)
- `offset`: Pagination offset

**Response:**
```json
{
    "documents": [
        {
            "document_id": "uuid",
            "title": "Document Title",
            "status": "completed",
            "collection": "course",
            "created_at": "2024-02-13T12:00:00Z"
        }
    ],
    "total": 150
}
```

#### System Statistics
```http
GET /admin/stats
```

**Response:**
```json
{
    "total_documents": 150,
    "total_collections": 5,
    "storage_used": {
        "uploads": "100.5 MB",
        "vectors": "50.2 MB",
        "total": "150.7 MB"
    },
    "processing_status": {
        "pending": 5,
        "processing": 2,
        "completed": 140,
        "failed": 3
    }
}
```

#### Reindex Document
```http
POST /admin/reindex
```

**Request Body:**
```json
{
    "document_id": "uuid"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Document queued for reindexing"
}
```

## Error Responses

### 400 Bad Request
```json
{
    "success": false,
    "message": "Invalid request",
    "error": {
        "code": "VALIDATION_ERROR",
        "details": {
            "field": "error description"
        }
    }
}
```

### 401 Unauthorized
```json
{
    "success": false,
    "message": "Authentication required",
    "error": {
        "code": "AUTH_ERROR"
    }
}
```

### 403 Forbidden
```json
{
    "success": false,
    "message": "Insufficient permissions",
    "error": {
        "code": "PERMISSION_ERROR"
    }
}
```

### 404 Not Found
```json
{
    "success": false,
    "message": "Resource not found",
    "error": {
        "code": "NOT_FOUND",
        "details": {
            "resource": "document",
            "id": "uuid"
        }
    }
}
```

### 500 Internal Server Error
```json
{
    "success": false,
    "message": "Internal server error",
    "error": {
        "code": "INTERNAL_ERROR"
    }
}
```

## Rate Limiting
- 100 requests per hour for regular users
- 1000 requests per hour for admin users

Rate limit headers:
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1644744000
```

## Filtering
Search endpoints support filtering with:
- Course ID
- Document type
- Tags
- Collection type
- Custom metadata

Example filter:
```json
{
    "filters": {
        "course_id": "CS101",
        "document_type": "pdf",
        "tags": ["lecture", "notes"],
        "metadata.author": "John Doe"
    }
}
```

## Version History
- v1.0 (Feb 2025) - Initial API documentation 