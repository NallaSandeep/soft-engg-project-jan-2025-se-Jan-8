# StudyIndexer Features Documentation

## Overview

StudyIndexer serves as a powerful Retrieval Augmented Generation (RAG) data source for the StudyHub platform. It enables vector-based search and retrieval of various educational resources including course content, personal resources, and provides academic integrity checking capabilities.

## Core Components

### 1. Vector Database Integration

The system uses ChromaDB as the underlying vector database for storing and querying embeddings. This enables:

- Semantic search across all content types
- Accurate matching of queries to relevant content
- Fast retrieval based on similarity rather than exact keyword matches

### 2. Embedding Generation

StudyIndexer uses sentence-transformers to generate high-quality embeddings for all indexed content:

- Model: all-MiniLM-L6-v2 (384 dimensions)
- Text chunking with configurable chunk size and overlap
- Batch processing support for efficient embedding generation

### 3. API Endpoints

StudyIndexer exposes the following API endpoints:

#### Course Selector API
- `/api/v1/course-selector/search`: Identifies courses most relevant to a query
- Filters results based on student's subscribed courses
- Returns matching courses with scores and relevant topics

#### Course Content API
- `/api/v1/course-content/search`: Retrieves specific content chunks matching a query
- Supports filtering by course IDs
- Returns rich content with source information, metadata, and match scores

#### Personal Resource API
- `/api/v1/personal-resource/search`: Searches student-specific resources
- `/api/v1/personal-resource/`: Adds new personal resources
- `/api/v1/personal-resource/{id}`: Retrieves, updates, or deletes a specific resource
- `/api/v1/personal-resource/{id}/files`: Handles file uploads for resources

#### Integrity Check API
- `/api/v1/integrity-check/check`: Checks submissions against graded assignments
- `/api/v1/integrity-check/index`: Indexes a graded assignment
- `/api/v1/integrity-check/bulk-index`: Indexes multiple assignments at once
- `/api/v1/integrity-check/assignment/{id}`: Retrieves a specific indexed assignment

### 4. Synchronization with StudyHub

StudyIndexer integrates with StudyHub through:

- Automatic sync during database initialization
- Dedicated sync scripts for personal resources and graded assignments
- Batch processing for efficient handling of large data sets

## Technical Architecture

### Technology Stack

- **Backend Framework**: FastAPI for high-performance API development
- **Vector Database**: ChromaDB for efficient similarity search
- **Embedding Model**: Sentence-Transformers (all-MiniLM-L6-v2)
- **Development Tools**: Python 3.9+, Uvicorn for ASGI server

### Service Architecture

The system follows a modular service-oriented architecture:

1. **API Layer**: FastAPI endpoints handling requests and responses
2. **Service Layer**: Core business logic for each feature area
3. **Database Layer**: ChromaDB integration through a service abstraction
4. **Embedding Layer**: Vector embedding generation and management

### Data Flow

1. **Content Creation/Updates in StudyHub**: Content is created or updated in the StudyHub platform
2. **Synchronization**: Content is synchronized to StudyIndexer through dedicated scripts
3. **Embedding Generation**: Text content is processed and embedded into vector representations
4. **Storage in ChromaDB**: Embeddings and metadata are stored in ChromaDB collections
5. **Retrieval**: User queries are embedded and matched against stored vectors
6. **Response**: Matching results are returned with relevant metadata and context

## Feature Details

### Personal Resources Management

Personal resources are student-specific materials like notes, assignments, and annotated content. StudyIndexer supports:

- **Vector Search**: Find semantically relevant personal resources based on queries
- **Resource Types**: Support for notes, PDFs, and other document types
- **Metadata Management**: Store and retrieve rich metadata for each resource
- **Permissions**: Respect privacy settings from StudyHub
- **Synchronization**: Two-way sync between StudyHub and StudyIndexer

### Academic Integrity Checking

The integrity checking feature helps identify potential academic integrity violations:

- **Assignment Indexing**: Index graded assignments for future integrity checks
- **Content Matching**: Match submissions against indexed assignments
- **Similarity Detection**: Calculate similarity scores between submissions and assignments
- **Evidence Highlighting**: Identify specific matching segments between text
- **Threshold Configuration**: Configurable similarity thresholds for violation flagging

### Course Content Retrieval

Course content retrieval enables effective learning support:

- **Cross-Course Search**: Search across multiple courses for relevant content
- **Content Chunking**: Retrieve specific chunks of content rather than entire documents
- **Source Tracking**: Maintain source information for content attribution
- **Rich Metadata**: Return structured metadata for improved context

### Course Selection

The course selection feature helps identify the most relevant courses for a query:

- **Relevance Ranking**: Rank courses based on query relevance
- **Topic Matching**: Identify specific topics within courses that match queries
- **User-Specific Filtering**: Filter results based on student-subscribed courses
- **Metadata Enhancement**: Provide additional context like matched topics and weeks

## Sync Tools and Scripts

StudyIndexer includes several tools for synchronization with StudyHub:

### 1. Master Initialization Script

`init_db.py` handles complete database initialization including:
- Course creation and content import
- Personal resource generation
- Synchronization with StudyIndexer for both resources and assignments

### 2. Standalone Sync Scripts

- `sync_resources.py`: Synchronize personal resources with StudyIndexer
- `sync_assignments.py`: Synchronize graded assignments for integrity checking
- `enhanced_personal_resources.py`: Generate rich personal resources and sync them

### 3. Course Import Scripts

- `import_courses.py`: Import course content from JSON files
- Support for handling various resource types (lectures, assignments, questions)

## Usage Examples

### Personal Resource Sync

```bash
# Sync all personal resources
python sync_resources.py

# Sync resources for a specific student
python sync_resources.py --student_id 3

# Export resources to JSON instead of syncing
python sync_resources.py --export resources.json
```

### Graded Assignment Sync

```bash
# Sync all graded assignments
python sync_assignments.py

# Sync assignments for a specific course
python sync_assignments.py --course_id 101

# Export assignments to JSON instead of syncing
python sync_assignments.py --export assignments.json
```

### API Usage

See the `implemented_apis.md` document for detailed API usage examples.

## Conclusion

StudyIndexer provides a powerful RAG backend for the StudyHub platform, enabling semantic search, personal resource management, and academic integrity checking. Its modular architecture and comprehensive API make it a flexible and extensible solution for educational technology applications. 