# API Usage Guide

This document provides examples of how to use the Study Indexer API to search for and manage FAQ content.

## Base URL

All API endpoints are available at:
```
http://127.0.0.1:8081/api/v1
```

## Authentication

Authentication is not currently implemented but planned for future versions.

## Search FAQs

### Endpoint
```
POST /faq/search
```

### Request Format

```json
{
  "query": "string",
  "limit": integer,
  "min_score": float,
  "tags": ["string"],
  "topic": "string",
  "source": "string"
}
```

#### Parameters:

- `query`: The search query text
- `limit`: Maximum number of results to return (default: 10)
- `min_score`: Minimum similarity score (0-1) for results (default: 0.3)
- `tags`: Optional list of tags to filter by
- `topic`: Optional topic to filter by
- `source`: Optional source to filter by

### Examples

#### Basic Search

```bash
curl -X 'POST' \
  'http://127.0.0.1:8081/api/v1/faq/search' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "query": "credit requirements for diploma",
  "limit": 10,
  "min_score": 0.3
}'
```

#### Search with Filters

```bash
curl -X 'POST' \
  'http://127.0.0.1:8081/api/v1/faq/search' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "query": "internship requirements",
  "limit": 5,
  "min_score": 0.5,
  "tags": ["internship", "graduation"],
  "topic": "Student Handbook"
}'
```

### Response Format

```json
{
  "count": integer,
  "results": [
    {
      "id": "string",
      "topic": "string",
      "question": "string",
      "answer": "string",
      "tags": ["string"],
      "score": float,
      "source": "string",
      "last_updated": "timestamp"
    }
  ],
  "query_time_ms": float
}
```

## Import FAQs

### Endpoint
```
POST /faq/import
```

### Request Format

Multipart form data with:
- `file`: JSONL file with FAQ items
- `source`: Optional source identifier

### JSONL Format

Each line in the JSONL file should be a valid JSON object with:

```json
{
  "topic": "string",
  "question": "string",
  "answer": "string",
  "tags": ["string"],
  "source": "string"
}
```

### Example

```bash
curl -X 'POST' \
  'http://127.0.0.1:8081/api/v1/faq/import' \
  -H 'accept: application/json' \
  -F 'file=@faq_data.jsonl' \
  -F 'source=Student Handbook'
```

### Response Format

```json
{
  "imported": integer,
  "failed": [
    {
      "line": integer,
      "content": "string",
      "error": "string"
    }
  ]
}
```

## Get FAQ by ID

### Endpoint
```
GET /faq/{id}
```

### Example

```bash
curl -X 'GET' \
  'http://127.0.0.1:8081/api/v1/faq/faq_12345abcde' \
  -H 'accept: application/json'
```

### Response Format

```json
{
  "id": "string",
  "topic": "string",
  "question": "string",
  "answer": "string",
  "tags": ["string"],
  "source": "string",
  "is_published": boolean,
  "priority": integer,
  "created_by": "string",
  "last_updated": "timestamp"
}
```

## Update FAQ

### Endpoint
```
PUT /faq/{id}
```

### Request Format

```json
{
  "topic": "string",
  "question": "string",
  "answer": "string",
  "tags": ["string"],
  "source": "string",
  "is_published": boolean,
  "priority": integer
}
```

### Example

```bash
curl -X 'PUT' \
  'http://127.0.0.1:8081/api/v1/faq/faq_12345abcde' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "answer": "Updated answer with new information.",
  "tags": ["updated", "revised"]
}'
```

### Response Format

```json
{
  "success": boolean,
  "message": "string"
}
```

## Delete FAQ

### Endpoint
```
DELETE /faq/{id}
```

### Example

```bash
curl -X 'DELETE' \
  'http://127.0.0.1:8081/api/v1/faq/faq_12345abcde' \
  -H 'accept: application/json'
```

### Response Format

```json
{
  "success": boolean,
  "message": "string"
}
```

## Common Issues and Solutions

### Search returns "ChromaDB query failed" error

This often occurs when:
1. Empty filter values are provided (e.g., empty tags)
2. Filters are malformed

**Solution**: Ensure all filter values are non-empty or omit them entirely.

```bash
# Incorrect (empty tag)
curl -X 'POST' \
  'http://127.0.0.1:8081/api/v1/faq/search' \
  -d '{
  "query": "credit requirements",
  "tags": [""]
}'

# Correct (omit tags completely)
curl -X 'POST' \
  'http://127.0.0.1:8081/api/v1/faq/search' \
  -d '{
  "query": "credit requirements"
}'
```

### JSONL import fails

This can happen due to:
1. File encoding issues
2. Malformed JSON data
3. Missing required fields

**Solution**: 
- Ensure JSONL is properly formatted with one JSON object per line
- Check that each object contains required fields (topic, question, answer)
- Try saving the file with UTF-8 encoding

### No results returned from search

This can occur when:
1. The minimum score is too high
2. The query doesn't match any content
3. Filters are too restrictive

**Solution**:
- Lower the `min_score` value
- Use more general search terms
- Remove or broaden filters 