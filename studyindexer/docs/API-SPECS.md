# StudyIndexer API Documentation
## Overview

The StudyIndexer module serves as a Retrieval Augmented Generation (RAG) data source for StudyAI. It provides structured access to course content, FAQs, personal resources, and integrity checking services through a set of specialized APIs.

### Core Components

1. **CourseSelector**: Identifies which courses match a specific query from the student's subscribed courses
2. **CourseContent**: Retrieves specific content chunks (lectures, topics, etc.) that match a query
3. **FAQ**: Provides answers to frequently asked questions across courses
4. **PersonalResource**: Retrieves student-specific resources matching a query
5. **IntegrityCheck**: Evaluates if student queries match graded assignments to maintain academic integrity

### Integration Flow (How should StudyAI integrate with/use it)
Here is the complete story:
When a student using StudyHub initiates a chat with StudyAI:

1. StudyAI receives the student ID and list of subscribed courses(and list of personal resources)
2. When the student asks a question, StudyAI's agent processes it
3. The agent breaks down the question into components (sub-questions)
4. Relevant StudyIndexer endpoints are queried to retrieve contextual information
5. StudyAI formulates a response using the retrieved information



## API Specifications
### 1. CourseSelector API

Helps identify which courses contain information relevant to a student's query.

```yaml
/api/v1/course-selector/search:
  post:
    summary: Find courses matching a query from subscribed courses
    parameters:
      - name: query
        description: The search query text
        required: true
      - name: subscribed_courses
        description: List of course IDs the student is subscribed to
        required: true
      - name: limit
        description: Maximum number of results to return
        required: false
        default: 10
      - name: min_score
        description: Minimum relevance score threshold
        required: false
        default: 0.0
    returns:
      success: Boolean
      data:
        results: Array of CourseMatchResult objects
        metadata:
          query_time_ms: Query execution time in milliseconds
          total_results: Total number of matching courses
```

**Example Request:**
```json
{
  "query": "What is singular value decomposition?",
  "subscribed_courses": ["MATH301", "CS350", "PHYS201"],
  "limit": 5,
  "min_score": 0.6
}
```

**Example Response:**
```json
{
  "success": true,
  "data": {
    "results": [
      {
        "course_id": "MATH301",
        "code": "MATH301",
        "title": "Linear Algebra",
        "description": "Advanced course covering vector spaces, matrices, and transformations",
        "score": 0.92,
        "matched_topics": ["singular value decomposition", "matrix factorization", "eigenvalues"],
        "weeks": [3, 4]
      },
      {
        "course_id": "CS350",
        "code": "CS350",
        "title": "Machine Learning",
        "description": "Introduction to machine learning algorithms and applications",
        "score": 0.75,
        "matched_topics": ["singular value decomposition", "dimensionality reduction"],
        "weeks": [7]
      }
    ],
    "metadata": {
      "query_time_ms": 156,
      "total_results": 2
    }
  }
}
```

**Intended Use by StudyAI:**
The primary response is the course_id which crosses your threshold (score). But you should use additional details available to set the environment/context for the chat. If the same additional details are repeated in consecutive messages, it should become the theme of the chat.

For example, if the response returns courseID MATH301 and matched_topics as SVD, EigenValues with a high score, and this happens in more than one conversation/message, then set these values in the session, use them in the LLM instructions, and also pass them in the next query to StudyIndexer, especially when calling /course-content/search. This search otherwise will return many results, but filtering content using topics will make results more relevant and rich.




### 2. CourseContent API
Provides detailed content chunks from courses for retrieval-augmented generation.

```yaml
/api/v1/course-content/search:
  get:
    summary: Search for specific content chunks matching a query
    parameters:
      - name: query
        description: The search query text
        required: true
      - name: course_ids
        description: Optional list of course IDs to filter search results
        required: false
      - name: limit
        description: Maximum number of results to return
        required: false
        default: 10
    returns:
      success: Boolean
      data:
        content_chunks: Array of content chunks with source information
        total_count: Total number of matching chunks
        query: The original query
        limit: Applied limit value
```

**Example Request:**
```
GET /api/v1/course-content/search?query=singular%20value%20decomposition&course_ids=MATH301&limit=3
```

