# Course Guide Database Implementation Specification

## 1. Overview

The Course Guide Database is one of the four vector databases in the StudyIndexer system. It stores semantic descriptions of what topics are covered or excluded in each course. This database provides a way for students to determine which courses cover specific topics they're interested in learning. This document provides detailed specifications for implementing the Course Guide database.

## 2. Data Model

### 2.1 Course Topic Schema

```python
class TopicScope(str, Enum):
    """Scope of topic coverage in a course"""
    COVERED = "covered"
    EXCLUDED = "excluded"
    PREREQUISITE = "prerequisite"
    ADVANCED = "advanced"  # Covered, but at an advanced level

class CourseTopic(BaseModel):
    """Course topic model with validation"""
    topic_name: str = Field(..., min_length=2, max_length=200, description="Topic name")
    scope: TopicScope = Field(..., description="Scope of topic coverage")
    description: Optional[str] = Field(None, max_length=1000, description="Detailed description of coverage")
    importance: int = Field(default=5, ge=1, le=10, description="Importance in the course (1-10)")
    week_covered: Optional[int] = Field(None, description="Course week when this topic is covered")
    related_topics: List[str] = Field(default=[], description="Related topics")
```

### 2.2 Course Guide Item Schema

```python
class CourseGuideItem(BaseModel):
    """Course guide model with validation"""
    course_id: str = Field(..., regex=r'^[A-Z]{2,4}\d{3,4}$', description="Course ID (e.g., CS101)")
    title: str = Field(..., min_length=5, max_length=200, description="Course title")
    department: str = Field(..., min_length=2, max_length=100, description="Academic department")
    description: str = Field(..., min_length=10, max_length=2000, description="Course description")
    topics: List[CourseTopic] = Field(..., min_items=1, description="Topics covered in this course")
    prerequisites: List[str] = Field(default=[], description="Prerequisite course IDs")
    credits: float = Field(..., gt=0, description="Number of credits")
    level: str = Field(..., regex=r'^(100|200|300|400|500|600|700)$', description="Course level")
    semester_offered: List[str] = Field(..., description="Semesters when this course is offered")
    instructors: List[str] = Field(default=[], description="Course instructors")
    last_updated: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    updated_by: Optional[str] = Field(None, description="User who last updated this guide")
```

### 2.3 Course Guide Search Query

```python
class CourseGuideSearchQuery(BaseModel):
    """Query model for course guide search"""
    query: str = Field(..., min_length=3, max_length=500, description="Search query text")
    departments: Optional[List[str]] = Field(None, description="Filter by departments")
    level: Optional[str] = Field(None, regex=r'^(100|200|300|400|500|600|700)$', description="Filter by course level")
    scope: Optional[TopicScope] = Field(None, description="Filter by topic scope")
    limit: int = Field(default=10, ge=1, le=50, description="Maximum number of results")
    min_score: float = Field(default=0.3, ge=0.0, le=1.0, description="Minimum similarity score")
```

### 2.4 Course Guide Search Result

```python
class CourseTopicResult(BaseModel):
    """Topic result within a course"""
    topic_name: str
    scope: TopicScope
    description: Optional[str]
    importance: int
    week_covered: Optional[int]

class CourseGuideResult(BaseModel):
    """Search result model for course guides"""
    course_id: str
    title: str
    department: str
    description: str
    score: float = Field(..., ge=0.0, le=1.0, description="Similarity score")
    matching_topics: List[CourseTopicResult]
    credits: float
    level: str
    semester_offered: List[str]
    last_updated: datetime
```

### 2.5 Course Guide Response Models

```python
class CourseGuideResponse(BaseModel):
    """Standard response for course guide operations"""
    success: bool
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    
class CourseGuideSearchResponse(BaseModel):
    """Response model for course guide search operations"""
    success: bool
    results: List[CourseGuideResult]
    query: str
    total_results: int
    query_time_ms: float
    scope: Optional[str] = None
```

## 3. API Endpoints

### 3.1 Search Courses by Topic

```
POST /api/v1/course-guide/search
```

**Request Body:**
```json
{
  "query": "Singular Value Decomposition",
  "departments": ["MATH", "CS"],
  "level": "300",
  "scope": "covered",
  "limit": 5,
  "min_score": 0.5
}
```

