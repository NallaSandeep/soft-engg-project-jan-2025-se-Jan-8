# Matched Topics Issue Investigation Report

## Issue Summary

The StudyIndexer service was not properly displaying matched topics in search results from the Course Selector API. When querying courses using the `/api/v1/course-selector/search` endpoint, the `matched_topics` array in the response was consistently empty, despite the data containing relevant topic information.

Example of issue:
```json
{
  "success": true,
  "query": "analytics using sql",
  "total_results": 2,
  "results": [
    {
      "code": "BA201",
      "title": "Business Analytics",
      "description": "A comprehensive course...",
      "score": 0.6335566460699307,
      "matched_topics": []  // <-- Empty array despite relevant topics in data
    }
  ]
}
```

## Investigation Findings

1. **Data Structure Confirmation**
   - The JSON data files (e.g., `sample.json`) correctly include `concepts_covered` within the `LLM_Summary` object:
   ```json
   "LLM_Summary": {
     "summary": "Introduction to computer science principles and programming.",
     "concepts_covered": ["Programming basics", "Problem-solving"],
     "concepts_not_covered": ["Advanced algorithms", "Machine learning"]
   }
   ```

2. **Diagnostic Results**
   - Created a diagnostic tool to directly query ChromaDB
   - Found that the `concepts_covered` field in ChromaDB was either completely missing or empty ("")
   - The structure in ChromaDB showed:
   ```json
   {
     "code": "CS101",
     "concepts_covered": "",  // <-- Empty despite existing in source data
     "course_id": "1",
     "department": "Computer Science",
     "title": "Introduction to Computer Science"
   }
   ```

3. **Import Process Issues**
   - The import process transforms JSON files through multiple steps:
     - `import_json_data` endpoint receives and transforms the JSON data
     - Pydantic validation converts JSON to structured data models
     - Service layer extracts concepts and stores them in ChromaDB
   
   - Multiple potential failure points identified:
     1. Loss during JSON transformation in API layer
     2. Loss during Pydantic validation (CourseContent model)
     3. Concepts not being correctly extracted in `_extract_concepts`
     4. Concepts not being added to metadata for ChromaDB storage

4. **Key Issue Identified**
   - Primary issue: The Pydantic validation process was resetting or emptying the `concepts_covered` array
   - When converting validated models back with `model_dump()`, the concepts were being lost
   - The issue occurs specifically at the boundary between API and service layers

## Solutions Implemented

1. **API Layer Fixes**
   - Added code to preserve concepts during validation:
   ```python
   # Save concepts before validation
   original_concepts = []
   if "course" in data and "LLM_Summary" in data["course"] and "concepts_covered" in data["course"]["LLM_Summary"]:
       original_concepts = data["course"]["LLM_Summary"]["concepts_covered"]
       
   # Validate with Pydantic
   course_content = CourseContent(**data)
   course_dict = course_content.model_dump()
   
   # Restore concepts after validation
   if original_concepts and "course" in course_dict and "LLM_Summary" in course_dict["course"]:
       course_dict["course"]["LLM_Summary"]["concepts_covered"] = original_concepts
   ```

2. **Service Layer Fixes**
   - Enhanced the `_extract_concepts` method to check multiple locations:
   ```python
   # Check for concepts_covered within LLM_Summary
   llm_concepts_covered = llm_summary.get("concepts_covered", [])
   if llm_concepts_covered:
       concepts.update(llm_concepts_covered)
   ```
   
   - Added direct force-insertion of concepts into metadata:
   ```python
   # Force concepts from LLM_Summary into metadata unconditionally
   if direct_concepts:
       logger.info(f"DIRECT FIX: Directly setting concepts_covered in metadata: {direct_concepts}")
       safe_metadata["concepts_covered"] = ",".join([str(c) for c in direct_concepts])
   ```

3. **Logging Enhancements**
   - Added extensive logging at critical points to trace concepts through the system
   - Logs confirm when concepts are extracted, where they're found, and how they're stored

4. **Infrastructure Improvements**
   - Added a `quickstart` command to the service manager:
   ```bash
   python studyindexer/manage_services.py quickstart
   ```
   - This allows faster testing cycles by only restarting FastAPI without ChromaDB

## Current Status

The fixes preserve concepts throughout the entire pipeline but require direct intervention at multiple points due to structural issues in the application:

1. We save concepts before validation and restore them after
2. We directly extract concepts from the LLM_Summary if available
3. We unconditionally force concepts into the metadata for ChromaDB

This should result in proper `matched_topics` in search responses, addressing the original issue.

## Next Steps

1. **Testing**: Perform end-to-end testing with a variety of course files
2. **Monitoring**: Monitor the logs during imports to verify concepts are preserved
3. **Refactoring**: Consider refactoring the Pydantic models to better handle nested data structures
4. **Future Development**:
   - Add a more robust mechanism for topic extraction that doesn't rely on JSON structure
   - Consider schema changes to simplify the concepts representation

## Appendix: Relevant Code Locations

- API Import Endpoint: `studyindexer/app/api/course_selector.py`
- Data Models: `studyindexer/app/models/course_selector.py`
- Service Layer: `studyindexer/app/services/course_selector.py` 