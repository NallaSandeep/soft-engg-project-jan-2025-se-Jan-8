"""Test suite for document processing functionality"""
import pytest
import os
from pathlib import Path
from fastapi import UploadFile
import aiofiles
from app.services.indexer import DocumentIndexer
from app.schemas.documents import DocumentMetadata, DocumentType
from app.core.config import settings

@pytest.fixture
def test_document_path():
    """Fixture for test document path"""
    return Path(__file__).parent / "test_documents" / "sample.txt"

@pytest.fixture
def document_indexer():
    """Fixture for DocumentIndexer instance"""
    indexer = DocumentIndexer()
    # Clean up any existing test data
    if os.path.exists(settings.UPLOAD_DIR):
        for file in os.listdir(settings.UPLOAD_DIR):
            os.remove(os.path.join(settings.UPLOAD_DIR, file))
    if os.path.exists(settings.PROCESSED_DIR):
        for file in os.listdir(settings.PROCESSED_DIR):
            os.remove(os.path.join(settings.PROCESSED_DIR, file))
    return indexer

@pytest.mark.asyncio
async def test_document_preparation(document_indexer, test_document_path):
    """Test document preparation process"""
    # Create a mock UploadFile
    class MockUploadFile:
        async def read(self):
            async with aiofiles.open(test_document_path, 'rb') as f:
                return await f.read()
        
        @property
        def filename(self):
            return "sample.txt"
        
        @property
        def content_type(self):
            return "text/plain"
    
    file = MockUploadFile()
    metadata = DocumentMetadata(
        title="Test Document",
        author="test_user",
        document_type=DocumentType.TEXT,
        tags=["test", "sample"]
    )
    
    # Test document preparation
    document_id = await document_indexer.prepare_document(file, metadata)
    assert document_id is not None
    
    # Verify status file was created
    status = await document_indexer.get_document_status(document_id)
    assert status["status"] == "pending"
    assert "metadata" in status
    assert status["metadata"]["title"] == "Test Document"
    
    # Test document indexing
    await document_indexer.index_document(document_id)
    
    # Verify document was processed
    status = await document_indexer.get_document_status(document_id)
    assert status["status"] == "completed"
    
    # Test search functionality
    results = await document_indexer.search(
        query="machine learning neural networks",
        limit=2,
        collection="course_None"
    )
    assert len(results) > 0
    assert any("neural networks" in result.content.lower() for result in results)
    
    # Test document deletion
    await document_indexer.delete_document(document_id)
    with pytest.raises(Exception):
        await document_indexer.get_document_status(document_id) 