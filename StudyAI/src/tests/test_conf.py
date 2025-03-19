# import pytest
# from fastapi.testclient import TestClient
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy.pool import StaticPool
# from src.database import Base, get_db
# from app import app
# from datetime import datetime, timedelta
# import json

# # Create in-memory SQLite database for testing
# SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
# engine = create_engine(
#     SQLALCHEMY_DATABASE_URL,
#     connect_args={"check_same_thread": False},
#     poolclass=StaticPool,
# )
# TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# # 1. Add error handling for database connection
# @pytest.fixture(scope="function")
# def test_db():
#     try:
#         Base.metadata.create_all(bind=engine)
#         db = TestingSessionLocal()
#         yield db
#     except Exception as e:
#         pytest.fail(f"Database setup failed: {str(e)}")
#     finally:
#         db.close()
#         Base.metadata.drop_all(bind=engine)


# @pytest.fixture(scope="function")
# def client(test_db):
#     # Override the get_db dependency
#     def override_get_db():
#         try:
#             yield test_db
#         finally:
#             test_db.close()

#     app.dependency_overrides[get_db] = override_get_db
#     with TestClient(app) as test_client:
#         yield test_client
#     app.dependency_overrides.clear()


# @pytest.fixture
# def sample_session(client):
#     """Create a sample chat session for testing"""
#     response = client.post("/chat/session")
#     return response.json()


# # 2. Add validation for sample_message fixture
# @pytest.fixture
# def sample_message():
#     """Sample message data for testing"""
#     timestamp = datetime.now(datetime.timezone.utc).isoformat()
#     return {
#         "content": "What is Python?",
#         "metadata": {"source": "user", "timestamp": timestamp},
#     }


# @pytest.fixture
# def admin_user():
#     """Fixture for admin user data"""
#     return {
#         "username": "admin",
#         "email": "admin@example.com",
#         "role": "admin",
#         "is_active": True,
#     }


# @pytest.fixture
# def regular_user():
#     """Fixture for regular user data"""
#     return {
#         "username": "user",
#         "email": "user@example.com",
#         "role": "user",
#         "is_active": True,
#     }


# @pytest.fixture
# def sample_conversation():
#     """Fixture for a multi-turn conversation"""
#     return [
#         {
#             "content": "What is Python?",
#             "metadata": {
#                 "source": "user",
#                 "timestamp": (datetime.utcnow() - timedelta(minutes=5)).isoformat()
#                 + "Z",
#             },
#         },
#         {
#             "content": "Python is a high-level programming language.",
#             "metadata": {
#                 "source": "assistant",
#                 "timestamp": (datetime.utcnow() - timedelta(minutes=4)).isoformat()
#                 + "Z",
#             },
#         },
#     ]


# @pytest.fixture
# def error_cases():
#     """Fixture for testing various error scenarios"""
#     return {
#         "invalid_session": "nonexistent_session_id",
#         "invalid_message": {"content": "", "metadata": {}},
#         "malformed_json": "{'broken': json}",
#         "large_message": {"content": "x" * 10000, "metadata": {}},
#     }


# @pytest.fixture
# def mock_external_service(monkeypatch):
#     """Fixture to mock external service calls"""

#     class MockResponse:
#         def __init__(self, status_code=200, json_data=None):
#             self.status_code = status_code
#             self.json_data = json_data or {}

#         def json(self) -> dict:
#             return self.json_data

#     def mock_get(*args, **kwargs):
#         return MockResponse(200, {"status": "success"})

#     def mock_post(*args, **kwargs):
#         return MockResponse(201, {"id": "mock_id"})

#     # Add monkeypatch for your external service calls here
#     return {"get": mock_get, "post": mock_post}
