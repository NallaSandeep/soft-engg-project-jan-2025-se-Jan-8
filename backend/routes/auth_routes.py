from flask import Blueprint, request, jsonify, abort
from backend.services import auth_service

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.post('/register')
def register():
    data = request.get_json()
    # Validation
    result = auth_service.register_user(data)
    return jsonify(result), 201

@auth_bp.post('/login')
def login():
    data = request.get_json()
    token_data = auth_service.login_user(data)
    if not token_data:
        abort(401, description="Invalid credentials")
    return jsonify(token_data), 200

@auth_bp.post('/logout')
def logout():
    data = request.get_json()
    result = auth_service.logout_user(data.get("userId"))
    if not result:
        abort(400, description="Logout failed")
    return jsonify({"message": "User logged out successfully"}), 200

