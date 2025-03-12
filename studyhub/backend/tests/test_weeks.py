import pytest
from flask import json
from app import create_app, db
from app.models import User, Course, Week
from flask_jwt_extended import create_access_token

@pytest.fixture
def client():
    """Setup Flask test client and test database."""
    app = create_app('testing')
    client = app.test_client()
    
    with app.app_context():
        db.create_all()
        yield client
        db.session.remove()
        db.drop_all()

@pytest.fixture
def auth_headers():
    """Create authentication headers for a test admin user."""
    user = User(username="admin", email="admin@example.com", role="admin")
    user.set_password("AdminPass123")
    db.session.add(user)
    db.session.commit()

    token = create_access_token(identity=user.id)
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def sample_course():
    """Create a sample course."""
    course = Course(title="Sample Course")
    db.session.add(course)
    db.session.commit()
    return course

@pytest.fixture
def sample_week(sample_course):
    """Create a sample week for a course."""
    week = Week(course_id=sample_course.id, number=1, title="Week 1")
    db.session.add(week)
    db.session.commit()
    return week

# ---------- GET /courses/{course_id}/weeks ----------
def test_get_course_weeks_valid(client, auth_headers, sample_course, sample_week):
    """Test retrieving weeks for a valid course."""
    response = client.get(f"/courses/{sample_course.id}/weeks", headers=auth_headers)
    assert response.status_code == 200
    assert response.json['success'] is True
    assert len(response.json['data']) == 1

def test_get_course_weeks_not_found(client, auth_headers):
    """Test retrieving weeks for a non-existent course."""
    response = client.get("/courses/999/weeks", headers=auth_headers)
    assert response.status_code == 404

# ---------- POST /courses/{course_id}/weeks ----------
def test_create_week_valid(client, auth_headers, sample_course):
    """Test creating a new week successfully."""
    data = {"number": 2, "title": "Week 2"}
    response = client.post(f"/courses/{sample_course.id}/weeks", json=data, headers=auth_headers)
    assert response.status_code == 201
    assert response.json['success'] is True

def test_create_week_missing_fields(client, auth_headers, sample_course):
    """Test creating a week with missing fields."""
    data = {"title": "Week 3"}  # Missing "number"
    response = client.post(f"/courses/{sample_course.id}/weeks", json=data, headers=auth_headers)
    assert response.status_code == 400

def test_create_week_duplicate_number(client, auth_headers, sample_course, sample_week):
    """Test creating a week with duplicate number."""
    data = {"number": 1, "title": "Duplicate Week"}
    response = client.post(f"/courses/{sample_course.id}/weeks", json=data, headers=auth_headers)
    assert response.status_code == 400

def test_create_week_course_not_found(client, auth_headers):
    """Test creating a week for a non-existent course."""
    data = {"number": 1, "title": "New Week"}
    response = client.post("/courses/999/weeks", json=data, headers=auth_headers)
    assert response.status_code == 404

# ---------- PUT /courses/{course_id}/weeks/{week_id} ----------
def test_update_week_valid(client, auth_headers, sample_course, sample_week):
    """Test updating an existing week successfully."""
    data = {"number": 1, "title": "Updated Week"}
    response = client.put(f"/courses/{sample_course.id}/weeks/{sample_week.id}", json=data, headers=auth_headers)
    assert response.status_code == 200

def test_update_week_missing_fields(client, auth_headers, sample_course, sample_week):
    """Test updating a week with missing fields."""
    data = {"title": "Only Title"}  # Missing "number"
    response = client.put(f"/courses/{sample_course.id}/weeks/{sample_week.id}", json=data, headers=auth_headers)
    assert response.status_code == 400

def test_update_week_duplicate_number(client, auth_headers, sample_course, sample_week):
    """Test updating a week to a duplicate number."""
    new_week = Week(course_id=sample_course.id, number=2, title="Week 2")
    db.session.add(new_week)
    db.session.commit()

    data = {"number": 2, "title": "Duplicate Week"}
    response = client.put(f"/courses/{sample_course.id}/weeks/{sample_week.id}", json=data, headers=auth_headers)
    assert response.status_code == 400

def test_update_week_course_not_found(client, auth_headers, sample_week):
    """Test updating a week in a non-existent course."""
    data = {"number": 1, "title": "Updated Week"}
    response = client.put(f"/courses/999/weeks/{sample_week.id}", json=data, headers=auth_headers)
    assert response.status_code == 404

def test_update_week_not_belonging(client, auth_headers, sample_course, sample_week):
    """Test updating a week that does not belong to the given course."""
    another_course = Course(title="Another Course")
    db.session.add(another_course)
    db.session.commit()

    data = {"number": 1, "title": "Updated Week"}
    response = client.put(f"/courses/{another_course.id}/weeks/{sample_week.id}", json=data, headers=auth_headers)
    assert response.status_code == 404