**Example Response:**
```json
{
  "success": true,
  "data": {
    "content_chunks": [
      {
        "source_course": {
          "code": "MATH301",
          "title": "Linear Algebra",
          "match_score": 0.94
        },
        "content_chunks": [
          {
            "type": "lecture",
            "title": "Singular Value Decomposition",
            "description": "Introduction to SVD and its applications",
            "content": "Singular Value Decomposition (SVD) is a factorization of a real or complex matrix. It generalizes the eigendecomposition of a square normal matrix to any m×n matrix. For a matrix M, the SVD is given by M = UΣV*, where U and V are orthogonal matrices and Σ is a diagonal matrix of singular values...",
            "week_number": 3
          },
          {
            "type": "topic",
            "name": "Matrix Factorization Techniques",
            "description": "Overview of techniques including SVD, QR, and LU decomposition"
          }
        ],
        "score": 0.94
      }
    ],
    "total_count": 1,
    "query": "singular value decomposition",
    "limit": 3
  }
}
```

**Intended Use by StudyAI:**
Pass these results to the LLM for better contextual understanding of the content and rich response generation. Instruct the LLM to include citations in the response. For example, if the LLM chooses a particular text chunk to explain a concept, it should mention the lecture and course name as a small note, demonstrating effective RAG implementation.

The response includes topic and week information which is helpful - instruct the LLM to align its response accordingly to provide better context and educational relevance to the student.




### 3. FAQ API

Provides answers to frequently asked questions related to courses.

```yaml
/api/v1/faq/search:
  post:
    summary: Search for FAQs matching a query
    parameters:
      - name: query
        description: The search query text
        required: true
      - name: limit
        description: Maximum number of results to return
        required: false
        default: 10
      - name: min_score
        description: Minimum relevance score threshold
        required: false
        default: 0.3
      - name: tags
        description: Optional tags to filter FAQs
        required: false
      - name: topic
        description: Optional topic to filter FAQs
        required: false
      - name: source
        description: Optional source to filter FAQs
        required: false
    returns:
      success: Boolean
      query: The original query
      total_results: Total number of matching FAQs
      query_time_ms: Query execution time in milliseconds
      results: Array of matching FAQ items with relevance scores
```

**Example Request:**
```json
{
  "query": "exam",
  "limit": 10,
  "min_score": 0.3,
  "tags": [""],
  "topic": "",
  "source": ""
}
```

**Example Response:**
```json
{
  "success": true,
  "query": "exam",
  "total_results": 10,
  "query_time_ms": 74.52750205993652,
  "results": [
    {
      "id": "faq_488b98f9cf874a779ce1ff342a5371c4",
      "topic": "Examination",
      "question": "When is the next examination",
      "answer": "The next examinationis in december",
      "tags": [],
      "score": 0.6002491414546967,
      "source": "Official_IITM_Site",
      "last_updated": "2025-03-27T13:44:19.400825"
    },
    {
      "id": "faq_e02319007af2480abae3e08740683718",
      "topic": "Eligibility Criteria",
      "question": "What else should students know about Eligibility Criteria? (Part 48)",
      "answer": "2 proctored Quizzes - to be attempted in person in the city chosen Two quizzes will be conducted at the end of Weeks 4 and 8 based on the content of Weeks 1-4 and 1-8 respectively...",
      "tags": ["eligibility", "criteria"],
      "score": 0.5420083701610565,
      "source": "Student_Handbook_Jan_2025",
      "last_updated": "2025-03-27T21:34:58.398681"
    }
  ]
}
```

**Intended Use by StudyAI:**
MUST mention the "source" for an FAQ response. Multiple sources exist for FAQs such as Student Handbook, Grading Document, and Official Website. Instruct the LLM to cite the source of information and possibly the date so the student knows if the data is current or potentially stale. This attribution is critical for providing accurate policy and procedural information to students.





### 4. PersonalResource API

Retrieves student-specific resources that match a query.

```yaml
/api/v1/personal-resource/search:
  get:
    summary: Search for personal resources matching a query
    parameters:
      - name: query
        description: The search query text
        required: true
      - name: student_id
        description: Student ID to retrieve personal resources for
        required: true
      - name: personal_resource_ids
        description: Optional list of personal resource IDs to filter by
        required: false
      - name: limit
        description: Maximum number of results to return
        required: false
        default: 10
    returns:
      success: Boolean
      data:
        resources: Array of matching personal resources with relevance scores
        total_count: Total number of matching resources
        query: The original query
```

**Example Request:**
```
GET /api/v1/personal-resource/search?query=singular%20value%20decomposition&student_id=S12345&limit=2
```

**Example Response:**
```json
{
  "success": true,
  "data": {
    "resources": [
      {
        "resource_id": "PR789",
        "title": "SVD Applications in Image Compression",
        "description": "My notes on using SVD for image compression techniques",
        "content": "Singular Value Decomposition can be used for image compression by...",
        "type": "note",
        "course_id": "MATH301",
        "score": 0.91
      },
      {
        "resource_id": "PR542",
        "title": "Prof. Smith's Lecture Notes on Matrix Decomposition",
        "description": "PDF notes from supplementary lecture",
        "content": "These notes cover various matrix decomposition methods with focus on SVD...",
        "type": "pdf",
        "course_id": "MATH301",
        "score": 0.85
      }
    ],
    "total_count": 2,
    "query": "singular value decomposition"
  }
}
```

