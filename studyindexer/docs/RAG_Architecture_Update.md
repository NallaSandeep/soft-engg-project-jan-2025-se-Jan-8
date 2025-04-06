# Retrieval-Augmented Generation (RAG) Architecture Update

## Overview
This document captures the upcoming improvements and finalized decisions for our RAG pipeline, specifically focusing on how we handle ingestion of course data, store additional metadata (e.g., acronyms, synonyms), and perform expansions or normalizations at query time. The ultimate goal is to enhance the user's search experience in StudyIndexer while keeping the architecture flexible and maintainable.

---

## Current Architecture Recap
1. JSON Files per Course (e.g., @sample.json, @ba_updated.json)  
   • Each course is represented in a single JSON, containing fields like course info, weeks, lectures, assignments, sometimes questions.  
   • Potentially includes extraneous or legacy fields (e.g., "assessment_methods," "delivery_mode") that are not currently used.

2. StudyHub (Flask/SQLAlchemy)  
   • "import_courses.py" reads these JSON files and writes them into the relational DB (Course, Week, Lecture, Assignment, etc.).  
   • "init_db.py" is also involved in database setup.

3. StudyIndexer (FastAPI + ChromaDB)  
   • Receives data from StudyHub through a "/course-content" POST endpoint.  
   • Chunkifies the text, creates embeddings, and stores them in ChromaDB for retrieval by AiChat or other clients.

4. Retrieval  
   • User queries are sent to StudyIndexer's "/search" endpoint.  
   • Matching is done primarily via vector embeddings on chunked text, with possible minimal lexical filters.

---

## Improvements and Decisions

### 1. Additional Metadata in JSON
- We will add "acronyms" and "synonyms" fields to the course section of the JSON:
  ```json
  "acronyms": {
    "MAE": "Mean Absolute Error",
    "RAG": "Retrieval Augmented Generation"
  },
  "synonyms": {
    "viz": "visualization",
    "stats": "statistics"
  }
  ```
- Optionally, we will store expanded or specialized "LLM_Summary" for each course/week/lecture.  
- By including these fields in the same JSON, StudyHub and StudyIndexer remain in sync on domain-specific expansions and synonyms.

### 2. Removing and Renaming Unused Fields
- We will review existing JSON fields that are not used at all in the ingestion scripts or the code base (e.g., "assessment_methods," "delivery_mode," "image_url," etc.).  
- Such fields will be removed from future JSON to keep them concise and relevant.

### 3. Case Normalization
- During ingestion, we might transform chunk text to lowercase prior to embedding.  
- We will also lowercase user queries at retrieval time, ensuring no mismatch due to capitalization.  

### 4. Acronym & Synonym Expansion (Retrieval Approach)
- We will preserve chunk text as is (rather than forcibly replacing acronyms in the stored text).  
- When a user query is processed, the "/search" logic will:
  1. Identify any recognized acronyms or synonyms for the course.  
  2. Expand or combine them: e.g., if user typed "MAE," also search "Mean Absolute Error."  
  3. Merge search results and return them, improving recall for domain-specific abbreviations.

### 5. (Optional) Stemming or Lemmatization
- Because embeddings are robust, we plan to do minimal morphological normalization.  
- If chosen, we can apply a consistent method at ingestion and query time:
  1. Ingestion-based: transform chunk text with a simple stemmer, then store and embed.  
  2. Query-based: also stem user's query.  
- This step remains optional depending on ongoing tests with query performance.

### 6. Overlapping Chunks & Keyword Tagging
- We can improve retrieval results by overlapping chunk windows (e.g., chunk_size=500, chunk_overlap=100).  
- We will store "keywords" or short summaries for each lecture chunk to further assist retrieval and weighting.

---

## Proposed JSON Example

Below is an updated structure for the JSON files:

```json
{
  "course": {
    "code": "BA201",
    "title": "Business Analytics",
    "description": "...",
    "acronyms": {
      "MAE": "Mean Absolute Error",
      "RAG": "Retrieval Augmented Generation"
    },
    "synonyms": {
      "viz": "visualization",
      "stats": "statistics"
    },
    "LLM_Summary": {
      "summary": "...",
      "concepts_covered": ["visualization", "distribution fitting"],
      "concepts_not_covered": []
    }
  },
  "weeks": [
    {
      "week_id": 1,
      "order": 1,
      "title": "Week 1: Data Visualization",
      "LLM_Summary": {
        "summary": "Focus on effective data visuals..."
      }
    }
  ],
  "lectures": [
    {
      "lecture_id": 1,
      "week_id": 1,
      "title": "Principles of Effective Data Visualization",
      "content_transcript": "Raw transcript text ...",
      "keywords": ["visualization", "integrity", "purpose"],
      "resource_type": "youtube",
      "video_url": "https://www.youtube.com/..."
    }
  ],
  "assignments": [
    {
      "assignment_id": 3001,
      "week_id": 1,
      "title": "Data Visualization Fundamentals",
      "type": "practice",
      "due_date": "2025-05-10",
      "start_date": "2025-05-03",
      "question_ids": [3001, 3002],
      "is_published": true
    }
  ],
  "questions": [
    {
      "question_id": 3001,
      "content": "Which chart is best for comparing categories?",
      "type": "MCQ",
      "question_options": ["Bar chart", "Line chart", "Pie chart", "Scatter plot"],
      "correct_answer": 0,
      "points": 5,
      "explanation": "Bar charts are for categorical comparisons ..."
    }
  ]
}
```

