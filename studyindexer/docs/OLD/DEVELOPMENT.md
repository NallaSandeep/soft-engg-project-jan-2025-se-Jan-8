# Technical Development Notes

## Issues and Resolutions

### 1. Service Management Challenges

#### Issue: Complex Dependency Checking
The original service management code included complex dependency chains that made service startup and health checks unreliable. Services would fail to start or report incorrect health status.

#### Resolution:
- Simplified service health checking to focus on port availability
- Removed complex prerequisite checks that were causing cascading failures
- Added direct process management for better control
- Created a debug mode for FastAPI to provide immediate console feedback

```python
# Before:
def start_service(service_name):
    if not check_prerequisites(service_name):
        logger.error(f"Prerequisites for {service_name} not met")
        return False
    # Complex starting logic

# After:
def start_service(service_name):
    # Direct starting logic with clear error handling
    ensure_port_available(service_config[service_name]["port"])
    start_cmd = service_config[service_name]["start_cmd"]
    # Simple process management
```

### 2. ChromaDB Search Issues

#### Issue: Query Parameter Construction
ChromaDB was rejecting search queries due to conflicting query parameters. The API would return errors when both `query_texts` and `query_embeddings` were provided, or when filter expressions were malformed.

#### Resolution:
- Updated search method to use only one query method (embedding preferred)
- Fixed filter construction for empty/single-item filters
- Enhanced error reporting to include query parameters for debugging
- Improved handling of optional search parameters

```python
# Before:
query_params = {
    "n_results": n_results,
    "query_texts": [query],
    "query_embeddings": [query_embedding]  # Both provided, causing error
}

# After:
# Determine which query method to use - prefer embeddings if available
if query_embedding is not None:
    # Use embedding search
    query_params["query_embeddings"] = [query_embedding]
elif query and len(query.strip()) > 0:
    # Use text search if no embedding but valid query text
    query_params["query_texts"] = [query]
```

### 3. File Encoding Detection

#### Issue: JSONL Import Failures
The system was failing to import JSONL files with different encodings, particularly files with UTF-16 Byte Order Mark (BOM).

#### Resolution:
- Enhanced file reading to try multiple encodings (UTF-8, UTF-16-LE, UTF-16-BE)
- Added BOM detection to automatically select the correct encoding
- Improved error handling to provide detailed feedback on import failures
- Added robust JSON parsing with line-specific error reporting

```python
# Before:
with open(file_path, 'r') as f:
    for line in f:
        # Process line

# After:
# Try detected encoding first, then fallback to others
if detected_encoding:
    encodings.insert(0, detected_encoding)

for encoding in encodings:
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            file_content = f.read()
        logger.info(f"Successfully read file with encoding: {encoding}")
        break
    except UnicodeDecodeError:
        logger.warning(f"Failed to decode with encoding: {encoding}")
        continue
```

## Architecture Decisions

### 1. Service Separation

We decided to maintain a clear separation between ChromaDB and FastAPI services for better scalability and reliability. Each service is independently managed, allowing for:

- Independent scaling of vector search (ChromaDB) and API (FastAPI)
- Better resource management
- Easier debugging and monitoring
- Future flexibility for deploying services on different machines

### 2. Embedding Strategy

We prioritized using pre-generated embeddings for searching instead of relying on text queries for several reasons:

- Better semantic search quality with controlled embedding generation
- More predictable search results
- Ability to use specialized embedding models in the future
- Compatibility with ChromaDB's query architecture

### 3. Error Handling Philosophy

We implemented a comprehensive error handling approach that focuses on:

- Providing actionable error messages
- Including context (e.g., query parameters) in error responses
- Graceful degradation when possible
- Detailed logging for troubleshooting

## Key Takeaways

1. **Vector Database Considerations**
   - ChromaDB has specific query parameter requirements that must be carefully followed
   - Filter construction is particularly sensitive to empty conditions
   - Understanding the ChromaDB SDK is essential for proper integration

2. **Service Management**
   - Simpler service management logic leads to more reliable operation
   - Direct health checks (port availability) are more reliable than complex logic
   - Clear separation of concerns makes debugging easier
   - Debug modes are essential for rapid troubleshooting

3. **Data Processing**
   - File encoding detection is crucial for reliable data import
   - BOM detection should be implemented for international data
   - Error reporting should include specific line and content information

## Future Technical Considerations

1. **Scalability**
   - Current architecture allows for basic horizontal scaling
   - Consider implementing a load balancer for FastAPI instances
   - Explore ChromaDB clustering for larger vector databases

2. **Security**
   - Implement authentication for API endpoints
   - Add RBAC (Role-Based Access Control) for different user types
   - Consider adding encryption for sensitive data

3. **Monitoring**
   - Add comprehensive logging and metrics collection
   - Implement health dashboards
   - Create alerts for service disruptions

4. **Performance Optimization**
   - Explore different embedding models for better search quality
   - Implement caching for frequent queries
   - Consider batch processing for large import/export operations 