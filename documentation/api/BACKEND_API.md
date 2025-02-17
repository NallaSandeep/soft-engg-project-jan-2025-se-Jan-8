# Backend API Reference

## Base URL
```
http://localhost:5000/api/v1
```

## Authentication
All endpoints require JWT authentication:
```http
Authorization: Bearer <token>
```

## Endpoints

### Authentication

#### Login
```http
POST /auth/login
Content-Type: application/json
```

**Request Body:**
```json
{
    "username": "string",
    "password": "string"
}
```

**Response:**
```json
{
    "access_token": "string",
    "token_type": "bearer",
    "expires_in": 1800
}
```

#### Refresh Token
```http
POST /auth/refresh
```

**Response:**
```json
{
    "access_token": "string",
    "token_type": "bearer",
    "expires_in": 1800
}
```

### Course Management

#### List Courses
```http
GET /courses
```

**Parameters:**
- `page`: Page number (default: 1)
- `per_page`: Items per page (default: 10)
- `search`: Search term (optional)

**Response:**
```json
{
    "courses": [
        {
            "id": "string",
            "code": "CS101",
            "name": "Introduction to Programming",
            "description": "string",
            "instructor": {
                "id": "string",
                "name": "string"
            },
            "enrollment_count": 0,
            "start_date": "2024-02-17",
            "end_date": "2024-05-17"
        }
    ],
    "pagination": {
        "page": 1,
        "per_page": 10,
        "total": 100
    }
}
```

#### Create Course
```http
POST /courses
Content-Type: application/json
```

**Request Body:**
```json
{
    "code": "string",
    "name": "string",
    "description": "string",
    "start_date": "2024-02-17",
    "end_date": "2024-05-17",
    "max_students": 30
}
```

#### Get Course Details
```http
GET /courses/{course_id}
```

**Response:**
```json
{
    "id": "string",
    "code": "CS101",
    "name": "string",
    "description": "string",
    "instructor": {
        "id": "string",
        "name": "string"
    },
    "weeks": [
        {
            "id": "string",
            "number": 1,
            "title": "string",
            "lectures": [],
            "assignments": []
        }
    ]
}
```

### User Management

#### List Users
```http
GET /users
```

**Parameters:**
- `role`: Filter by role (admin, teacher, student)
- `page`: Page number
- `per_page`: Items per page

**Response:**
```json
{
    "users": [
        {
            "id": "string",
            "username": "string",
            "email": "string",
            "role": "string",
            "is_active": true
        }
    ],
    "pagination": {
        "page": 1,
        "per_page": 10,
        "total": 100
    }
}
```

#### Create User
```http
POST /users
Content-Type: application/json
```

**Request Body:**
```json
{
    "username": "string",
    "email": "string",
    "password": "string",
    "role": "student",
    "first_name": "string",
    "last_name": "string"
}
```

### Personal Knowledge Base

#### List Folders
```http
GET /personal/folders
```

**Response:**
```json
{
    "folders": [
        {
            "id": "string",
            "name": "string",
            "parent_id": "string",
            "document_count": 0
        }
    ]
}
```

#### Create Folder
```http
POST /personal/folders
Content-Type: application/json
```

**Request Body:**
```json
{
    "name": "string",
    "parent_id": "string",
    "description": "string"
}
```

## Error Responses

### 400 Bad Request
```json
{
    "error": "VALIDATION_ERROR",
    "message": "Validation error",
    "details": {
        "field": ["error message"]
    }
}
```

### 401 Unauthorized
```json
{
    "error": "UNAUTHORIZED",
    "message": "Invalid credentials"
}
```

### 403 Forbidden
```json
{
    "error": "FORBIDDEN",
    "message": "Insufficient permissions"
}
```

### 404 Not Found
```json
{
    "error": "NOT_FOUND",
    "message": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
    "error": "INTERNAL_ERROR",
    "message": "Internal server error"
}
```

## Rate Limiting
- 100 requests per minute per IP
- Headers:
  ```http
  X-RateLimit-Limit: 100
  X-RateLimit-Remaining: 95
  X-RateLimit-Reset: 1644744000
  ```

## Pagination
List endpoints support pagination with:
- `page`: Page number (1-based)
- `per_page`: Results per page (default: 10, max: 100)

Response includes pagination metadata:
```json
{
    "pagination": {
        "page": 1,
        "per_page": 10,
        "total": 100,
        "pages": 10
    }
}
```

## Version History
- v1.0 (Feb 2025) - Initial API documentation 