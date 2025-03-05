# StudyIndexer API Explorer

A web-based interface for interacting with the StudyIndexer API endpoints.

## Overview

The StudyIndexer API Explorer provides a user-friendly interface to test and use all available API endpoints in the StudyIndexer system. It allows users to upload documents, search for content, manage document collections, and access administrative functions through an intuitive browser interface.

## Features

- JWT token-based authentication
- Document upload and management
- Text and similarity search
- Tabular views for document lists and search results
- Parent-child document relationship visualization
- Administrative functions (for admin users)

## Access

The API Explorer is automatically available when running the StudyIndexer application at:

```
http://localhost:8000/static/explorer.html
```

## Authentication

To use the API Explorer:

1. Obtain a valid JWT token from the authentication system
2. Enter the token in the JWT Token field on the login screen
3. Click "Login" to authenticate

## Usage Guide

### Document Management

- **Upload Document**: Upload and index new documents
- **List My Documents**: View all documents you've uploaded
- **List Course Documents**: View documents for a specific course
- **Get Document**: View details of a specific document
- **Document Status**: Check processing status of a document
- **Reindex Document**: Reprocess an existing document
- **Delete Document**: Remove a document and its chunks

### Search

- **Search Documents**: Search by text with optional filters
- **Find Similar Documents**: Find documents similar to a reference document

### Admin Functions

- **List All Documents**: View all documents in the system
- **System Stats**: View system statistics and metrics

## Parent-Child Document Relationship

The Explorer clearly shows the relationship between original documents and their chunks:

- Parent documents show the number of chunks they contain
- Chunks show their parent document ID and position
- "View Parent" buttons allow quick navigation from chunks to their parent documents

## Development

The API Explorer is implemented as a single HTML file with embedded JavaScript and CSS:

- Location: `studyindexer/app/static/explorer.html`
- No build process required - edit the HTML file directly
- Changes take effect after restarting the server or refreshing the browser

## Documentation

For more detailed information, see:

- [API Explorer Documentation](../docs/api_explorer.md) - Comprehensive guide
- [API Explorer Status Report](../docs/api_explorer_status.md) - Implementation status

## Troubleshooting

- If authentication fails, ensure your JWT token is valid and not expired
- If API calls fail, check the server logs for more detailed error information
- For CORS issues, ensure you're accessing the Explorer from the same origin as the API 