# StudyIndexer Rewrite Plan

## 1. Project Overview

The StudyIndexer service needs to be rewritten to fully implement the VectorDB_AI_Layer_Spec.md requirements. This document outlines our approach to rewrite the system while preserving useful components from the existing codebase.

## 2. Requirements Analysis

Based on the VectorDB_AI_Layer_Spec.md, the system requires:

### 2.1 Core Components

- **Four Vector Databases**: Each backed by ChromaDB
  - FAQ Database (static institutional info)
  - Course Guide Database (course topic coverage)
  - Course Content Database (lecture-level content)
  - Personal Resources Database (user-uploaded notes)
  
- **Multi-agent RAG System**: Powered by Gemini LLM

- **Integration Points**:
  - Search APIs for each database
  - Content ingestion APIs for each database
  - Perceptron chat assistant interface

### 2.2 API Requirements

Each vector database requires:
- **Search APIs**: Semantic search with filtering
- **Create APIs**: Content ingestion with metadata

### 2.3 Technical Requirements

- Text embedding using `all-MiniLM-L6-v2`
- Vector storage with ChromaDB
- Metadata-rich search capabilities
- Private/public access controls
- Academic integrity checking system

## 3. Assessment of Existing Codebase

### 3.1 Components to Reuse

- **Configuration**:
  - `.env.example` - Environment variables template
  - `config.py` - Configuration loading and validation
  
- **Core Application**:
  - `main.py` - Application entry point
  - Service bootstrap processes
  
- **Service Management**:
  - `manage_services.py` - Service orchestration
  - `health_monitor.py` - Health checking
  - `setup.py` - Package setup

### 3.2 Components to Rewrite

- **API Layer**:
  - All API endpoints need rewriting to match the spec
  - Need specialized endpoints for each vector database type
  
- **Data Models**:
  - Database schemas need more specialization
  - Robust metadata structures for each database type
  
- **Service Layer**:
  - Enhanced ChromaDB integration
  - Specialized collection management
  - More granular document processing
  
- **Search & Indexing**:
  - Specialized search functionality for each database
  - Integrity checking system
  - RAG integration

## 4. New Architecture

### 4.1 Directory Structure

```
studyindexer/
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
│   │   ├── auth.py
│   │   ├── config.py (reuse)
│   │   ├── errors.py
│   │   ├── logging.py (reuse)
│   │   └── middleware.py (reuse)
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
│   │   ├── chroma.py (rewrite)
│   │   ├── embeddings.py
│   │   ├── indexer.py (rewrite)
│   │   ├── integrity.py (new)
│   │   └── rag.py (new)
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── document.py
│   │   ├── search.py
│   │   └── text.py
│   └── __init__.py
├── data/
│   ├── chroma/
│   ├── processed/
│   └── temp/
├── logs/
├── static/
├── uploads/
├── .env.example (reuse)
├── main.py (reuse)
├── manage_services.py (reuse)
├── health_monitor.py (reuse)
├── setup.py (reuse)
└── start_chromadb.py (reuse)
```

### 4.2 Component Relationships

```
Client Request → FastAPI Router → API Endpoint → Service Layer → ChromaDB Service
                                               → Embedding Service
                                               → RAG Service (Gemini)
                                               → Integrity Service
```

### 4.3 Collection Structure

Each vector database will be implemented as a separate ChromaDB collection:

```
ChromaDB
├── faq_collection
├── course_guide_collection
├── course_content_collection
└── personal_resources_collection (per user)
```

## 5. Implementation Plan

### 5.1 Phase 1: Core Infrastructure

1. Setup project structure
2. Reuse/update core configuration
3. Implement ChromaDB service with specialized collections
4. Implement embedding service
5. Create base models

### 5.2 Phase 2: FAQ Database

1. Create FAQ models
2. Implement FAQ service
3. Create FAQ API endpoints
   - POST /faq/search
   - POST /faq/add

### 5.3 Phase 3: Course Guide Database

1. Create Course Guide models
2. Implement Course Guide service
3. Create Course Guide API endpoints
   - POST /course-guide/search
   - POST /course-guide/add

### 5.4 Phase 4: Course Content Database

1. Create Course Content models
2. Implement Course Content service
3. Create Course Content API endpoints
   - POST /course-content/search
   - POST /course-content/add

### 5.5 Phase 5: Personal Resources Database

1. Create Personal Resources models
2. Implement Personal Resources service
3. Create Personal Resources API endpoints
   - POST /personal-resources/search
   - POST /personal-resources/add

### 5.6 Phase 6: Integrity Check System

1. Create Integrity Check models
2. Implement Integrity Check service
3. Create Integrity Check API endpoints
   - POST /integrity-check/check
   - POST /integrity-check/add

### 5.7 Phase 7: RAG Integration

1. Implement Gemini LLM integration
2. Create RAG service
3. Integrate RAG with search functionality

### 5.8 Phase 8: Testing & Refinement

1. Create comprehensive test suite
2. Performance testing and optimization
3. Refine and improve APIs based on test results

## 6. Comparison with Existing Implementation

| Feature             | Existing Implementation           | New Implementation                   |
|---------------------|-----------------------------------|-------------------------------------|
| Collections         | Generic "general" collection      | Specialized collections for each DB  |
| Metadata            | General purpose                   | Tailored to each vector DB type      |
| API Endpoints       | Mixed implementation              | Specialized for each vector DB       |
| Integrity Checking  | Not implemented                   | Fully implemented as specified       |
| RAG System          | Not implemented                   | Gemini integration                   |
| Search              | Basic filtering                   | Enhanced with vector-specific params |

## 7. Risks and Mitigations

| Risk                                 | Mitigation                                            |
|--------------------------------------|-------------------------------------------------------|
| ChromaDB scaling limitations         | Implement efficient chunking and specialized indexes  |
| Complexity of multiple collections   | Strong separation of concerns and modular design      |
| RAG integration challenges           | Incremental development with thorough testing         |
| Performance degradation with scale   | Regular profiling and optimization                    |
| Data consistency across collections  | Transactional operations and validation               |

## 8. Conclusion

This rewrite will properly implement all requirements in the Vector DB AI Layer specification while maintaining compatibility with the existing infrastructure. By carefully separating concerns and creating specialized components for each vector database type, we will create a more maintainable and extensible system.

## 9. Next Steps

1. Set up project structure
2. Begin Phase 1 implementation with reusable components
3. Schedule regular progress reviews
4. Update this document as implementation details are finalized 