**Intended Use by StudyAI:**
Instruct LLM to use the title of the response so the student knows which note has been accessed for providing the answer. The LLM must clearly reference the personal resource title when using this information, helping students connect the AI response with their own materials and improving their learning experience through these connections.




### 5. IntegrityCheck API

Checks if a query potentially matches graded assignments to maintain academic integrity.

```yaml
/api/v1/integrity-check/check:
  post:
    summary: Check if a query matches any graded assignments
    parameters:
      - name: query
        description: The query text to check against graded assignments
        required: true
      - name: course_ids
        description: Optional list of course IDs to limit the check
        required: false
      - name: threshold
        description: Minimum score threshold to consider a match
        required: false
        default: 0.8
    returns:
      success: Boolean
      data:
        matches: Array of matching graded assignments with similarity scores
        highest_match: Details of the highest matching assignment
        is_potential_violation: Boolean indicating if any match exceeded threshold
```

**Example Request:**
```json
{
  "query": "Derive the formula for singular value decomposition and explain its applications",
  "course_ids": ["MATH301"],
  "threshold": 0.85
}
```

**Example Response:**
```json
{
  "success": true,
  "data": {
    "matches": [
      {
        "assignment_id": "GA456",
        "title": "Homework 5: Matrix Decompositions",
        "question": "Question 2: Derive the formula for singular value decomposition and explain how it can be applied to image compression",
        "course_id": "MATH301",
        "score": 0.89,
        "match_details": {
          "matched_segments": ["Derive the formula for singular value decomposition", "applications"]
        }
      }
    ],
    "highest_match": {
      "assignment_id": "GA456",
      "title": "Homework 5: Matrix Decompositions",
      "score": 0.89
    },
    "is_potential_violation": true
  }
}
```

**Intended Use by StudyAI:**
It is important that the LLM understands which part of the content segment is matching with the graded assignment. This is why this response is particularly rich in detail. The LLM can decide to change that specific part of the query and also warn the user by citing which graded assignment/homework the question is very close to. This helps maintain academic integrity while still providing educational value.








## Integrated Example Scenario

### Student Question
A student asks StudyAI: "What is singular value decomposition and is it important for my end term exams?"

### API Flow

1. **CourseSelector API** is called first to identify relevant courses:
   ```
   POST /api/v1/course-selector/search
   {
     "query": "singular value decomposition end term exams",
     "subscribed_courses": ["MATH301", "CS350", "PHYS201"]
   }
   ```
   Result: MATH301 (Linear Algebra) is identified as the most relevant course.

2. **CourseContent API** is called to retrieve specific content:
   ```
   GET /api/v1/course-content/search?query=singular%20value%20decomposition&course_ids=MATH301
   ```
   Result: Detailed explanation of SVD from Linear Algebra course.

3. **FAQ API** is called to get information about exam importance:
   ```
   POST /api/v1/faq/search
   {
     "query": "Important weeks for End Term exam"
   }
   ```
   Result: FAQ says most weeks are imporant.

4. **PersonalResource API** is optionally called if the student has related notes:
   ```
   GET /api/v1/personal-resource/search?query=singular%20value%20decomposition&student_id=S12345
   ```
   Result: Student's personal notes on SVD applications.

5. **IntegrityCheck API** is called to ensure the question doesn't match a current assignment:
   ```
   POST /api/v1/integrity-check/check
   {
     "query": "What is singular value decomposition and is it important for my end term exams?",
     "course_ids": ["MATH301"]
   }
   ```
   Result: No integrity concerns found.

6. StudyAI combines these results to generate a comprehensive response about SVD, its importance for exams, and reference to the student's own notes.

## Additional Notes

### ID Consistency
- Course IDs must match between StudyHub and StudyIndexer
- Personal resource IDs must match between StudyHub and StudyIndexer
- Student IDs must be consistent across platforms

### Response Format
- All endpoints follow a standard BaseResponse format with success, message (optional), and data fields
- All search responses include the original query and total count for validation
- The "data" field structure is specific to each endpoint

### Validation Rules
1. Course IDs should be valid identifiers from StudyHub
2. Queries should be between 3 and 1000 characters
3. Limit parameters should be between 1 and 100
4. Student IDs must be authenticated via StudyHub