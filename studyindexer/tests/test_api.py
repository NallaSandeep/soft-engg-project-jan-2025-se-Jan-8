import pytest
import json
import sys
import requests
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from app import app
from fastapi.testclient import TestClient
import os

client = TestClient(app)

# Test data paths
TEST_DATA_DIR = Path(__file__).parent / "test_data"
JAVA_DOC_PATH = TEST_DATA_DIR / "Java.txt"
SQL_DOC_PATH = TEST_DATA_DIR / "SQL.txt"

# Test document IDs
JAVA_DOC_ID = None  # Will be set after upload
SQL_DOC_ID = None   # Will be set after upload

# Test authentication token
TEST_AUTH_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc0MjQ0MDY2NSwianRpIjoiMzkzMzBmY2EtMDhjYi00MjU4LWFlMzgtZTE0M2ZmZGI5ZDVmIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6IjEiLCJuYmYiOjE3NDI0NDA2NjUsImNzcmYiOiJkNDA0MGY0Zi0wZDQwLTRiNDgtOWI0Ny0wNDE1N2Y2MTFiOWMiLCJleHAiOjE3NDI1MjcwNjUsInJvbGUiOiJhZG1pbiJ9.1a8R-nEB6CKm9Jn9WG_-Gc-on5ksz2tGsXLT45bVc6o"

@pytest.fixture(autouse=True)
def setup_test_environment():
    """Setup test environment before each test"""
    # Verify test files exist
    assert JAVA_DOC_PATH.exists(), f"Java document not found at {JAVA_DOC_PATH}"
    assert SQL_DOC_PATH.exists(), f"SQL document not found at {SQL_DOC_PATH}"
    
    yield
    
    # No cleanup needed since we want to keep the test files

def test_health_check():
    """Test Case 1: Health check endpoint"""
    response = client.get("/api/health", headers={"Authorization": f"Bearer {TEST_AUTH_TOKEN}"})
    assert response.status_code == 200
    data = response.json()
    
    # Log the actual response for documentation
    print(f"\nHealth Check Response:\n{json.dumps(data, indent=2)}")
    
    # Basic validation
    assert "status" in data
    assert "environment" in data
    assert "version" in data

def test_chroma_heartbeat():
    """Test Case 2: ChromaDB heartbeat endpoint"""
    # Use requests directly to check ChromaDB health
    response = requests.get("http://127.0.0.1:8000/api/v2/heartbeat", timeout=10)
    assert response.status_code == 200
    data = response.json()
    
    # Log the actual response for documentation
    print(f"\nChromaDB Heartbeat Response:\n{json.dumps(data, indent=2)}")
    
    # Basic validation
    assert "status" in data
    assert "timestamp" in data

def test_upload_java_document():
    """Test Case 3: Upload Java document"""
    global JAVA_DOC_ID
    
    # Prepare test data
    files = {
        "file": ("Java.txt", open(JAVA_DOC_PATH, "rb"), "text/plain")
    }
    params = {
        "title": "Java Programming Guide",
        "document_type": "text",
        "tags": "java,programming,guide",
        "collection": "course"
    }
    
    # Make the request
    response = client.post(
        "/api/v1/documents/",
        files=files,
        params=params,
        headers={"Authorization": f"Bearer {TEST_AUTH_TOKEN}"}
    )
    
    # Log the actual response for documentation
    print(f"\nJava Document Upload Response:\n{json.dumps(response.json(), indent=2)}")
    
    # Basic validation
    assert response.status_code in [200, 201]  # Accept both success codes
    data = response.json()
    assert "document_id" in data
    assert "status" in data
    assert "message" in data
    
    # Store document ID for subsequent tests
    JAVA_DOC_ID = data.get("document_id")
    
    # Wait for document to be processed
    import time
    time.sleep(2)  # Give some time for document processing

def test_upload_sql_document():
    """Test Case 4: Upload SQL document"""
    global SQL_DOC_ID
    
    # Prepare test data
    files = {
        "file": ("SQL.txt", open(SQL_DOC_PATH, "rb"), "text/plain")
    }
    params = {
        "title": "SQL Basics Guide",
        "document_type": "text",
        "tags": "sql,database,basics",
        "collection": "course"
    }
    
    # Make the request
    response = client.post(
        "/api/v1/documents/",
        files=files,
        params=params,
        headers={"Authorization": f"Bearer {TEST_AUTH_TOKEN}"}
    )
    
    # Log the actual response for documentation
    print(f"\nSQL Document Upload Response:\n{json.dumps(response.json(), indent=2)}")
    
    # Basic validation
    assert response.status_code in [200, 201]  # Accept both success codes
    data = response.json()
    assert "document_id" in data
    assert "status" in data
    assert "message" in data
    
    # Store document ID for subsequent tests
    SQL_DOC_ID = data.get("document_id")
    
    # Wait for document to be processed
    import time
    time.sleep(2)  # Give some time for document processing

def test_get_java_document():
    """Test Case 5: Get Java document"""
    if not JAVA_DOC_ID:
        pytest.skip("Java document ID not available - upload test must have failed")
    
    response = client.get(
        f"/api/v1/documents/{JAVA_DOC_ID}",
        headers={"Authorization": f"Bearer {TEST_AUTH_TOKEN}"}
    )
    
    # Log the actual response for documentation
    print(f"\nGet Java Document Response:\n{json.dumps(response.json(), indent=2)}")
    
    # Basic validation
    assert response.status_code == 200
    data = response.json()
    assert "document_id" in data
    assert "status" in data
    assert "metadata" in data
    assert "title" in data["metadata"]
    assert data["metadata"]["title"] == "Java Programming Guide"

