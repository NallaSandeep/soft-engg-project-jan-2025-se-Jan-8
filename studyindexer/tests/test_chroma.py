"""Test suite for ChromaDB service"""
import pytest
from app.services.chroma import ChromaService
import numpy as np

@pytest.fixture
def chroma_service():
    """Fixture for ChromaDB service"""
    service = ChromaService()
    # Clean up any existing test collections
    for collection_name in service.client.list_collections():
        service.client.delete_collection(collection_name)
    return service

def test_collection_management(chroma_service):
    """Test collection creation and management"""
    # Test collection creation
    collection = chroma_service.get_or_create_collection("test_collection")
    assert collection is not None
    assert collection.name == "test_collection"
    
    # Test adding documents
    documents = [
        "This is the first test document",
        "This is the second test document",
        "This is a completely different document"
    ]
    embeddings = np.random.rand(3, 384).tolist()  # Mock embeddings
    metadatas = [
        {"source": "test1", "type": "text"},
        {"source": "test2", "type": "text"},
        {"source": "test3", "type": "text"}
    ]
    ids = ["1", "2", "3"]
    
    chroma_service.add_documents(
        collection_name="test_collection",
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids
    )
    
    # Test search functionality
    results = chroma_service.search(
        collection_name="test_collection",
        query_embeddings=[np.random.rand(384).tolist()],
        n_results=2
    )
    assert len(results['ids'][0]) == 2
    
    # Test filtering
    results = chroma_service.search(
        collection_name="test_collection",
        query_embeddings=[np.random.rand(384).tolist()],
        n_results=2,
        where={"source": "test1"}
    )
    assert len(results['ids'][0]) == 1
    
    # Test document deletion
    chroma_service.delete_documents(
        collection_name="test_collection",
        ids=["1"]
    )
    results = chroma_service.search(
        collection_name="test_collection",
        query_embeddings=[np.random.rand(384).tolist()],
        n_results=3
    )
    assert len(results['ids'][0]) == 2
    
    # Test collection statistics
    stats = chroma_service.get_collection_stats("test_collection")
    assert stats["document_count"] == 2
    
    # Test listing collections
    collections = chroma_service.list_collections()
    assert len(collections) == 1
    assert collections[0]["name"] == "test_collection" 