**Response:**
```json
{
  "success": true,
  "results": [
    {
      "course_id": "MATH302",
      "title": "Linear Algebra II",
      "department": "MATH",
      "description": "Advanced topics in linear algebra including...",
      "score": 0.92,
      "matching_topics": [
        {
          "topic_name": "Singular Value Decomposition",
          "scope": "covered",
          "description": "Applications of SVD in data science and dimensionality reduction",
          "importance": 8,
          "week_covered": 6
        }
      ],
      "credits": 4.0,
      "level": "300",
      "semester_offered": ["Fall", "Spring"],
      "last_updated": "2024-02-10T09:45:00Z"
    },
    {
      "course_id": "CS375",
      "title": "Machine Learning Fundamentals",
      "department": "CS",
      "description": "Introduction to machine learning algorithms...",
      "score": 0.85,
      "matching_topics": [
        {
          "topic_name": "Matrix Factorization",
          "scope": "covered",
          "description": "Including SVD and applications in recommendation systems",
          "importance": 7,
          "week_covered": 5
        }
      ],
      "credits": 3.0,
      "level": "300",
      "semester_offered": ["Spring"],
      "last_updated": "2024-01-15T14:20:00Z"
    }
  ],
  "query": "Singular Value Decomposition",
  "total_results": 2,
  "query_time_ms": 50.3,
  "scope": "covered"
}
```

### 3.2 Add Course Guide

```
POST /api/v1/course-guide/add
```

**Request Body:**
```json
{
  "course_id": "CS101",
  "title": "Introduction to Computer Science",
  "department": "CS",
  "description": "Fundamental concepts of computer science including programming, algorithms, and data structures.",
  "topics": [
    {
      "topic_name": "Python Programming",
      "scope": "covered",
      "description": "Introduction to Python syntax, data types, and basic constructs",
      "importance": 9,
      "week_covered": 2,
      "related_topics": ["Programming Fundamentals", "Variables"]
    },
    {
      "topic_name": "Recursion",
      "scope": "covered",
      "description": "Basic recursive algorithms and problem-solving",
      "importance": 7,
      "week_covered": 8,
      "related_topics": ["Algorithms", "Stack Frame"]
    },
    {
      "topic_name": "Database Design",
      "scope": "excluded",
      "description": "This topic is covered in CS301",
      "importance": 1
    }
  ],
  "prerequisites": [],
  "credits": 3.0,
  "level": "100",
  "semester_offered": ["Fall", "Spring", "Summer"],
  "instructors": ["Dr. Smith", "Dr. Johnson"]
}
```

**Response:**
```json
{
  "success": true,
  "message": "Course guide added successfully",
  "data": {
    "course_id": "CS101",
    "title": "Introduction to Computer Science",
    "department": "CS"
  }
}
```

### 3.3 Update Course Guide

```
PUT /api/v1/course-guide/{course_id}
```

**Request Body:**
```json
{
  "description": "Updated description: Introduction to computer science concepts with focus on problem-solving and algorithmic thinking.",
  "topics": [
    {
      "topic_name": "Python Programming",
      "scope": "covered",
      "description": "Comprehensive introduction to Python with practical examples",
      "importance": 10,
      "week_covered": 1,
      "related_topics": ["Programming Fundamentals", "Variables", "Control Structures"]
    },
    {
      "topic_name": "Object-Oriented Programming",
      "scope": "covered",
      "description": "Introduction to classes, inheritance, and polymorphism",
      "importance": 8,
      "week_covered": 9
    }
  ],
  "semester_offered": ["Fall", "Spring"]
}
```

**Response:**
```json
{
  "success": true,
  "message": "Course guide updated successfully",
  "data": {
    "course_id": "CS101",
    "topics_added": 1,
    "topics_updated": 1,
    "topics_removed": 1,
    "last_updated": "2024-03-18T15:30:00Z"
  }
}
```

### 3.4 Delete Course Guide

```
DELETE /api/v1/course-guide/{course_id}
```

**Response:**
```json
{
  "success": true,
  "message": "Course guide deleted successfully"
}
```

### 3.5 List Departments

```
GET /api/v1/course-guide/departments
```

**Response:**
```json
{
  "success": true,
  "departments": ["CS", "MATH", "PHYS", "CHEM", "BIO"]
}
```

## 4. Service Layer

### 4.1 Course Guide Service Interface

