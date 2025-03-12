import pytest
from flask import url_for
from app import create_app, db
from app.models import User, Course, Resource
from werkzeug.security import generate_password_hash
from flask_jwt_extended import create_access_token

@pytest.fixture
def app():
    """Create and configure a new app instance for testing."""
    app = create_app("testing")  # Ensure the "testing" config is used
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """Returns a test client for making HTTP requests."""
    return app.test_client()

@pytest.fixture
def setup_resources(app):
    """Setup test data including users, courses, and resources."""
    with app.app_context():
        db.session.rollback()  # Ensure a clean state before running

        # Create test users
        student = User(
            username="student1",
            email="student1@example.com",
            password_hash=generate_password_hash("password"),
            role="student",
            first_name="John",
            last_name="Doe",
            is_active=True
        )
        admin = User(
            username="admin",
            email="admin@example.com",
            password_hash=generate_password_hash("adminpassword"),
            role="admin",
            first_name="Admin",
            last_name="User",
            is_active=True
        )

        db.session.add_all([student, admin])
        db.session.commit()
        
        # Create a test course (with code and created_by_id)
        course = Course(
            code="CS101",
            name="Test Course",
            description="A sample course",
            created_by_id=admin.id,  # Set the course creator
            is_active=True,
            max_students=100,
            enrollment_type="open"
        )
        
        db.session.add(course)
        db.session.commit()
        from app.models import CourseEnrollment
        # Enroll student in the course
        enrollment = CourseEnrollment(
            course_id=course.id,
            user_id=student.id,
            role="student",
            status="active"
        )

        db.session.add(enrollment)
        db.session.commit()
        # Create a public resource
        public_resource = Resource(
            title="Public PDF",
            type="file",
            file_path="test.pdf",
            file_type="application/pdf",
            file_size=1024,
            course_id=course.id,
            created_by_id=admin.id,
            is_public=True
        )

        # Create a private resource (only enrolled users can access)
        private_resource = Resource(
            title="Private Notes",
            type="text",
            content="Confidential notes",
            course_id=course.id,
            created_by_id=admin.id,
            is_public=False
        )

        db.session.add_all([public_resource, private_resource])
        db.session.commit()
        return {
            "student": student,
            "admin": admin,
            "course": course,
            "enrollment": enrollment,
            "public_resource": public_resource,
            "private_resource": private_resource
        }


@pytest.fixture
def auth_headers(app, setup_resources):
    """Generate JWT tokens for different users."""
    with app.app_context():
        student = setup_resources["student"]
        admin = setup_resources["admin"]

        student_token = create_access_token(identity=student.id)
        admin_token = create_access_token(identity=admin.id)

        return {
            "student": {"Authorization": f"Bearer {student_token}"},
            "admin": {"Authorization": f"Bearer {admin_token}"},
        }

# ✅ Test getting a public resource (should succeed)
def test_get_public_resource(client, auth_headers, setup_resources):
    resource_id = setup_resources["public_resource"].id
    response = client.get(f"/resources/{resource_id}", headers=auth_headers["student"])
    assert response.status_code == 200
    assert response.json["resource"]["title"] == "Public PDF"

# ❌ Test getting a private resource (should fail for unauthenticated user)
def test_get_private_resource_unauthorized(client, setup_resources):
    resource_id = setup_resources["private_resource"].id
    response = client.get(f"/resources/{resource_id}")  # No auth header
    assert response.status_code == 401  # Unauthorized

# ✅ Test getting a private resource (should succeed for admin)
def test_get_private_resource_admin(client, auth_headers, setup_resources):
    resource_id = setup_resources["private_resource"].id
    response = client.get(f"/resources/{resource_id}", headers=auth_headers["admin"])
    assert response.status_code == 200
    assert response.json["resource"]["title"] == "Private Notes"

# ❌ Test modifying a resource as a student (should fail)
def test_update_resource_unauthorized(client, auth_headers, setup_resources):
    resource_id = setup_resources["public_resource"].id
    response = client.put(f"/resources/{resource_id}", headers=auth_headers["student"], json={"title": "Hacked!"})
    assert response.status_code == 403  # Forbidden

# ✅ Test modifying a resource as an admin (should succeed)
def test_update_resource_admin(client, auth_headers, setup_resources):
    resource_id = setup_resources["public_resource"].id
    response = client.put(f"/resources/{resource_id}", headers=auth_headers["admin"], json={"title": "Updated Title"})
    assert response.status_code == 200
    assert response.json["resource"]["title"] == "Updated Title"

# ✅ Test deleting a resource (admin)
def test_delete_resource_admin(client, auth_headers, setup_resources):
    resource_id = setup_resources["private_resource"].id
    response = client.delete(f"/resources/{resource_id}", headers=auth_headers["admin"])
    assert response.status_code == 200
    assert response.json["msg"] == "Resource deleted successfully"

# ❌ Test deleting a resource (student - should fail)
def test_delete_resource_student(client, auth_headers, setup_resources):
    resource_id = setup_resources["public_resource"].id
    response = client.delete(f"/resources/{resource_id}", headers=auth_headers["student"])
    assert response.status_code == 403  # Forbidden

# ✅ Test downloading a file (public resource)
def test_download_public_file(client, auth_headers, setup_resources):
    resource_id = setup_resources["public_resource"].id
    response = client.get(f"/resources/{resource_id}/download", headers=auth_headers["student"])
    assert response.status_code == 200

# ❌ Test downloading a private file (should fail for unauthorized user)
def test_download_private_file_unauthorized(client, setup_resources):
    resource_id = setup_resources["private_resource"].id
    response = client.get(f"/resources/{resource_id}/download")  # No auth header
    assert response.status_code == 401  # Unauthorized

# ✅ Test health check
def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json["status"] == "ok"
