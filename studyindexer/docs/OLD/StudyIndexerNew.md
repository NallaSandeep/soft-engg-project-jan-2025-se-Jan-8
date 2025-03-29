### StudyIndexerNew New Development Initial Plan###

## 1. Project Overview

StudyIndexerNew is a complete rewrite of the existing StudyIndexer module, which provides vector database capabilities for the larger system that includes StudyHub (learning portal) and StudyAI (chat API). The system consists of multiple vector databases backed by ChromaDB and provides semantic search capabilities across various educational content.

### 1.1 Project Context
- Academic project with a 1-2 day implementation timeline
- Focus on MVP/demo level functionality, not production-level features
- New implementation will be in the StudyIndexerNew folder
- Existing code in studyindexer folder can serve as reference

## 2. System Architecture

### 2.1 Vector Databases
The system will implement the following vector databases, each as a separate ChromaDB collection:

1. **FAQ Database**
   - Stores static institutional information (policies, guidelines, etc.)
   - Public access, single-table structure
   - Simple question-answer format with tags

2. **Course Guide Database**
   - Stores semantic descriptions of topic coverage per course
   - Identifies which topics are covered or excluded in each course
   - Public access with course-level metadata

3. **Course Content Database**
   - Stores lecture-level content (texts, PDF content, video transcripts)
   - Rich metadata including course_id, week_id, lecture_id
   - Filterable by course and week

4. **Personal Resources Database**
   - User-uploaded notes stored privately per student
   - Accessible only by the respective student
   - Course-specific organization

5. **Integrity Check Database** (Optional)
   - Stores assignment questions to check for academic integrity
   - Performs similarity checks against student queries

### 2.2 Core Components

1. **Embedding Service**
   - Central service for generating text embeddings
   - Uses sentence-transformers (`all-MiniLM-L6-v2`)
   - Supports both synchronous and asynchronous processing
   - Handles document chunking for large texts

2. **ChromaDB Service**
   - Manages specialized collections for each vector database
   - Handles CRUD operations for vector storage
   - Provides filtered semantic search capabilities

3. **API Layer**
   - FastAPI endpoints for each vector database
   - Consistent request/response formats
   - Input validation and error handling

## 3. Technical Requirements

### 3.1 API Endpoints

#### FAQ Database
```
POST /faq/search
Input: { 'query': 'Can I carry a calculator to the exam?' }
Output: Top-K FAQ vector chunks (text)

POST /faq/add
Input: { 'text': 'Calculators are allowed in exams unless stated otherwise.', 'tags': ['exam', 'policy'] }
```

#### Course Guide Database
```
POST /course-guide/search
Input: { 'query': 'Which courses cover SVD?' }
Output: List of { course_id, scope, score }

POST /course-guide/add
Input: { 'course_id': 'MATH202', 'covered_topics': [...], 'excluded_topics': [...] }
```

#### Course Content Database
```
POST /course-content/search
Input: { 'query': 'Explain recursion', 'filters': { 'course_id': 'CS101', 'week_id': 'W3' } }
Output: Top-K lecture chunks

POST /course-content/add
Input: { 'course_id': 'CS101', 'week_id': 'W3', 'lecture_id': 'L2', 'text': '...', 'topics': ['Recursion'] }
```

#### Personal Resources Database
```
POST /personal-resources/search
Input: { 'query': 'Sorting in Java', 'filters': { 'course_id': 'CS102', 'topic': 'Sorting' } }
Output: Top-K lecture chunks

POST /personal-resources/add
Input: { 'course_id': 'CS102', 'text': '...', 'topics': ['Merge Sort'] }
```

#### Integrity Check Database
```
POST /integrity-check/check
Input: { 'query': 'Explain pointers in C' }
Output: List of { question_id, similarity_score }

POST /integrity-check/add
Input: { 'course_id': 'CS101', 'assignment_id': 'A1', 'question_text': 'Explain pointers in C' }
```

### 3.2 Data Models

#### FAQ Item
```python
class FAQItem(BaseModel):
    question: str
    answer: str
    category: str
    tags: List[str] = []
    source: Optional[str] = None
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None
    is_published: bool = True
    priority: int = 0
```

