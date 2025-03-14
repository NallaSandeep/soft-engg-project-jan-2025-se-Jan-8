import pytest
from io import BytesIO
from app import create_app, db
from config import TestingConfig
from app.models import Course, Week, Lecture, User

# -------------------------------
# Fixtures
# -------------------------------

@pytest.fixture
def app():
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
def admin_user(app):
    user = User.query.filter_by(username="admin1").first()
    if not user:
        user = User(
            username="admin1",
            email="admin1@example.com",
            password="TestPass123!",
            role="admin",
            first_name="Admin",
            last_name="User",
            is_active=True
        )
        db.session.add(user)
        db.session.commit()
    return user

@pytest.fixture
def ta_user(app):
    user = User.query.filter_by(username="ta1").first()
    if not user:
        user = User(
            username="ta1",
            email="ta1@example.com",
            password="TestPass123!",
            role="ta",
            first_name="TA",
            last_name="User",
            is_active=True
        )
        db.session.add(user)
        db.session.commit()
    return user

@pytest.fixture
def teacher_user(app):
    user = User.query.filter_by(username="teacher1").first()
    if not user:
        user = User(
            username="teacher1",
            email="teacher1@example.com",
            password="TestPass123!",
            role="teacher",
            first_name="Teacher",
            last_name="User",
            is_active=True
        )
        db.session.add(user)
        db.session.commit()
    return user

# Fixtures to obtain JWT headers by logging in.
@pytest.fixture
def admin_auth_headers(client, admin_user):
    login_data = {"email": admin_user.email, "password": "TestPass123!"}
    response = client.post("/api/v1/auth/login", json=login_data)
    token = response.get_json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def ta_auth_headers(client, ta_user):
    login_data = {"email": ta_user.email, "password": "TestPass123!"}
    response = client.post("/api/v1/auth/login", json=login_data)
    token = response.get_json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def teacher_auth_headers(client, teacher_user):
    login_data = {"email": teacher_user.email, "password": "TestPass123!"}
    response = client.post("/api/v1/auth/login", json=login_data)
    token = response.get_json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}

# Create a sample course. Required non-nullable fields: code, name, description, created_by_id.
@pytest.fixture
def sample_course(app, admin_user):
    course = Course(
        code="CSE101",
        name="Intro to Testing",
        description="A course for testing weeks and lectures.",
        created_by_id=admin_user.id,
        is_active=True
    )
    db.session.add(course)
    db.session.commit()
    return course

# Create a sample week. Required non-nullable fields: course_id, number, title.
@pytest.fixture
def sample_week(app, sample_course):
    week = Week(
        course_id=sample_course.id,
        number=1,
        title="Week 1: Introduction",
        description="Basics of testing",
        is_published=True
    )
    db.session.add(week)
    db.session.commit()
    return week

# Create a sample lecture. Required non-nullable fields: week_id, title, order.
@pytest.fixture
def sample_lecture(app, sample_week):
    lecture = Lecture(
        week_id=sample_week.id,
        title="Lecture 1: Getting Started",
        order=1,
        description="An introduction lecture",
        youtube_url="https://youtu.be/dummy",
        transcript="Dummy transcript",
        is_published=True
    )
    db.session.add(lecture)
    db.session.commit()
    return lecture

#start
# -------------------------------
# GET /courses/{course_id}/weeks Tests
# -------------------------------

