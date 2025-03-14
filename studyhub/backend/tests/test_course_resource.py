import os
import pytest
from io import BytesIO
from app import create_app, db
from config import TestingConfig
from app.models import Course, Resource, User

@pytest.fixture
def app():
    # Create the app using the TestingConfig.
    app = create_app(config_class=TestingConfig)
    app.config['TESTING'] = True
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def teacher_user(app):
    # Create a teacher user.
    user = User(
        username="teacher1",
        email="teacher1@example.com",
        password="TestPass123!",
        role="teacher",
        first_name="Teacher",
        last_name="One",
        is_active=True
    )
    db.session.add(user)
    db.session.commit()
    return user

@pytest.fixture
def student_user(app):
    # Create a student user.
    user = User(
        username="student1",
        email="student1@example.com",
        password="TestPass123!",
        role="student",
        first_name="Student",
        last_name="One",
        is_active=True
    )
    db.session.add(user)
    db.session.commit()
    return user

@pytest.fixture
def teacher_auth_headers(client, teacher_user):
    # Login the teacher user and obtain a JWT token.
    login_data = {"email": teacher_user.email, "password": "TestPass123!"}
    response = client.post("/api/v1/auth/login", json=login_data)
    token = response.get_json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def student_auth_headers(client, student_user):
    # Login the student user.
    login_data = {"email": student_user.email, "password": "TestPass123!"}
    response = client.post("/api/v1/auth/login", json=login_data)
    token = response.get_json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def sample_course(app, teacher_user):
    # Create a sample course (created by the teacher).
    course = Course(
        code="CSE101",
        name="Intro to Computer Science",
        description="A test course",
        created_by_id=teacher_user.id,
        is_active=True
    )
    db.session.add(course)
    db.session.commit()
    return course

@pytest.fixture
def sample_resource(app, sample_course, teacher_user):
    # Create a sample resource associated with the course.
    resource = Resource(
        title="Sample Resource",
        description="Test resource description",
        type="text",
        content="Test content",
        course_id=sample_course.id,
        created_by_id=teacher_user.id,
        is_public=True
    )
    db.session.add(resource)
    db.session.commit()
    return resource

# -------------------------------
# GET /courses/{course_id}/resources Tests
# -------------------------------

def test_get_resources_success(client, teacher_auth_headers, sample_course, sample_resource):
    # Request resources for an existing course.
    response = client.get(f"/api/v1/resources/courses/{sample_course.id}/resources", headers=teacher_auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert "resources" in data
    # Verify that our sample resource is included.
    assert any(r["title"] == sample_resource.title for r in data["resources"])

def test_get_resources_course_not_found(client, teacher_auth_headers):
    # Request resources for a non-existent course.
    response = client.get("/api/v1/resources/courses/9999/resources", headers=teacher_auth_headers)
    assert response.status_code == 404
    data = response.get_json()
    assert data.get("error") == "Course not found"

# -------------------------------
# POST /courses/{course_id}/resources Tests
# -------------------------------

def test_create_resource_success(client, teacher_auth_headers, sample_course, teacher_user):
    data = {
        "title": "New Resource",
        "type": "text", 
        "course_id": sample_course.id, 
        "description": "Resource description",
        "content": "Resource content",
        "is_public": "true"
    }
    response = client.post(f"/api/v1/resources/courses/{sample_course.id}/resources", headers=teacher_auth_headers, data=data)
    
    assert response.status_code == 201
    res_data = response.get_json()

    assert res_data.get("msg") == "Resource created successfully"
    resource = res_data.get("resource")
    
    # Check all non-nullable fields
    assert resource["title"] == "New Resource"
    assert resource["type"] == "text"
    assert resource["course_id"] == sample_course.id



def test_create_resource_missing_title(client, teacher_auth_headers, sample_course, teacher_user):
    # Sending data without a title should yield a 400 error.
    data = {
        "type": "text", 
        "course_id": sample_course.id, 
        "created_by_id": teacher_user.id,
        "description": "Resource description",
        "content": "Resource content",
        "is_public": "true"
    }
    response = client.post(f"/api/v1/resources/courses/{sample_course.id}/resources", headers=teacher_auth_headers, data=data)
    assert response.status_code == 400
    data_resp = response.get_json()
    assert data_resp.get("error") == "Title is required"

def test_create_resource_course_not_found(client, teacher_auth_headers):
    # Attempt to create a resource for a non-existent course.
    data = {
        "title": "New Resource",
        "description": "Resource description",
        "type": "text",
        "content": "Resource content",
        "is_public": "true"
    }
    response = client.post("/api/v1/resources/courses/9999/resources", headers=teacher_auth_headers, data=data)
    assert response.status_code == 404
    data_resp = response.get_json()
    assert data_resp.get("error") == "Course not found"

def test_create_resource_unauthorized(client, student_auth_headers, sample_course):
    # A student (without privileges) should not be allowed to create a resource.
    data = {
        "title": "New Resource",
        "description": "Resource description",
        "type": "text",
        "content": "Resource content",
        "is_public": "true"
    }
    response = client.post(f"/api/v1/resources/courses/{sample_course.id}/resources", headers=student_auth_headers, data=data)
    assert response.status_code == 403
    data_resp = response.get_json()
    print(data_resp)
    assert data_resp.get("success") == False

def test_create_resource_with_file_upload(client, teacher_auth_headers, sample_course):
    # Test resource creation with a file upload using multipart/form-data.
    data = {
        "title": "File Resource",
        "description": "Resource description",
        "type": "file",
        "is_public": "true"
    }
    # Create a dummy file in memory.
    file_data = {
        "file": (BytesIO(b"This is test file content."), "testfile.txt")
    }
    response = client.post(
        f"/api/v1/resources/courses/{sample_course.id}/resources",
        headers=teacher_auth_headers,
        data={**data, **file_data},
        content_type="multipart/form-data"
    )
    assert response.status_code == 201
    res_data = response.get_json()
    assert "Resource created successfully" in res_data.get("msg")
    resource = res_data.get("resource")
    assert resource["title"] == "File Resource"
