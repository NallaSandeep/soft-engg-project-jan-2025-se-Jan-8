# StudyHub Development Standards

> "Consistency is the key to maintainable code. Standards aren't about being right or wrong; they're about the entire team rowing in the same direction." - Michael, Lead Architect

## Table of Contents
1. [Code Style](#code-style)
2. [Database Practices](#database-practices)
3. [API Design](#api-design)
4. [Testing Requirements](#testing-requirements)
5. [Documentation Guidelines](#documentation-guidelines)
6. [Git Workflow](#git-workflow)

## Code Style

### Python Code Style
```python
# Example of our preferred Python style
from typing import Optional, List, Dict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """
    Handles document processing and indexing.
    
    Written by Michael (Feb 2025)
    """
    
    def __init__(self, config: Dict[str, Any]) -> None:
        self.config = config
        self._initialize_components()
    
    def process_document(
        self,
        document_id: str,
        content: bytes,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Process and index a document.
        
        Args:
            document_id: Unique identifier for the document
            content: Raw document content
            metadata: Optional metadata for the document
            
        Returns:
            bool: True if processing successful, False otherwise
            
        Raises:
            ProcessingError: If document processing fails
        """
        try:
            logger.info(f"Processing document: {document_id}")
            # Implementation
            return True
        except Exception as e:
            logger.error(f"Failed to process document {document_id}: {str(e)}")
            raise ProcessingError(f"Processing failed: {str(e)}")
```

### JavaScript/TypeScript Style
```typescript
// Example of our preferred TypeScript style
import { useState, useEffect } from 'react';
import { DocumentService } from '@services/document';
import type { Document } from '@types';

interface DocumentViewerProps {
  documentId: string;
  onUpdate?: (doc: Document) => void;
}

/**
 * Document viewer component with real-time updates.
 * 
 * @author Michael
 * @since February 2025
 */
export const DocumentViewer: React.FC<DocumentViewerProps> = ({
  documentId,
  onUpdate
}) => {
  const [document, setDocument] = useState<Document | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const loadDocument = async () => {
      try {
        const doc = await DocumentService.getDocument(documentId);
        setDocument(doc);
        onUpdate?.(doc);
      } catch (err) {
        setError(err instanceof Error ? err : new Error('Failed to load document'));
      } finally {
        setLoading(false);
      }
    };

    loadDocument();
  }, [documentId]);

  // Component implementation
};
```

## Database Practices

### 1. Schema Management
- **NO** `flask db upgrade` - We use `init_db.py` for consistency
- Schema changes must be documented in `init_db.py`
- Include data migrations in `init_db.py`
- Test data should be meaningful and consistent

### 2. Query Patterns
```python
# Good - Using SQLAlchemy properly
def get_user_documents(user_id: int) -> List[Document]:
    return (
        Document.query
        .filter_by(user_id=user_id)
        .order_by(Document.created_at.desc())
        .limit(100)
        .all()
    )

# Bad - N+1 query problem
def get_user_documents_bad(user_id: int) -> List[Dict]:
    documents = Document.query.filter_by(user_id=user_id).all()
    return [
        {
            **doc.to_dict(),
            'author': User.query.get(doc.user_id)  # N+1 problem!
        }
        for doc in documents
    ]
```

## API Design

### 1. Endpoint Structure
```python
@router.get(
    "/{document_id}",
    response_model=DocumentResponse,
    responses={
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def get_document(
    document_id: str,
    current_user: User = Depends(get_current_user)
) -> DocumentResponse:
    """
    Get document details.
    
    Follows our standard response structure and error handling.
    """
    try:
        document = await document_service.get_document(document_id)
        return DocumentResponse(
            success=True,
            data=document
        )
    except DocumentNotFoundError:
        raise HTTPException(status_code=404, detail="Document not found")
```

### 2. Response Structure
```json
{
    "success": true,
    "data": {
        "id": "doc123",
        "title": "Example Document",
        "created_at": "2025-02-17T10:00:00Z"
    },
    "metadata": {
        "version": "1.0",
        "processing_time": "0.123s"
    }
}
```

## Testing Requirements

### 1. Unit Tests
```python
def test_document_processing():
    """
    Example of our preferred test style.
    
    Written by Michael (Feb 2025)
    """
    # Arrange
    processor = DocumentProcessor(config={'chunk_size': 1000})
    content = b"Test document content"
    
    # Act
    result = processor.process_document(
        document_id="test123",
        content=content
    )
    
    # Assert
    assert result.success
    assert len(result.chunks) > 0
    assert result.metadata['processed_at'] is not None
```

### 2. Integration Tests
```python
@pytest.mark.integration
async def test_document_upload_flow():
    """Test complete document upload and processing flow."""
    # Setup
    client = TestClient(app)
    test_file = create_test_file()
    
    # Execute
    response = await client.post(
        "/api/v1/documents",
        files={"file": test_file}
    )
    
    # Verify
    assert response.status_code == 200
    document_id = response.json()['data']['document_id']
    
    # Wait for processing
    await wait_for_processing(document_id)
    
    # Check final state
    status = await get_document_status(document_id)
    assert status['status'] == 'completed'
```

## Documentation Guidelines

### 1. Code Documentation
- All public APIs must have docstrings
- Include type hints for Python code
- Document exceptions and edge cases
- Add context and rationale for complex logic

### 2. Markdown Standards
- Use proper heading hierarchy
- Include code examples
- Add diagrams for complex flows
- Keep documentation up to date

### 3. Commit Messages
```
feat(studyindexer): add semantic search capability

- Implement vector search using ChromaDB
- Add document chunking logic
- Update API documentation
- Add integration tests

Breaking Changes:
- Search API response structure has changed
- Requires ChromaDB 0.4.0 or higher

Signed-off-by: Michael <michael@studyhub.com>
```

## Git Workflow

### 1. Branch Naming
```
feature/add-semantic-search
bugfix/fix-auth-token-refresh
hotfix/critical-security-patch
release/v1.2.0
```

### 2. Pull Request Template
```markdown
## Description
Brief description of the changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing performed

## Checklist
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] Tests passing
- [ ] PR is ready for review
```

---

*"Standards are like a good map - they help the team navigate together without getting lost." - Michael*

## Version History
- v1.0 (Feb 2025) - Initial standards document
- v1.1 (Feb 2025) - Added code examples and testing requirements
``` 