def test_get_course_weeks_success(client, admin_auth_headers, sample_course, sample_week, sample_lecture):
    response = client.get(f"/api/v1/courses/{sample_course.id}/weeks", headers=admin_auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data.get("success") is True
    assert "data" in data
    weeks = data["data"]
    # Verify sample_week is present
    assert any(week["title"] == sample_week.title for week in weeks)
    # Check that sample_lecture is included in the week data
    for week in weeks:
        if week["id"] == sample_week.id:
            assert "lectures" in week
            assert any(lec["title"] == sample_lecture.title for lec in week["lectures"])

def test_get_course_weeks_course_not_found(client, admin_auth_headers):
    response = client.get("/api/v1/courses/9999/weeks", headers=admin_auth_headers)
    # Expect 404 if course is not found.
    assert response.status_code == 404

# -------------------------------
# POST /courses/{course_id}/weeks Tests
# -------------------------------

def test_create_week_success(client, ta_auth_headers, sample_course):
    payload = {
        "number": 2,
        "title": "Week 2: Advanced Topics",
        "description": "Deeper dive into testing",
        "is_published": True
    }
    response = client.post(f"/api/v1/courses/{sample_course.id}/weeks", headers=ta_auth_headers, json=payload)
    assert response.status_code == 201
    data = response.get_json()
    assert data.get("success") is True
    week_data = data.get("data")
    assert week_data["number"] == payload["number"]
    assert week_data["title"] == payload["title"]
    assert week_data["description"] == payload["description"]
    assert week_data["is_published"] == payload["is_published"]

def test_create_week_missing_fields(client, ta_auth_headers, sample_course):
    # Missing required fields: 'number' and 'title'
    payload = {
        "description": "Missing required fields"
    }
    response = client.post(f"/api/v1/courses/{sample_course.id}/weeks", headers=ta_auth_headers, json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert data.get("message") == "Missing required fields"

def test_create_week_duplicate_number(client, ta_auth_headers, sample_course, sample_week):
    # Attempt to create a week with a number that already exists in the same course.
    payload = {
        "number": sample_week.number,
        "title": "Duplicate Week",
        "description": "Conflict in week number",
        "is_published": False
    }
    response = client.post(f"/api/v1/courses/{sample_course.id}/weeks", headers=ta_auth_headers, json=payload)
    assert response.status_code == 400
    data = response.get_json()
    expected_msg = f"Week {payload['number']} already exists in this course"
    assert data.get("message") == expected_msg

def test_create_week_course_not_found(client, ta_auth_headers):
    payload = {
        "number": 1,
        "title": "Week for Non-existent Course",
        "description": "Test week creation",
        "is_published": False
    }
    response = client.post("/api/v1/courses/9999/weeks", headers=ta_auth_headers, json=payload)
    assert response.status_code == 404

def test_create_week_unauthorized(client, teacher_auth_headers, sample_course):
    # Teacher role is not authorized to create weeks (only admin and ta have privileges).
    payload = {
        "number": 3,
        "title": "Unauthorized Week",
        "description": "Teacher cannot create weeks",
        "is_published": True
    }
    response = client.post(f"/api/v1/courses/{sample_course.id}/weeks", headers=teacher_auth_headers, json=payload)
    assert response.status_code == 403

# -------------------------------
# PUT /courses/{course_id}/weeks/{week_id} Tests
# -------------------------------

def test_update_week_success(client, ta_auth_headers, sample_course, sample_week):
    payload = {
        "number": 5,  # Changing week number from its original value
        "title": "Updated Week Title",
        "description": "Updated description",
        "is_published": True
    }
    response = client.put(f"/api/v1/courses/{sample_course.id}/weeks/{sample_week.id}", headers=ta_auth_headers, json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data.get("success") is True
    updated_week = data.get("data")
    assert updated_week["number"] == payload["number"]
    assert updated_week["title"] == payload["title"]
    assert updated_week["description"] == payload["description"]
    assert updated_week["is_published"] == payload["is_published"]

def test_update_week_missing_fields(client, ta_auth_headers, sample_course, sample_week):
    payload = {
        # Missing 'number' and 'title'
        "description": "Missing required fields"
    }
    response = client.put(f"/api/v1/courses/{sample_course.id}/weeks/{sample_week.id}", headers=ta_auth_headers, json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert data.get("message") == "Missing required fields"

def test_update_week_not_in_course(client, ta_auth_headers, sample_course, sample_week):
    # Create a new course different from sample_course.
    new_course = Course(
        code="CSE202",
        name="Another Course",
        description="Another test course",
        created_by_id=sample_course.created_by_id,
        is_active=True
    )
    db.session.add(new_course)
    db.session.commit()
    payload = {
        "number": 3,
        "title": "Week Not In Course",
        "description": "Test update",
        "is_published": False
    }
    response = client.put(f"/api/v1/courses/{new_course.id}/weeks/{sample_week.id}", headers=ta_auth_headers, json=payload)
    assert response.status_code == 404
    data = response.get_json()
    assert data.get("message") == "Week does not belong to this course"

def test_update_week_duplicate_number(client, ta_auth_headers, sample_course, sample_week):
    # Create a second week with a distinct number.
    second_week = Week(
        course_id=sample_course.id,
        number=2,
        title="Second Week",
        description="Another week",
        is_published=False
    )
    db.session.add(second_week)
    db.session.commit()
    # Attempt to update sample_week to a number that already exists (number 2).
    payload = {
        "number": 2,
        "title": "Updated Week",
        "description": "Conflict update",
        "is_published": True
    }
    response = client.put(f"/api/v1/courses/{sample_course.id}/weeks/{sample_week.id}", headers=ta_auth_headers, json=payload)
    assert response.status_code == 400
    data = response.get_json()
    expected_msg = f"Week {payload['number']} already exists in this course"
    assert data.get("message") == expected_msg

def test_update_week_course_not_found(client, ta_auth_headers, sample_week):
    payload = {
        "number": 3,
        "title": "Updated Week",
        "description": "Updated description",
        "is_published": True
    }
    response = client.put(f"/api/v1/courses/9999/weeks/{sample_week.id}", headers=ta_auth_headers, json=payload)
    assert response.status_code == 404

def test_update_week_unauthorized(client, teacher_auth_headers, sample_course, sample_week):
    print("Auth Headers:", teacher_auth_headers)
    payload = {
        "number": 4,
        "title": "Unauthorized Update",
        "description": "Teacher should not update",
        "is_published": False
    }
    response = client.put(f"/api/v1/courses/{sample_course.id}/weeks/{sample_week.id}", headers=teacher_auth_headers, json=payload)
    assert response.status_code == 403
