# StudyIndexer API Overview

## Core Services

StudyIndexer provides the following core services:

1. **CourseSelector API**: Helps identify which courses contain information relevant to a query
   - Endpoint: `/api/v1/course-selector`
   - Primary function: Find courses matching a query from a student's subscribed courses

2. **CourseContent API**: Provides course content for RAG applications
   - Endpoint: `/api/v1/course-content`
   - Primary function: Retrieve specific content (lectures, topics, etc.) matching a query

3. **FAQ API**: Provides answers to frequently asked questions
   - Endpoint: `/api/v1/faq`
   - Primary function: Return relevant FAQ items based on a query

4. **PersonalResource API**: Manages personal resources for students
   - Endpoint: `/api/v1/personal-resource`
   - Primary function: Index and search personal resources like notes and files

5. **IntegrityCheck API**: Checks submissions against graded assignments
   - Endpoint: `/api/v1/integrity-check`
   - Primary function: Identify potential academic integrity violations by comparing submissions to assignments

## API Endpoints

### Course Selector

- `POST /api/v1/course-selector/search`: Find courses matching a query
- `POST /api/v1/course-selector/index`: Index a course
- `GET /api/v1/course-selector/{course_id}`: Get a specific course
- `GET /api/v1/course-selector/courses`: List all indexed courses

### Course Content

- `GET /api/v1/course-content`: List all course content
- `GET /api/v1/course-content/{course_id}`: Get content for a specific course
- `POST /api/v1/course-content`: Add new course content
- `DELETE /api/v1/course-content/{course_id}`: Delete course content
- `POST /api/v1/course-content/import`: Import course content from a file
- `POST /api/v1/course-content/import-sample`: Import sample course content

### FAQ

- `POST /api/v1/faq/search`: Search for FAQ items
- `GET /api/v1/faq`: List all FAQ items
- `POST /api/v1/faq`: Add a new FAQ item
- `PUT /api/v1/faq/{faq_id}`: Update an FAQ item
- `DELETE /api/v1/faq/{faq_id}`: Delete an FAQ item
- `POST /api/v1/faq/import`: Import FAQ items from JSONL file

### Personal Resource

- `POST /api/v1/personal-resource/search`: Search for personal resources
- `GET /api/v1/personal-resource`: List personal resources
- `GET /api/v1/personal-resource/{resource_id}`: Get a specific resource
- `POST /api/v1/personal-resource`: Add a new resource
- `PUT /api/v1/personal-resource/{resource_id}`: Update a resource
- `DELETE /api/v1/personal-resource/{resource_id}`: Delete a resource
- `POST /api/v1/personal-resource/sync`: Sync resources from StudyHub

### Integrity Check

- `POST /api/v1/integrity-check/check`: Check a submission against indexed assignments
- `POST /api/v1/integrity-check/index`: Index a new graded assignment
- `GET /api/v1/integrity-check/assignment/{assignment_id}`: Get assignment details
- `POST /api/v1/integrity-check/bulk-index`: Index multiple assignments in one request

## Initialization Process

StudyIndexer is initialized through the StudyHub `init_db.py` script, which includes:

1. Creating users and courses in StudyHub
2. Syncing course content to StudyIndexer
3. Syncing personal resources to StudyIndexer
4. Syncing graded assignments to StudyIndexer for integrity checking

This ensures that StudyIndexer has all the necessary data to provide accurate search results and integrity checks.

## Data Syncing

Data is kept in sync between StudyHub and StudyIndexer using the following scripts:

- `sync_resources.py`: Sync personal resources from StudyHub to StudyIndexer
- `sync_assignments.py`: Sync graded assignments from StudyHub to StudyIndexer for integrity checking

These scripts can be run independently of the initialization process to update data as needed. 