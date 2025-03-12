import pytest
import io
from flask import url_for
from app.models import Course, Resource, User
from app import create_app, db
from flask_jwt_extended import create_access_token

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = create_app("testing")  # Ensure your create_app function supports a testing config
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def setup_course_resources(app):
    """Setup test data: create a user, course, and resources."""
    with app.app_context():
        user = User(username="testuser", email="test@example.com", role="teacher")
        user.password = "password"  # Uses password setter (hashing applied)
        db.session.add(user)
        db.session.commit()

        course = Course(code="TEST101", name="Test Course", created_by_id=user.id)
        db.session.add(course)
        db.session.commit()

        resource = Resource(title="Test Resource", type="text", content="Sample Content", course_id=course.id, created_by_id=user.id)
        db.session.add(resource)
        db.session.commit()

        # ✅ Return only IDs to prevent detached instance issues
        return user.id, course.id, resource.id

def get_headers(user_id):
    """Generate headers with a valid JWT token for authentication."""
    return {"Authorization": f"Bearer {create_access_token(identity=user_id)}"}

def test_get_resources(client, setup_course_resources):
    """Test retrieving resources for a course."""
    user_id, course_id, _ = setup_course_resources
    headers = get_headers(user_id)

    response = client.get(f"/courses/{course_id}/resources", headers=headers)

    assert response.status_code == 200
    json_data = response.get_json()
    assert "resources" in json_data
    assert len(json_data["resources"]) > 0
    assert json_data["resources"][0]["title"] == "Test Resource"

def test_get_resources_course_not_found(client, setup_course_resources):
    """Test getting resources for a non-existing course."""
    user_id, _, _ = setup_course_resources
    headers = get_headers(user_id)
    response = client.get("/courses/999/resources", headers=headers)

    assert response.status_code == 404
    assert response.get_json()["error"] == "Course not found"

def test_create_resource(client, setup_course_resources):
    """Test successfully creating a resource."""
    user_id, course_id, _ = setup_course_resources
    headers = get_headers(user_id)

    data = {
        "title": "New Resource",
        "type": "text",
        "content": "Sample Text Content",
        "is_public": True  # Ensure boolean is correctly passed
    }

    response = client.post(f"/courses/{course_id}/resources", headers=headers, json=data)

    assert response.status_code == 201
    json_data = response.get_json()
    assert json_data["msg"] == "Resource created successfully"
    assert json_data["resource"]["title"] == "New Resource"

def test_create_resource_missing_title(client, setup_course_resources):
    """Test creating a resource without a title (should return 400)."""
    user_id, course_id, _ = setup_course_resources
    headers = get_headers(user_id)

    data = {
        "type": "text",
        "content": "Sample Content"
    }

    response = client.post(f"/courses/{course_id}/resources", headers=headers, json=data)

    assert response.status_code == 400
    assert response.get_json()["error"] == "Title is required"

def test_create_resource_unauthorized(client, setup_course_resources):
    """Test that unauthorized users cannot create a resource."""
    _, course_id, _ = setup_course_resources
    headers = {}  # No authentication

    data = {
        "title": "Unauthorized Resource",
        "type": "text",
        "content": "Unauthorized attempt"
    }

    response = client.post(f"/courses/{course_id}/resources", headers=headers, json=data)

    assert response.status_code == 401  # Changed from 403 to 401 (Unauthorized)
    assert "error" in response.get_json()

def test_create_resource_with_file(client, setup_course_resources):
    """Test uploading a file as a resource."""
    user_id, course_id, _ = setup_course_resources
    headers = get_headers(user_id)

    file_data = {
        "title": "File Resource",
        "description": "This is a file test",
        "type": "file",
        "is_public": True,  # Boolean correction
        "file": (io.BytesIO(b"Fake file content"), "testfile.txt")
    }

    response = client.post(f"/courses/{course_id}/resources", headers=headers, data=file_data, content_type='multipart/form-data')

    assert response.status_code == 201
    json_data = response.get_json()
    assert json_data["resource"]["type"] == "file"
    assert "file_path" in json_data["resource"]
