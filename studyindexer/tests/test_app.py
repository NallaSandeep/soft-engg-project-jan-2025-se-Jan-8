"""Test suite for StudyIndexer FastAPI application"""
import pytest
from fastapi.testclient import TestClient
from app import app
from app.core.config import settings

@pytest.fixture
def client():
    """Test client fixture"""
    return TestClient(app)

def test_root_endpoint(client):
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "StudyIndexer"
    assert data["version"] == settings.VERSION
    assert data["status"] == "running"
    assert data["environment"] == settings.ENV

def test_health_check(client):
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == settings.VERSION
    assert data["environment"] == settings.ENV

def test_api_docs_endpoints(client):
    """Test API documentation endpoints"""
    if settings.DEBUG:
        # Swagger UI
        response = client.get(f"{settings.API_V1_STR}/docs")
        assert response.status_code == 200
        # ReDoc
        response = client.get(f"{settings.API_V1_STR}/redoc")
        assert response.status_code == 200
    else:
        # Docs should be disabled in non-debug mode
        response = client.get(f"{settings.API_V1_STR}/docs")
        assert response.status_code == 404
        response = client.get(f"{settings.API_V1_STR}/redoc")
        assert response.status_code == 404

def test_unauthorized_access(client):
    """Test endpoints requiring authentication"""
    endpoints = [
        "/api/v1/documents",
        "/api/v1/search",
        "/api/v1/admin/documents"
    ]
    for endpoint in endpoints:
        response = client.get(endpoint)
        assert response.status_code in {401, 403}  # Unauthorized or Forbidden
        data = response.json()
        assert not data["success"]
        assert "error" in data 