#### Course Guide Item
```python
class TopicScope(str, Enum):
    COVERED = "covered"
    EXCLUDED = "excluded"
    PREREQUISITE = "prerequisite"
    ADVANCED = "advanced"

class CourseTopic(BaseModel):
    topic_name: str
    scope: TopicScope
    description: Optional[str] = None
    importance: int = 5
    week_covered: Optional[int] = None
    related_topics: List[str] = []

class CourseGuideItem(BaseModel):
    course_id: str
    title: str
    department: str
    description: str
    topics: List[CourseTopic]
    prerequisites: List[str] = []
    credits: float
    level: str
    semester_offered: List[str]
    instructors: List[str] = []
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    updated_by: Optional[str] = None
```

#### Course Content Item
```python
class CourseContentItem(BaseModel):
    course_id: str
    week_id: str
    lecture_id: str
    text: str
    topics: List[str]
    title: Optional[str] = None
    source_type: Optional[str] = None  # pdf, video, notes, etc.
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None
```

#### Personal Resource Item
```python
class PersonalResourceItem(BaseModel):
    user_id: str
    course_id: str
    text: str
    topics: List[str]
    title: Optional[str] = None
    source_type: Optional[str] = None
    last_updated: datetime = Field(default_factory=datetime.utcnow)
```

#### Integrity Check Item
```python
class IntegrityCheckItem(BaseModel):
    course_id: str
    assignment_id: str
    question_id: str  # Generated
    question_text: str
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None
```

## 4. Implementation Plan

### 4.1 Project Structure
```
StudyIndexerNew/
├── app/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── course_content.py
│   │   ├── course_guide.py
│   │   ├── faq.py
│   │   ├── integrity.py
│   │   └── personal.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── errors.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── course_content.py
│   │   ├── course_guide.py
│   │   ├── faq.py
│   │   ├── integrity.py
│   │   └── personal.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── chroma.py
│   │   ├── embeddings.py
│   │   └── integrity.py
│   ├── utils/
│   │   ├── __init__.py
│   │   └── text.py
│   └── __init__.py
├── main.py
└── requirements.txt
```

### 4.2 Implementation Phases

For a 1-2 day implementation window, we'll prioritize the following phases:

#### Phase 1: Core Infrastructure (Priority)
1. Setup project structure
2. Implement embedding service
3. Implement ChromaDB service with specialized collections
4. Setup basic FastAPI application

#### Phase 2: FAQ Database (Priority)
1. Implement FAQ models
2. Implement FAQ service
3. Create FAQ API endpoints

#### Phase 3: Course Guide Database
1. Implement Course Guide models
2. Implement Course Guide service
3. Create Course Guide API endpoints

#### Phase 4: Additional Databases (If Time Permits)
1. Implement Course Content database
2. Implement Personal Resources database
3. Implement Integrity Check database

### 4.3 Implementation Details

#### Embedding Service
- Implement as per Embedding_Service_Implementation.md
- Support both synchronous and asynchronous operations
- Include document chunking for large texts

#### ChromaDB Service
- Create specialized collections for each database
- Implement basic CRUD operations
- Support filtered semantic search

#### API Layer
- Implement FastAPI endpoints for each database
- Add validation using Pydantic models
- Include proper error handling

## 5. Technical Considerations

### 5.1 Performance Optimization
- Batch processing for embeddings
- Efficient chunking strategies for large documents
- Index optimization in ChromaDB

### 5.2 Security
- Implement proper access controls for personal resources
- Validate inputs to prevent injection attacks

### 5.3 Testing
- Basic functional tests for each endpoint
- Simple integration tests for the embedding flow

## 6. Evaluation Criteria
Given the academic nature and time constraints, we'll focus on:
1. Functional correctness of the vector search
2. Basic API functionality
3. Proper embedding and retrieval
4. Simple, clean architecture

## 7. References
- VectorDB_AI_Layer_Spec.md - Core requirements
- Course_Guide_Implementation.md - Course Guide details
- Embedding_Service_Implementation.md - Embedding service implementation
- FAQ_Database_Implementation.md - FAQ database implementation
- StudyIndexer_Rewrite_Plan.md - Original rewrite plan
- Existing codebase in studyindexer folder 