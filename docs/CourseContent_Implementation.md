# CourseContent Implementation

## Overview

The CourseContent feature provides a complete API for managing detailed course content in the StudyIndexerNew platform. It enables the storage, retrieval, and management of comprehensive course information including course metadata, topics, concepts, weekly materials, and lectures.

## Objectives

- Provide a centralized system for storing and managing course content
- Enable semantic search across course materials
- Support content organization by weeks and topics
- Facilitate efficient content retrieval for various applications

## Data Model

### CourseInfo

```python
class CourseInfo(BaseModel):
    """Basic course information"""
    course_id: Optional[Union[str, int]] = None
    code: str = Field(..., description="Course code (e.g., CS101)")
    title: str = Field(..., description="Course title")
    description: Optional[str] = Field(None, description="Course description")
    department: Optional[str] = Field(None, description="Academic department")
    credits: Optional[int] = Field(None, description="Number of credits")
```

### CourseTopic

```python
class CourseTopic(BaseModel):
    """Course topic model"""
    name: str = Field(..., description="Topic name")
    description: Optional[str] = Field(None, description="Topic description")
```

### CourseContent

```python
class CourseContent(BaseModel):
    """Course content model with full details"""
    course_info: CourseInfo
    topics: List[CourseTopic] = Field(default=[], description="List of topics covered in the course")
    concepts_covered: List[str] = Field(default=[], description="List of concepts covered in the course")
    concepts_not_covered: List[str] = Field(default=[], description="List of concepts not covered in the course")
    weeks: List[Dict[str, Any]] = Field(default=[], description="Weekly breakdown of course content")
    lectures: List[Dict[str, Any]] = Field(default=[], description="Detailed lecture information")
```

## API Endpoints

### POST /api/v1/course-content

Add new course content to the database.

**Request Body**: `CourseContent` object
**Response**: `BaseResponse` with course_id in data

Example request:
```json
{
  "course_info": {
    "code": "CS101",
    "title": "Introduction to Computer Science",
    "description": "A foundational course in computer science principles",
    "department": "Computer Science",
    "credits": 3
  },
  "topics": [
    {
      "name": "Programming Basics",
      "description": "Fundamental concepts of programming"
    },
    {
      "name": "Data Structures",
      "description": "Basic data structures and algorithms"
    }
  ],
  "concepts_covered": ["Variables", "Control Flow", "Functions"],
  "concepts_not_covered": ["Advanced Algorithms", "Machine Learning"],
  "weeks": [
    {
      "order": 1,
      "title": "Introduction to Programming",
      "description": "Getting started with programming concepts"
    }
  ],
  "lectures": [
    {
      "title": "Variables and Data Types",
      "week": 1,
      "order": 1,
      "content_type": "video",
      "url": "https://example.com/lecture1"
    }
  ]
}
```

Example response:
```json
{
  "success": true,
  "message": "Course content added successfully",
  "data": {
    "course_id": "1234"
  }
}
```

### GET /api/v1/course-content/{course_id}

Retrieve course content by ID.

**Path Parameter**: `course_id` - ID of the course to retrieve
**Response**: `BaseResponse` with CourseContent in data

Example response:
```json
{
  "success": true,
  "data": {
    "course_info": {
      "course_id": "1234",
      "code": "CS101",
      "title": "Introduction to Computer Science",
      "description": "A foundational course in computer science principles",
      "department": "Computer Science",
      "credits": 3
    },
    "topics": [
      {
        "name": "Programming Basics",
        "description": "Fundamental concepts of programming"
      }
    ],
    "concepts_covered": ["Variables", "Control Flow", "Functions"],
    "concepts_not_covered": ["Advanced Algorithms", "Machine Learning"],
    "weeks": [...],
    "lectures": [...]
  }
}
```

### PUT /api/v1/course-content/{course_id}

Update existing course content.

**Path Parameter**: `course_id` - ID of the course to update
**Request Body**: `CourseContent` object
**Response**: `BaseResponse` with course_id in data

Example response:
```json
{
  "success": true,
  "message": "Course content updated successfully",
  "data": {
    "course_id": "1234"
  }
}
```

### DELETE /api/v1/course-content/{course_id}

Delete course content by ID.

**Path Parameter**: `course_id` - ID of the course to delete
**Response**: `BaseResponse` with course_id in data

Example response:
```json
{
  "success": true,
  "message": "Course content deleted successfully",
  "data": {
    "course_id": "1234"
  }
}
```

### GET /api/v1/course-content

List all courses with basic information.

**Query Parameters**:
- `limit` - Maximum number of results to return (default: 100)
- `offset` - Number of results to skip (default: 0)

**Response**: `BaseResponse` with list of courses in data

Example response:
```json
{
  "success": true,
  "data": {
    "courses": [
      {
        "course_id": "1234",
        "code": "CS101",
        "title": "Introduction to Computer Science",
        "department": "Computer Science",
        "credits": 3,
        "week_count": 10,
        "topic_count": 5,
        "created_at": "2023-04-15T14:30:45.123Z",
        "updated_at": "2023-04-15T14:30:45.123Z"
      }
    ],
    "total_count": 1,
    "limit": 100,
    "offset": 0
  }
}
```