---

## Overall Workflow

1) JSON is Authored or Updated:
   - We add or remove fields, ensure "acronyms" and "synonyms" are accurate.  

2) "import_courses.py":
   - Reads JSON, inserts/updates the course, weeks, lectures, assignments in the StudyHub DB.
   - Also extracts "acronyms" / "synonyms" to store in the database or attaches them to the final payload for indexing.

3) Sync to StudyIndexer:
   - The script calls "/course-content" with well-structured JSON.  
   - StudyIndexer chunkifies and stores embeddings with any metadata (acronyms, synonyms).  

4) Retrieval:
   - A user enters a query (AiChat or manual).  
   - We optionally normalize case to lowercase.  
   - Expand acronyms/synonyms if found in the metadata.  
   - Conduct vector search in ChromaDB on expanded query.  
   - Merge and rank results, return to the user.

---

## Action Items

1. Remove or rename unused fields in all example JSON files.  
2. Implement "acronyms" and "synonyms" usage in "import_courses.py".  
3. Confirm whether we do overlapping chunks in StudyIndexer (and finalize chunk_size).  
4. Decide if we apply a minimal stemmer or only do lowercase.  
5. Add or refine short summaries or "keywords" for each lecture to boost retrieval.  

---

## Implementation Details & Progress

This section tracks the implementation of the RAG architecture updates, specifically focusing on the integration of `acronyms` and `synonyms` metadata for improved search retrieval.

### Code Analysis Summary

Based on the review of the StudyIndexer codebase, the following components require modification:

1.  **Models (`app/models/course_selector.py`):**
    *   The `CourseInfo` Pydantic model needs to be updated to include optional `acronyms` and `synonyms` dictionary fields. This ensures the API layer correctly validates and accepts the enhanced course data payload from StudyHub.
2.  **Services (`app/services/`):**
    *   **`CourseSelectorService` (`course_selector.py`):**
        *   *Ingestion (`index_course_sync`):* Needs to extract `acronyms` and `synonyms` from the incoming course data and store them in the ChromaDB metadata for the `course-selector` collection. This data might be used later for improving course recommendations.
    *   **`CourseContentService` (`course_content.py`):**
        *   *Ingestion (`add_course_content_sync`, `_extract_content_chunks`):* Must extract `acronyms` and `synonyms` from the course data. Crucially, this metadata must be added to the metadata dictionary of **every chunk** generated from the course content before being stored in ChromaDB. This makes the expansion data readily available during search.
        *   *Search (`search_courses_sync`):* This requires the most significant changes to implement the query-time expansion logic:
            1.  Lowercase the incoming query.
            2.  Perform an initial vector search.
            3.  Extract `acronyms`/`synonyms` from the metadata of the initial results.
            4.  Generate expanded query variations based on the metadata and the original query terms.
            5.  Perform additional vector searches for the expanded queries.
            6.  Merge, deduplicate (based on chunk ID, keeping highest score), and re-rank results from all searches.
            7.  Apply the final limit.
3.  **API Layer (`app/api/`):**
    *   No direct changes anticipated if the Pydantic models are correctly updated.

### Implementation Plan

The following steps will be performed in sequence:

1.  [X] **Update `CourseInfo` Model:** Add `acronyms` and `synonyms` fields to `app/models/course_selector.py`.
2.  [X] **Update `CourseSelectorService` Ingestion:** Modify `index_course_sync` in `app/services/course_selector.py` to store `acronyms`/`synonyms` in metadata.
3.  [X] **Update `CourseContentService` Ingestion:** Modify `add_course_content_sync` and chunking logic in `app/services/course_content.py` to store `acronyms`/`synonyms` in **chunk** metadata.
4.  [X] **Implement Query Expansion:** Rework `search_courses_sync` in `app/services/course_content.py` to perform query lowercasing, metadata extraction, expansion, multi-search, and result merging/ranking.

### Implementation Status

*   **Step 1 (Update `CourseInfo` Model):** Completed
*   **Step 2 (Update `CourseSelectorService` Ingestion):** Completed
*   **Step 3 (Update `CourseContentService` Ingestion):** Completed
*   **Step 4 (Implement Query Expansion):** Completed

---

## Conclusion
This plan solidifies the ingestion pipeline and retrieval expansions. By storing additional metadata (acronyms, synonyms, short summaries) in the JSON, we gain flexible, domain-specific search improvements. Pairing that with optional morphological steps and case normalization will enhance the reliability and user-friendliness of the entire RAG flow. End result: more accurate retrieval with minimal added complexity. 
