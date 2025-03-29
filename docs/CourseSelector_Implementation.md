# CourseSelector Implementation Specification

## Overview

The CourseSelector is a helper service designed to identify which courses from a student's subscribed courses are relevant to their query. It serves as a routing mechanism to help students find the most relevant course materials based on semantic search of course content.

The key objectives of the CourseSelector are:
1. Maintain academic integrity by only searching within courses that the student is enrolled in
2. Efficiently route student queries to the most relevant course materials
3. Provide a ranked list of matching courses with appropriate metadata

## Data Model

### Course Information Schema

```python
class CourseInfo(BaseModel):
    """Basic course information model"""
    course_id: int
    code: str
    title: str
    description: str
    department: str
    credits: int
```

### Course Topic Schema

```python
class CourseTopic(BaseModel):
    """Course topic model with metadata"""
    name: str = Field(..., min_length=2, max_length=100, description="Topic name")
    description: str = Field(..., min_length=5, max_length=1000, description="Topic description")
    week: Optional[int] = Field(None, description="Week number when the topic is covered")
    importance: int = Field(default=5, ge=1, le=10, description="Importance level (1-10)")
```

### Course Content Schema

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

### CourseSelector Search Query

```python
class CourseSelectorQuery(BaseSearchQuery):
    """Query model for CourseSelector search"""
    subscribed_courses: List[int] = Field(..., description="List of course IDs the student is subscribed to")
```

### CourseSelector Search Result

```python
class CourseMatchResult(BaseModel):
    """Search result model for matched courses"""
    course_id: int
    code: str
    title: str
    description: str
    department: str
    credits: int
    score: float = Field(..., ge=0.0, le=1.0, description="Relevance score")
    matched_topics: List[str] = Field(default=[], description="Topics that matched the query")
    weeks: List[int] = Field(default=[], description="Relevant week numbers")
```

### CourseSelector Response

```python
class CourseSelectorResponse(BaseSearchResponse):
    """Response model for CourseSelector operations"""
    results: List[CourseMatchResult]
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata about the search")
```

## API Endpoints

### Search Courses by Query

- **URL**: `POST /api/v1/course-selector/search`
- **Description**: Find relevant courses from a student's subscribed courses based on a query
- **Request Body**:
  ```json
  {
    "query": "sorting algorithms and complexity analysis",
    "subscribed_courses": [1, 2, 3],
    "min_score": 0.5,
    "limit": 10
  }
  ```
- **Response**:
  ```json
  {
    "success": true,
    "query": "sorting algorithms and complexity analysis",
    "total_results": 2,
    "query_time_ms": 125.47,
    "results": [
      {
        "course_id": 2,
        "code": "CSE101",
        "title": "Data Structures and Algorithms",
        "description": "A comprehensive course covering the fundamental data structures and algorithms",
        "department": "Computer Science",
        "credits": 4,
        "score": 0.89,
        "matched_topics": ["Algorithm Analysis", "Sorting Algorithms", "Computational Complexity"],
        "weeks": [3, 4, 5]
      },
      {
        "course_id": 3,
        "code": "CSE201",
        "title": "Algorithm Design",
        "description": "Advanced techniques for algorithm design and analysis",
        "department": "Computer Science",
        "credits": 3,
        "score": 0.72,
        "matched_topics": ["Algorithm Analysis", "Computational Complexity"],
        "weeks": [1, 2]
      }
    ],
    "metadata": {
      "subscribed_courses": [1, 2, 3]
    }
  }
  ```

### Index a Course

- **URL**: `POST /api/v1/course-selector/index`
- **Description**: Index a course in the CourseSelector database
- **Request Body**: Course content object with course information and topics
- **Response**:
  ```json
  {
    "success": true,
    "message": "Course indexed successfully",
    "data": {
      "course_id": "2"
    }
  }
  ```

### Index Sample Courses

- **URL**: `POST /api/v1/course-selector/index-sample-courses`
- **Description**: Index all sample course files for testing/demonstration
- **Response**:
  ```json
  {
    "success": true,
    "message": "Indexed 3 sample courses",
    "data": {
      "total_indexed": 3,
      "course_ids": ["1", "2", "3"],
      "failed_items": []
    }
  }
  ```

### Get Course Details

- **URL**: `GET /api/v1/course-selector/{course_id}`
- **Description**: Get detailed information about a course
- **Response**:
  ```json
  {
    "success": true,
    "data": {
      "course_info": {
        "course_id": 2,
        "code": "CSE101",
        "title": "Data Structures and Algorithms",
        "description": "A comprehensive course covering the fundamental data structures and algorithms",
        "department": "Computer Science",
        "credits": 4
      },
      "concepts_covered": [
        "Algorithm Analysis",
        "Sorting Algorithms",
        "Computational Complexity",
        "Data Structures",
        "Recursion"
      ],
      "concepts_not_covered": [
        "Advanced Graph Algorithms",
        "Parallel Algorithms"
      ],
      "weeks": [
        "1. Introduction to Algorithms",
        "2. Fundamental Data Structures",
        "3. Recursive Algorithms"
      ],
      "indexed_at": "2023-06-15T14:30:25.123456"
    }
  }
  ```

