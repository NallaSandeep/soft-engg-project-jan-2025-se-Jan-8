import pytest
from flask import json
from app import create_app, db
from app.models import User
from flask_jwt_extended import create_access_token

@pytest.fixture
def client():
    app = create_app("testing")
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

@pytest.fixture
def test_user():
    user = User(username="testuser", email="test@example.com", password="password123", role="student", is_active=True)
    user.save()
    return user

@pytest.fixture
def access_token(test_user):
    return create_access_token(identity=str(test_user.id), additional_claims={"role": test_user.role})

# Test Registration

def test_register_success(client):
    data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "SecurePass123",
        "role": "student"
    }
    response = client.post("/auth/register", data=json.dumps(data), content_type="application/json")
    assert response.status_code == 201
    assert response.json["msg"] == "User registered successfully"
    assert "id" in response.json["user"]


def test_register_missing_fields(client):
    data = {"username": "user1", "email": "user1@example.com"}  # Missing password & role
    response = client.post("/auth/register", data=json.dumps(data), content_type="application/json")
    assert response.status_code == 400
    assert "Missing required field" in response.json["msg"]


def test_register_invalid_role(client):
    data = {
        "username": "user2",
        "email": "user2@example.com",
        "password": "Password!1",
        "role": "invalid_role"
    }
    response = client.post("/auth/register", data=json.dumps(data), content_type="application/json")
    assert response.status_code == 400
    assert "Invalid role" in response.json["msg"]


def test_register_duplicate_user(client, test_user):
    data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "NewPass123",
        "role": "student"
    }
    response = client.post("/auth/register", data=json.dumps(data), content_type="application/json")
    assert response.status_code == 409
    assert "Username already exists" in response.json["msg"]


# Test Login

def test_login_success(client, test_user):
    data = {"email": "test@example.com", "password": "password123"}
    response = client.post("/auth/login", data=json.dumps(data), content_type="application/json")
    assert response.status_code == 200
    assert "access_token" in response.json["data"]


def test_login_invalid_credentials(client):
    data = {"email": "wrong@example.com", "password": "WrongPass123"}
    response = client.post("/auth/login", data=json.dumps(data), content_type="application/json")
    assert response.status_code == 401
    assert "Invalid email or password" in response.json["message"]


def test_login_inactive_user(client, test_user):
    test_user.is_active = False
    test_user.save()
    data = {"email": "test@example.com", "password": "password123"}
    response = client.post("/auth/login", data=json.dumps(data), content_type="application/json")
    assert response.status_code == 403
    assert "Account is deactivated" in response.json["message"]


# Test Verify Token

def test_verify_token_success(client, access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.get("/auth/verify-token", headers=headers)
    assert response.status_code == 200
    assert response.json["msg"] == "Token is valid"


def test_verify_token_invalid(client):
    headers = {"Authorization": "Bearer invalidtoken"}
    response = client.get("/auth/verify-token", headers=headers)
    assert response.status_code == 500


# Test Request Password Reset

def test_request_password_reset_success(client, test_user):
    data = {"email": "test@example.com"}
    response = client.post("/auth/request-password-reset", data=json.dumps(data), content_type="application/json")
    assert response.status_code == 200


def test_request_password_reset_invalid_email(client):
    data = {"email": "notexists@example.com"}
    response = client.post("/auth/request-password-reset", data=json.dumps(data), content_type="application/json")
    assert response.status_code == 200  # Should not indicate user existence


def test_request_password_reset_missing_email(client):
    data = {}
    response = client.post("/auth/request-password-reset", data=json.dumps(data), content_type="application/json")
    assert response.status_code == 400
    assert "Email is required" in response.json["msg"]


# Test Reset Password

def test_reset_password_success(client, test_user):
    test_user.reset_token = "validtoken"
    test_user.save()
    data = {"token": "validtoken", "new_password": "NewPass123!"}
    response = client.post("/auth/reset-password", data=json.dumps(data), content_type="application/json")
    assert response.status_code == 200
    assert "Password has been reset successfully" in response.json["msg"]


def test_reset_password_invalid_token(client):
    data = {"token": "invalidtoken", "new_password": "NewPass123!"}
    response = client.post("/auth/reset-password", data=json.dumps(data), content_type="application/json")
    assert response.status_code == 400
    assert "Invalid or expired reset token" in response.json["msg"]
