import json
from datetime import datetime, timedelta
import pytest
from flask_jwt_extended import create_access_token
from app import create_app, db
from config import TestingConfig
from app.models import User

@pytest.fixture
def app():
    app = create_app(config_class=TestingConfig)
    app.config['TESTING'] = True

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

# Fixture for a test client.
@pytest.fixture
def client(app):
    return app.test_client()

### Tests for /auth/register endpoint ###

def test_register_success(client):
    data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "TestPass123!",
        "role": "student",
        "first_name": "Test",
        "last_name": "User"
    }
    response = client.post("/api/v1/auth/register", json=data)
    assert response.status_code == 201, response.get_data(as_text=True)
    resp_json = response.get_json()
    assert resp_json.get("msg") == "User registered successfully"
    assert resp_json.get("user")["username"] == "testuser"
    assert resp_json.get("user")["email"] == "test@example.com"
    assert resp_json.get("user")["role"] == "student"

def test_register_missing_field(client):
    data = {
        "email": "test@example.com",
        "password": "TestPass123!",
        "role": "student"
    }
    response = client.post("/api/v1/auth/register", json=data)
    assert response.status_code == 400
    resp_json = response.get_json()
    assert "Missing required field" in resp_json.get("msg", "")


def test_register_invalid_role(client):
    data = {
        "username": "testuser2",
        "email": "test2@example.com",
        "password": "TestPass123!",
        "role": "invalid_role"
    }
    response = client.post("/api/v1/auth/register", json=data)
    assert response.status_code == 400
    resp_json = response.get_json()
    assert "Invalid role" in resp_json.get("msg", "")

def test_register_duplicate_user(client):
    data = {
        "username": "duplicateuser",
        "email": "dup@example.com",
        "password": "TestPass123!",
        "role": "teacher"
    }
    response1 = client.post("/api/v1/auth/register", json=data)
    assert response1.status_code == 201

    dup_username = {
        "username": "duplicateuser",
        "email": "newemail@example.com",
        "password": "TestPass123!",
        "role": "teacher"
    }
    response2 = client.post("/api/v1/auth/register", json=dup_username)
    assert response2.status_code == 409
    dup_email = {
        "username": "newusername",
        "email": "dup@example.com",
        "password": "TestPass123!",
        "role": "teacher"
    }
    response3 = client.post("/api/v1/auth/register", json=dup_email)
    assert response3.status_code == 409

### Tests for /auth/login endpoint ###

def test_login_success(client):
    reg_data = {
        "username": "loginuser",
        "email": "login@example.com",
        "password": "TestPass123!",
        "role": "student"
    }
    client.post("/api/v1/auth/register", json=reg_data)

    login_data = {"email": "login@example.com", "password": "TestPass123!"}
    response = client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 200
    resp_json = response.get_json()
    assert resp_json.get("success") is True
    assert "access_token" in resp_json.get("data", {})


def test_login_missing_credentials(client):
    login_data = {"email": "login@example.com"}
    response = client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 400


def test_login_invalid_credentials(client):
    reg_data = {
        "username": "loginuser2",
        "email": "login2@example.com",
        "password": "TestPass123!",
        "role": "student"
    }
    client.post("/api/v1/auth/register", json=reg_data)
    login_data = {"email": "login2@example.com", "password": "WrongPassword"}
    response = client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 401


def test_login_inactive_user(client):
    reg_data = {
        "username": "inactiveuser",
        "email": "inactive@example.com",
        "password": "TestPass123!",
        "role": "student"
    }
    client.post("/api/v1/auth/register", json=reg_data)

    user = User.query.filter_by(email="inactive@example.com").first()
    user.is_active = False
    user.save()

    login_data = {"email": "inactive@example.com", "password": "TestPass123!"}
    response = client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 403


### Tests for /auth/verify-token endpoint ###