```python
class CourseGuideService:
    """Service for managing course guides"""
    
    def __init__(self, chroma_service: ChromaService, embedding_service: EmbeddingService):
        self.chroma = chroma_service
        self.embedder = embedding_service
        self.collection_name = "course_guide_collection"
        
    async def initialize(self):
        """Initialize the course guide collection"""
        metadata = {
            "description": "Course guide collection for topic coverage information",
            "type": "course_guide",
            "schema_version": "1.0"
        }
        self.collection = await self.chroma.get_or_create_collection(
            name=self.collection_name,
            metadata=metadata
        )
        
    async def add_course_guide(self, guide_item: CourseGuideItem, user_id: str) -> str:
        """Add a new course guide to the collection"""
        # Validate course ID
        course_id = guide_item.course_id
        
        # Check if course guide already exists
        existing = await self.get_course_guide(course_id)
        if existing:
            # Delete existing course guide to replace it
            await self.delete_course_guide(course_id)
            
        # Add updated_by if not provided
        if not guide_item.updated_by:
            guide_item.updated_by = user_id
            
        # Convert to dict for storage
        guide_dict = guide_item.model_dump()
        
        # Process each topic into a separate document for better search
        documents = []
        metadatas = []
        ids = []
        embeddings = []
        
        # Store base course info
        base_document = (
            f"COURSE: {guide_item.course_id} - {guide_item.title}\n"
            f"DEPARTMENT: {guide_item.department}\n"
            f"DESCRIPTION: {guide_item.description}"
        )
        
        base_metadata = {
            "course_id": course_id,
            "title": guide_item.title,
            "department": guide_item.department,
            "credits": guide_item.credits,
            "level": guide_item.level,
            "semester_offered": ",".join(guide_item.semester_offered),
            "prerequisites": ",".join(guide_item.prerequisites),
            "instructors": ",".join(guide_item.instructors),
            "updated_by": guide_item.updated_by,
            "last_updated": guide_item.last_updated.isoformat(),
            "type": "course_guide",
            "is_topic": False  # This is the base course document
        }
        
        base_id = f"course_{course_id}_base"
        base_embedding = self.embedder.generate_embedding(base_document)
        
        documents.append(base_document)
        metadatas.append(base_metadata)
        ids.append(base_id)
        embeddings.append(base_embedding)
        
        # Process each topic
        for i, topic in enumerate(guide_item.topics):
            # Create topic document with additional context
            topic_document = (
                f"COURSE: {guide_item.course_id} - {guide_item.title}\n"
                f"TOPIC: {topic.topic_name}\n"
                f"SCOPE: {topic.scope.value}\n"
                f"DESCRIPTION: {topic.description or ''}"
            )
            
            # Create topic metadata
            topic_metadata = {
                "course_id": course_id,
                "title": guide_item.title,
                "department": guide_item.department,
                "credits": guide_item.credits,
                "level": guide_item.level,
                "semester_offered": ",".join(guide_item.semester_offered),
                "topic_name": topic.topic_name,
                "scope": topic.scope.value,
                "importance": topic.importance,
                "week_covered": topic.week_covered,
                "related_topics": ",".join(topic.related_topics) if topic.related_topics else "",
                "updated_by": guide_item.updated_by,
                "last_updated": guide_item.last_updated.isoformat(),
                "type": "course_guide",
                "is_topic": True  # This is a topic document
            }
            
            topic_id = f"course_{course_id}_topic_{i}"
            topic_embedding = self.embedder.generate_embedding(topic_document)
            
            documents.append(topic_document)
            metadatas.append(topic_metadata)
            ids.append(topic_id)
            embeddings.append(topic_embedding)
        
        # Store in collection in batches (if needed)
        batch_size = 32
        for i in range(0, len(documents), batch_size):
            batch_docs = documents[i:i + batch_size]
            batch_meta = metadatas[i:i + batch_size]
            batch_ids = ids[i:i + batch_size]
            batch_embeddings = embeddings[i:i + batch_size]
            
            await self.chroma.add_documents(
                collection_name=self.collection_name,
                documents=batch_docs,
                metadatas=batch_meta,
                ids=batch_ids,
                embeddings=batch_embeddings
            )
        
        return course_id
        
    async def search_courses(self, search_query: CourseGuideSearchQuery) -> Tuple[int, List[CourseGuideResult]]:
        """Search for courses based on the query"""
        # Prepare filters
        filters = {"is_topic": True}  # Always search in topics
        
        if search_query.departments:
            dept_conditions = []
            for dept in search_query.departments:
                dept_conditions.append({"department": dept})
            if dept_conditions:
                filters = {"$and": [filters, {"$or": dept_conditions}]}
        
        if search_query.level:
            level_filter = {"level": search_query.level}
            if "$and" in filters:
                filters["$and"].append(level_filter)
            else:
                filters = {"$and": [filters, level_filter]}
        
        if search_query.scope:
            scope_filter = {"scope": search_query.scope.value}
            if "$and" in filters:
                filters["$and"].append(scope_filter)
            else:
                filters = {"$and": [filters, scope_filter]}
        
        # Generate embedding for query
        query_embedding = self.embedder.generate_embedding(search_query.query)
        
        # Search collection
        results = await self.chroma.search(
            collection_name=self.collection_name,
            query=search_query.query,
            query_embedding=query_embedding,
            n_results=search_query.limit * 3,  # Get more results to account for course deduplication
            where=filters,
            include_metadata=True,
            include_values=True
        )
        
        # Process results
        course_results = []
        seen_courses = set()
        
        for i, (doc, metadata, score) in enumerate(zip(results.documents, results.metadatas, results.distances)):
            # Convert distance to similarity score (1 - distance)
            similarity = 1.0 - min(score, 1.0)
            
            # Skip results below minimum score
            if similarity < search_query.min_score:
                continue
                
            # Get course ID
            course_id = metadata.get("course_id")
            
            # Skip if we've already processed this course
            if course_id in seen_courses:
                continue
                
            seen_courses.add(course_id)
            
            # Find all matching topics for this course
            matching_topics = []
            for j, (topic_doc, topic_meta, topic_score) in enumerate(zip(results.documents, results.metadatas, results.distances)):
                if topic_meta.get("course_id") == course_id and topic_meta.get("is_topic", False):
                    topic_similarity = 1.0 - min(topic_score, 1.0)
                    if topic_similarity >= search_query.min_score:
                        matching_topic = CourseTopicResult(
                            topic_name=topic_meta.get("topic_name", ""),
                            scope=TopicScope(topic_meta.get("scope", "covered")),
                            description=None,  # We could extract this from the document if needed
                            importance=topic_meta.get("importance", 5),
                            week_covered=topic_meta.get("week_covered")
                        )
                        matching_topics.append(matching_topic)
            
            # Get semesters as list
            semesters = metadata.get("semester_offered", "").split(",") if metadata.get("semester_offered") else []
            
            # Create result object
            guide_result = CourseGuideResult(
                course_id=course_id,
                title=metadata.get("title", ""),
                department=metadata.get("department", ""),
                description=self._extract_description(doc),
                score=similarity,
                matching_topics=matching_topics,
                credits=metadata.get("credits", 0.0),
                level=metadata.get("level", ""),
                semester_offered=semesters,
                last_updated=datetime.fromisoformat(metadata.get("last_updated", datetime.utcnow().isoformat()))
            )
            course_results.append(guide_result)
            
            # Limit results
            if len(course_results) >= search_query.limit:
                break
                
        return len(course_results), course_results
        
    def _extract_description(self, doc: str) -> str:
        """Extract course description from document"""
        if "DESCRIPTION: " in doc:
            return doc.split("DESCRIPTION: ", 1)[1].strip()
        return ""
        
    async def get_course_guide(self, course_id: str) -> Optional[Dict[str, Any]]:
        """Get a course guide by ID"""
        try:
            base_id = f"course_{course_id}_base"
            results = await self.chroma.get(
                collection_name=self.collection_name,
                ids=[base_id],
                include_metadata=True
            )
            
            if not results.documents or len(results.documents) == 0:
                return None
                
            # Get topic documents for this course
            topic_results = await self.chroma.search(
                collection_name=self.collection_name,
                query="",  # Empty query to get all topics
                n_results=100,  # Assume no course has more than 100 topics
                where={"$and": [{"course_id": course_id}, {"is_topic": True}]},
                include_metadata=True
            )
            
            # Get base metadata
            base_metadata = results.metadatas[0]
            
            # Process topics
            topics = []
            for i, topic_meta in enumerate(topic_results.metadatas):
                if topic_meta.get("is_topic"):
                    related_topics = topic_meta.get("related_topics", "").split(",") if topic_meta.get("related_topics") else []
                    topic = {
                        "topic_name": topic_meta.get("topic_name", ""),
                        "scope": topic_meta.get("scope", "covered"),
                        "importance": topic_meta.get("importance", 5),
                        "week_covered": topic_meta.get("week_covered"),
                        "related_topics": related_topics
                    }
                    topics.append(topic)
            
            # Create result with all information
            result = {
                "course_id": course_id,
                "title": base_metadata.get("title", ""),
                "department": base_metadata.get("department", ""),
                "description": self._extract_description(results.documents[0]),
                "topics": topics,
                "credits": base_metadata.get("credits", 0.0),
                "level": base_metadata.get("level", ""),
                "semester_offered": base_metadata.get("semester_offered", "").split(",") if base_metadata.get("semester_offered") else [],
                "prerequisites": base_metadata.get("prerequisites", "").split(",") if base_metadata.get("prerequisites") else [],
                "instructors": base_metadata.get("instructors", "").split(",") if base_metadata.get("instructors") else [],
                "last_updated": base_metadata.get("last_updated")
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting course guide {course_id}: {str(e)}")
            return None
        
    async def update_course_guide(self, course_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a course guide"""
        # Get existing course guide
        existing = await self.get_course_guide(course_id)
        if not existing:
            return None
            
        # Merge existing and update data
        merged = {**existing}
        
        # Special handling for topics - if provided, fully replace
        if "topics" in update_data:
            merged["topics"] = update_data.pop("topics")
            
        # Update remaining fields
        for key, value in update_data.items():
            merged[key] = value
            
        # Create CourseGuideItem from merged data
        topics = []
        for topic_data in merged["topics"]:
            related_topics = topic_data.get("related_topics", [])
            topic = CourseTopic(
                topic_name=topic_data["topic_name"],
                scope=TopicScope(topic_data["scope"]),
                description=topic_data.get("description"),
                importance=topic_data.get("importance", 5),
                week_covered=topic_data.get("week_covered"),
                related_topics=related_topics
            )
            topics.append(topic)
            
        guide_item = CourseGuideItem(
            course_id=course_id,
            title=merged["title"],
            department=merged["department"],
            description=merged["description"],
            topics=topics,
            prerequisites=merged["prerequisites"],
            credits=merged["credits"],
            level=merged["level"],
            semester_offered=merged["semester_offered"],
            instructors=merged["instructors"],
            last_updated=datetime.utcnow(),
            updated_by=update_data.get("updated_by")
        )
        
        # Delete existing guide and add updated one
        await self.delete_course_guide(course_id)
        await self.add_course_guide(guide_item, update_data.get("updated_by", "system"))
        
        # Return counts of changes
        return {
            "course_id": course_id,
            "topics_added": len(guide_item.topics) - len(existing["topics"]),
            "topics_updated": min(len(guide_item.topics), len(existing["topics"])),
            "topics_removed": max(0, len(existing["topics"]) - len(guide_item.topics)),
            "last_updated": guide_item.last_updated.isoformat()
        }
        
    async def delete_course_guide(self, course_id: str) -> bool:
        """Delete a course guide"""
        try:
            # Delete all documents with this course_id
            await self.chroma.delete(
                collection_name=self.collection_name,
                where={"course_id": course_id}
            )
            return True
        except Exception as e:
            logger.error(f"Error deleting course guide {course_id}: {str(e)}")
            return False
            
    async def get_departments(self) -> List[str]:
        """Get all unique departments"""
        try:
            results = await self.chroma.get_metadata_keys(
                collection_name=self.collection_name,
                key="department"
            )
            return sorted(list(set(results)))
        except Exception as e:
            logger.error(f"Error getting departments: {str(e)}")
            return []
```