### GET /api/v1/course-content/search

Search for courses by query.

**Query Parameters**:
- `query` - Search query string
- `limit` - Maximum number of results to return (default: 10)

**Response**: `BaseResponse` with list of courses in data

Example response:
```json
{
  "success": true,
  "data": {
    "courses": [
      {
        "course_id": "1234",
        "code": "CS101",
        "title": "Introduction to Computer Science",
        "department": "Computer Science",
        "credits": 3,
        "week_count": 10,
        "topic_count": 5,
        "score": 0.87,
        "created_at": "2023-04-15T14:30:45.123Z",
        "updated_at": "2023-04-15T14:30:45.123Z"
      }
    ],
    "total_count": 1,
    "query": "computer science",
    "limit": 10
  }
}
```

### POST /api/v1/course-content/import

Import course content from JSON files.

**Request Body**: `List[UploadFile]` - List of JSON files to import
**Response**: `BaseResponse` with import results in data

Example response:
```json
{
  "success": true,
  "message": "Imported 3 courses",
  "data": {
    "success": true,
    "total_imported": 3,
    "failed_items": [],
    "course_ids": ["1234", "5678", "9012"]
  }
}
```

### POST /api/v1/course-content/import-sample

Import sample course content files for testing.

**Response**: `BaseResponse` with import results in data

Example response:
```json
{
  "success": true,
  "message": "Imported 3 sample courses",
  "data": {
    "success": true,
    "total_imported": 3,
    "failed_items": [],
    "course_ids": ["1234", "5678", "9012"]
  }
}
```

## Service Implementation

The CourseContent service is responsible for managing course content in the database. It handles the following operations:

- Adding new course content
- Retrieving course content by ID
- Updating existing course content
- Deleting course content
- Listing all courses
- Searching for courses by query

The service uses ChromaDB as the underlying vector database for storing course content. It generates embeddings for each course using the EmbeddingService to enable semantic search.

### Key Features

- **Content Organization**: Courses are organized by topics, weeks, and lectures to provide a structured learning experience.
- **Semantic Search**: The service generates embeddings for course content to enable semantic search across the database.
- **Batch Import**: Support for importing multiple courses at once from JSON files.
- **Sample Data**: Built-in functionality to import sample courses for testing and demonstration.

## Implementation Details

### CourseContentService

```python
class CourseContentService:
    """Service for managing course content"""
    
    _instance = None
    
    def __new__(cls):
        """Singleton pattern to ensure only one instance is created"""
        if cls._instance is None:
            cls._instance = super(CourseContentService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the CourseContent service"""
        if getattr(self, '_initialized', False):
            return
            
        # Initialize dependencies
        self.chroma = ChromaService()
        self.embedder = EmbeddingService()
        
        # Set collection name for course content data
        self.collection_name = "course-content"
        
        # Flag for initialization status
        self._initialized = False
```

### Embedding Generation

```python
# Create a combined text for embedding
combined_text = f"COURSE: {title}\nDESCRIPTION: {description}\n"

if topic_texts:
    combined_text += "TOPICS: " + ", ".join(topic_texts) + "\n"
    
if concepts_covered:
    combined_text += "CONCEPTS COVERED: " + ", ".join(concepts_covered) + "\n"
    
if concepts_not_covered:
    combined_text += "CONCEPTS NOT COVERED: " + ", ".join(concepts_not_covered) + "\n"
    
if week_texts:
    combined_text += "WEEKS: " + " | ".join(week_texts)

# Generate embedding
embedding = await self.embedder.generate_embedding_async(combined_text)
```

### Data Storage

```python
# Store the full course content as a JSON string in the document
document = json.dumps(course_data)

# Prepare metadata
metadata = {
    "course_id": course_id_str,
    "code": course_info.get("code", ""),
    "title": title,
    "description": description[:1000] if description else "",
    "department": course_info.get("department", ""),
    "credits": str(course_info.get("credits", 0)),
    "created_at": datetime.utcnow().isoformat(),
    "updated_at": datetime.utcnow().isoformat(),
    "week_count": str(len(weeks)) if weeks else "0",
    "topic_count": str(len(topics)) if topics else "0",
}

# Store in ChromaDB
ids = await self.chroma.add_documents(
    collection_name=self.collection_name,
    documents=[document],
    metadatas=[metadata],
    ids=[course_id_str],
    embeddings=[embedding]
)
```

## Best Practices

- Ensure that course_info is always provided when adding or updating course content
- Use structured topics and weeks for better content organization
- Include relevant concepts_covered and concepts_not_covered for more accurate search results
- Provide detailed metadata in CourseInfo for better filtering and organization

## Future Enhancements

- Support for content versioning to track changes to course content
- Enhanced analytics to track content usage and popularity
- Integration with learning management systems for automatic content import/export
- Better search capabilities with filtering by topics, departments, etc.
- Support for multimedia content embedding (videos, PDFs, etc.) 