def test_verify_token_success(client):
    reg_data = {
        "username": "verifyuser",
        "email": "verify@example.com",
        "password": "TestPass123!",
        "role": "student"
    }
    client.post("/api/v1/auth/register", json=reg_data)
    login_data = {"email": "verify@example.com", "password": "TestPass123!"}
    login_resp = client.post("/api/v1/auth/login", json=login_data)
    token = login_resp.get_json()["data"]["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/v1/auth/verify-token", headers=headers)
    assert response.status_code == 200
    resp_json = response.get_json()
    assert "Token is valid" in resp_json.get("msg", "")


def test_verify_token_user_not_found(client):
    token = create_access_token(identity=9999, additional_claims={'role': 'student'})
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/v1/auth/verify-token", headers=headers)
    assert response.status_code == 404

### Tests for /auth/request-password-reset endpoint ###

def test_request_password_reset_success(client, monkeypatch):
    reg_data = {
        "username": "resetuser",
        "email": "reset@example.com",
        "password": "TestPass123!",
        "role": "student"
    }
    client.post("/api/v1/auth/register", json=reg_data)

    def fake_send_reset_email(user_email, reset_token):
        return True
    monkeypatch.setattr("app.api.v1.auth.send_reset_email", fake_send_reset_email)

    data = {"email": "reset@example.com"}
    response = client.post("/api/v1/auth/request-password-reset", json=data)
    assert response.status_code == 200
    resp_json = response.get_json()
    assert "reset token" in resp_json.get("msg", "").lower() or "sent" in resp_json.get("msg", "").lower()


def test_request_password_reset_missing_email(client):
    data = {}
    response = client.post("/api/v1/auth/request-password-reset", json=data)
    assert response.status_code == 400


def test_request_password_reset_nonexistent_email(client):
    data = {"email": "nonexistent@example.com"}
    response = client.post("/api/v1/auth/request-password-reset", json=data)
    assert response.status_code == 200


### Tests for /auth/reset-password endpoint ###

def test_reset_password_success(client):
    reg_data = {
        "username": "resetuser2",
        "email": "reset2@example.com",
        "password": "TestPass123!",
        "role": "student"
    }
    client.post("/api/v1/auth/register", json=reg_data)

    user = User.query.filter_by(email="reset2@example.com").first()
    reset_token = "test-reset-token"
    
    user.reset_token = reset_token

    user.reset_token_expires = datetime.utcnow() + timedelta(hours=1)
    user.save()

    data = {"token": reset_token, "new_password": "NewTestPass123!"}
    response = client.post("/api/v1/auth/reset-password", json=data)
    assert response.status_code == 200
    resp_json = response.get_json()
    assert "reset successfully" in resp_json.get("msg", "").lower()

    login_data = {"email": "reset2@example.com", "password": "NewTestPass123!"}
    login_resp = client.post("/api/v1/auth/login", json=login_data)
    assert login_resp.status_code == 200


def test_reset_password_missing_fields(client):
    data = {}
    response = client.post("/api/v1/auth/reset-password", json=data)
    assert response.status_code == 400


def test_reset_password_invalid_token(client):
    data = {"token": "invalid-token", "new_password": "NewTestPass123!"}
    response = client.post("/api/v1/auth/reset-password", json=data)
    assert response.status_code == 400


def test_reset_password_expired_token(client):

    reg_data = {
        "username": "resetuser3",
        "email": "reset3@example.com",
        "password": "TestPass123!",
        "role": "student"
    }
    client.post("/api/v1/auth/register", json=reg_data)


    user = User.query.filter_by(email="reset3@example.com").first()
    reset_token = "expired-reset-token"
    past_time = datetime.utcnow() - timedelta(hours=2)
    user.reset_token = reset_token
    user.reset_token_expires = past_time
    user.save()

    data = {"token": reset_token, "new_password": "NewTestPass123!"}
    response = client.post("/api/v1/auth/reset-password", json=data)
    assert response.status_code == 400
