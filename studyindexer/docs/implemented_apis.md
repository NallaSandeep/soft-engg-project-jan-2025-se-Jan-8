# StudyIndexer Implemented APIs

Based on the provided initialization and sync scripts, the following APIs have been implemented:

## 1. PersonalResource API

This API allows searching and retrieving student-specific resources.

### Test Command:
```bash
curl -X 'GET' \
  'http://localhost:8081/api/v1/personal-resource/search?query=notes&student_id=3&limit=5' \
  -H 'accept: application/json'
```

### Adding a Personal Resource:
```bash
curl -X 'POST' \
  'http://localhost:8081/api/v1/personal-resource/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "resource_info": {
      "id": 123,
      "title": "Database Systems Notes",
      "description": "My personal notes for the Database Systems course",
      "content": "Important concepts: SQL, joins, normalization, transactions...",
      "type": "note",
      "course_id": 2,
      "student_id": 3,
      "tags": ["database", "notes", "sql"],
      "metadata": {
        "resource_type": "note",
        "is_private": true,
        "created_at": "2023-01-15T10:30:00",
        "updated_at": "2023-01-15T10:30:00"
      }
    }
  }'
```

## 2. IntegrityCheck API

This API checks submissions against graded assignments to identify potential academic integrity violations.

### Test Command:
```bash
curl -X 'POST' \
  'http://localhost:8081/api/v1/integrity-check/check' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "query": "To retrieve the name and email of all customers who have placed an order in the last 30 days, I would use the following SQL query: SELECT c.customer_name, c.email FROM Customers c JOIN Orders o ON c.customer_id = o.customer_id WHERE o.order_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY) GROUP BY c.customer_id;",
    "course_ids": ["2"],
    "threshold": 0.7
  }'
```

### Index an Assignment:
```bash
curl -X 'POST' \
  'http://localhost:8081/api/v1/integrity-check/index' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "assignment_id": "DBMS201_MIDTERM",
    "course_id": "2",
    "course_code": "DBMS201",
    "course_title": "Database Management Systems",
    "title": "Database Systems Midterm Exam",
    "description": "Midterm examination covering SQL queries",
    "questions": [
      {
        "question_id": "q1",
        "title": "SQL Joins",
        "content": "Write a SQL query to retrieve the name and email of all customers who have placed an order in the last 30 days. Use the Customers and Orders tables.",
        "type": "open_ended"
      }
    ]
  }'
```

## 3. CourseContent API

This API provides detailed content from courses for retrieval-augmented generation.

### Test Command:
```bash
curl -X 'GET' \
  'http://localhost:8081/api/v1/course-content/search?query=database%20systems&limit=5' \
  -H 'accept: application/json'
```

## 4. CourseSelector API

This API helps identify which courses contain information relevant to a student's query.

### Test Command:
```bash
curl -X 'POST' \
  'http://localhost:8081/api/v1/course-selector/search' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "query": "database management SQL queries",
    "subscribed_courses": ["DBMS201", "MAD-II", "CS401"],
    "limit": 5,
    "min_score": 0.5
  }'
```

## Implementation Notes

These APIs align with the API specifications in the `API-SPECS.md` document. The implementation prioritized:

1. **Personal Resources Integration**: Syncing student resources between StudyHub and StudyIndexer
2. **Academic Integrity**: Implementing the IntegrityCheck API for checking submissions against graded assignments
3. **Course Content Retrieval**: Indexing course content for search and retrieval
4. **Course Selection**: Identifying relevant courses for student queries

The implementation allows for both:
- Automatic syncing during database initialization (`init_db.py`)
- Manual syncing through standalone scripts (`sync_resources.py`, `sync_assignments.py`) 