## 5. Implementation Notes

### 5.1 Embedding Strategy

The Course Guide database uses a dual embedding approach:

1. **Base Course Document**: Contains general course information
2. **Topic Documents**: Each topic is stored as a separate document with context

This approach allows:
- Precise search for specific topics
- Easy filtering by scope (covered/excluded)
- Efficient retrieval of course-topic relationships

### 5.2 Storage Considerations

Each course generates multiple documents:
- One base document with course information
- One document per topic (typically 5-20 topics per course)

For a university with 1,000 courses and an average of 10 topics per course, we would have approximately 11,000 documents in the collection.

### 5.3 Security

Course Guide data should be public and accessible to all users. However, modifications should be restricted to administrators and authorized academic staff.

### 5.4 Testing Strategy

Key test cases should include:
- Adding courses with varying numbers of topics and scopes
- Searching for specific topics across departments
- Testing topic scope filtering (covered vs. excluded)
- Verifying course updates properly replace all topic documents
- Performance testing with a realistic number of courses

## 6. Integration with Other Components

### 6.1 Perceptron Chat Assistant

The Perceptron assistant can use the Course Guide database to answer questions like:
- "Which courses cover machine learning?"
- "What math courses include linear algebra?"
- "Does CS101 teach recursion?"

### 6.2 Course Content Database

The Course Guide database complements the Course Content database:
- Course Guide: High-level topic coverage information
- Course Content: Detailed lecture materials and content

When students search for topics, the system should present both:
1. Courses covering the topic (from Course Guide)
2. Specific lectures and materials (from Course Content)

## 7. Future Enhancements

1. **Topic Taxonomy**: Implement a hierarchical topic structure
2. **Prerequisite Mapping**: Visual representation of course prerequisites
3. **Topic Learning Path**: Suggest sequence of courses to master a topic
4. **Course Similarity**: Find courses with similar topic coverage
5. **Topic Gap Analysis**: Identify topics not covered across the curriculum 