## Service Implementation

The CourseSelector is implemented as a dedicated service that leverages ChromaDB for vector storage and semantic search. It follows a singleton pattern to ensure efficient use of resources.

The key components of the service include:

1. **Embedding Generation**: Course content (title, description, concepts) is embedded using an embedding model (all-MiniLM-L6-v2) to create vector representations for semantic search.

2. **Course Indexing**: Each course is indexed with its metadata, including course ID, title, description, and concepts covered.

3. **Semantic Search**: When a student submits a query, it is converted to an embedding and used to search for the most similar courses among their subscribed courses.

4. **Filtering**: Search results are filtered to include only courses that the student is enrolled in, maintaining academic integrity.

5. **Result Processing**: Courses are ranked by similarity score, and additional metadata (matched topics, relevant weeks) is included in the results.

## Implementation Details

### Initialization

The CourseSelector service initializes by creating a connection to ChromaDB and ensuring the required collection exists.

```python
async def initialize(self) -> bool:
    """Initialize the service and ensure the collection exists"""
    try:
        # Create or get the collection
        await self.chroma.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "Course content for finding relevant courses"}
        )
        
        # Check if collection already has data
        collection_info = await self.chroma.get_collection_info(self.collection_name)
        logger.info(f"Course selector collection initialized with {collection_info['count']} entries")
        
        self._initialized = True
        return True
    except Exception as e:
        logger.error(f"Failed to initialize CourseSelector service: {str(e)}")
        return False
```

### Indexing Courses

When indexing a course, the service extracts key information and creates a combined text representation for embedding.

```python
# Create a combined text for embedding that captures the essence of the course
combined_text = f"COURSE: {title}\nDESCRIPTION: {description}\n"

if concepts_covered:
    combined_text += "CONCEPTS COVERED: " + ", ".join(concepts_covered) + "\n"
    
if concepts_not_covered:
    combined_text += "CONCEPTS NOT COVERED: " + ", ".join(concepts_not_covered) + "\n"
    
if week_titles:
    combined_text += "WEEKS: " + " | ".join(week_titles)

# Generate embedding
embedding = await self.embedder.generate_embedding_async(combined_text)
```

### Searching Courses

The search process involves:
1. Converting the subscribed courses to a filter condition
2. Generating an embedding for the query
3. Searching ChromaDB with the embedding and filter
4. Processing results to extract matched topics and weeks

```python
# Convert subscribed courses to string IDs for where clause
if search_query.subscribed_courses:
    str_course_ids = [str(course_id) for course_id in search_query.subscribed_courses]
    
    # Handle single course subscription
    if len(str_course_ids) == 1:
        filter_conditions.append({"course_id": str_course_ids[0]})
    else:
        # For multiple courses, use $or condition
        or_conditions = [{"course_id": course_id} for course_id in str_course_ids]
        filter_conditions.append({"$or": or_conditions})
```

## Usage Examples

### Filtering Courses by Query

```python
# Example: Finding relevant courses for a student query
query = CourseSelectorQuery(
    query="How do sorting algorithms work?",
    subscribed_courses=[1, 2, 3],  # Course IDs the student is enrolled in
    min_score=0.5,  # Minimum relevance score
    limit=5  # Maximum number of results
)

total_results, results, query_time = await course_selector_service.select_courses(query)
```

### Indexing a New Course

```python
# Index a new course from a JSON file
with open("course_data.json", "r") as f:
    course_data = json.load(f)
    
course_id = await course_selector_service.index_course(course_data)
```

## Best Practices

1. **Pre-index all courses**: For optimal performance, index all courses during system initialization.

2. **Validate subscribed courses**: Always validate that the student is actually subscribed to the courses they're requesting to search.

3. **Combine with course content**: The CourseSelector is designed to be used in conjunction with a more detailed course content search, where it first identifies the most relevant courses, and then a more detailed search is performed within those courses.

4. **Monitor query performance**: Keep track of query times to ensure optimal performance, especially as the number of courses increases.

## Future Enhancements

1. **Topic-level matching**: Enhance the matching algorithm to identify specific topics within courses that match the query.

2. **Personalized ranking**: Incorporate student preferences, past searches, and performance to personalize course rankings.

3. **Cross-course connections**: Identify connections between different courses that cover related topics.

4. **Learning path suggestions**: Based on a query, suggest sequences of courses that would help the student master a particular topic.

5. **Query reformulation**: Automatically expand or refine queries to improve search results. 