def test_get_sql_document():
    """Test Case 6: Get SQL document"""
    if not SQL_DOC_ID:
        pytest.skip("SQL document ID not available - upload test must have failed")
    
    response = client.get(
        f"/api/v1/documents/{SQL_DOC_ID}",
        headers={"Authorization": f"Bearer {TEST_AUTH_TOKEN}"}
    )
    
    # Log the actual response for documentation
    print(f"\nGet SQL Document Response:\n{json.dumps(response.json(), indent=2)}")
    
    # Basic validation
    assert response.status_code == 200
    data = response.json()
    assert "document_id" in data
    assert "status" in data
    assert "metadata" in data
    assert "title" in data["metadata"]
    assert data["metadata"]["title"] == "SQL Basics Guide"

def test_list_my_documents():
    """Test Case 7: List my documents endpoint"""
    response = client.get(
        "/api/v1/documents/my",
        headers={"Authorization": f"Bearer {TEST_AUTH_TOKEN}"}
    )
    
    # Log the actual response for documentation
    print(f"\nList My Documents Response:\n{json.dumps(response.json(), indent=2)}")
    
    # Basic validation
    assert response.status_code == 200
    data = response.json()
    assert "documents" in data
    assert "total" in data
    assert isinstance(data["documents"], list)
    assert isinstance(data["total"], int)
    assert data["total"] >= 2  # Should have at least our two uploaded documents

def test_semantic_search_java():
    """Test Case 8: Semantic search for Java content"""
    search_query = {
        "text": "What is Java programming language and its features?",  # Longer query to meet min_length requirement
        "page": 1,
        "page_size": 10,
        "filters": {
            "tags": "java"
        },
        "collection": "course",
        "min_score": 0.5
    }
    
    response = client.post(
        "/api/v1/search/",
        json=search_query,
        headers={"Authorization": f"Bearer {TEST_AUTH_TOKEN}"}
    )
    
    # Log the actual response for documentation
    print(f"\nJava Semantic Search Response:\n{json.dumps(response.json(), indent=2)}")
    
    # Basic validation
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert "pagination" in data
    assert "query_time_ms" in data
    assert "collection" in data
    assert isinstance(data["results"], list)
    assert isinstance(data["pagination"]["total_results"], int)
    assert data["collection"] == "course"
    
    # Validate pagination
    pagination = data["pagination"]
    assert pagination["current_page"] >= 1
    assert 1 <= pagination["page_size"] <= 50
    assert pagination["total_pages"] >= 0
    assert pagination["total_results"] >= 0
    assert isinstance(pagination["has_next"], bool)
    assert isinstance(pagination["has_previous"], bool)

def test_semantic_search_sql():
    """Test Case 9: Semantic search for SQL content"""
    search_query = {
        "text": "What are the basic SQL commands and their usage?",  # Longer query to meet min_length requirement
        "page": 1,
        "page_size": 10,
        "filters": {
            "tags": "sql"
        },
        "collection": "course",
        "min_score": 0.5
    }
    
    response = client.post(
        "/api/v1/search/",
        json=search_query,
        headers={"Authorization": f"Bearer {TEST_AUTH_TOKEN}"}
    )
    
    # Log the actual response for documentation
    print(f"\nSQL Semantic Search Response:\n{json.dumps(response.json(), indent=2)}")
    
    # Basic validation
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert "pagination" in data
    assert "query_time_ms" in data
    assert "collection" in data
    assert isinstance(data["results"], list)
    assert isinstance(data["pagination"]["total_results"], int)
    assert data["collection"] == "course"
    
    # Validate pagination
    pagination = data["pagination"]
    assert pagination["current_page"] >= 1
    assert 1 <= pagination["page_size"] <= 50
    assert pagination["total_pages"] >= 0
    assert pagination["total_results"] >= 0
    assert isinstance(pagination["has_next"], bool)
    assert isinstance(pagination["has_previous"], bool)

def test_find_similar_documents():
    """Test Case 10: Find similar documents"""
    if not JAVA_DOC_ID:
        pytest.skip("Java document not uploaded")
        
    response = client.get(
        f"/api/v1/search/similar/{JAVA_DOC_ID}",
        params={
            "limit": 5,
            "min_score": 0.5
        },
        headers={"Authorization": f"Bearer {TEST_AUTH_TOKEN}"}
    )
    
    # Log the actual response for documentation
    print(f"\nSimilar Documents Response:\n{json.dumps(response.json(), indent=2)}")
    
    # Basic validation
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert "pagination" in data
    assert "query_time_ms" in data
    assert "collection" in data
    assert isinstance(data["results"], list)
    assert isinstance(data["pagination"]["total_results"], int)
    assert data["collection"] == "course"
    
    # Validate pagination
    pagination = data["pagination"]
    assert pagination["current_page"] == 1
    assert pagination["page_size"] == 5
    assert pagination["total_pages"] == 1
    assert pagination["total_results"] >= 0
    assert not pagination["has_next"]
    assert not pagination["has_previous"]

def test_delete_documents():
    """Test Case 11: Delete uploaded documents"""
    if not JAVA_DOC_ID or not SQL_DOC_ID:
        pytest.skip("Document IDs not available - upload tests must have failed")
    
    # Delete Java document
    response = client.delete(
        f"/api/v1/documents/{JAVA_DOC_ID}",
        headers={"Authorization": f"Bearer {TEST_AUTH_TOKEN}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "success" in data
    assert "message" in data
    
    # Delete SQL document
    response = client.delete(
        f"/api/v1/documents/{SQL_DOC_ID}",
        headers={"Authorization": f"Bearer {TEST_AUTH_TOKEN}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "success" in data
    assert "message" in data 