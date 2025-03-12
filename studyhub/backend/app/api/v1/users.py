from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ...models import User
from ...utils.auth import admin_required
from ... import db

users_bp = Blueprint('users', __name__)

@users_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get details of the currently logged-in user."""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'msg': 'User not found'}), 404
            
        return jsonify({
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_active': user.is_active,
                'is_email_verified': user.is_email_verified,
                'last_login': user.last_login.isoformat() if user.last_login else None
            }
        }), 200
        
    except Exception as e:
        print(f"Error getting user details: {str(e)}")
        return jsonify({'msg': 'Failed to get user details'}), 500

@users_bp.route('/me', methods=['PUT'])
@jwt_required()
def update_current_user():
    """Update details of the currently logged-in user."""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'msg': 'User not found'}), 404
            
        data = request.get_json()
        
        # Fields that can be updated
        updatable_fields = ['first_name', 'last_name', 'email']
        
        # Update fields if provided
        for field in updatable_fields:
            if field in data:
                # Check email uniqueness if updating email
                if field == 'email' and data[field] != user.email:
                    existing_user = User.query.filter_by(email=data[field]).first()
                    if existing_user:
                        return jsonify({'msg': 'Email already exists'}), 409
                setattr(user, field, data[field])
        
        # Handle password update separately
        if 'current_password' in data and 'new_password' in data:
            if not user.verify_password(data['current_password']):
                return jsonify({'msg': 'Current password is incorrect'}), 401
            user.password = data['new_password']
        
        user.save()
        
        return jsonify({
            'msg': 'User updated successfully',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'first_name': user.first_name,
                'last_name': user.last_name
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error updating user: {str(e)}")
        return jsonify({'msg': 'Failed to update user'}), 500

@users_bp.route('/', methods=['GET'])
@jwt_required()
def get_users():
    """Get all users."""
    try:
        users = User.query.all()
        return jsonify({
            'success': True,
            'users': [{
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_active': user.is_active,
                'is_email_verified': user.is_email_verified,
                'last_login': user.last_login.isoformat() if user.last_login else None
            } for user in users]
        }), 200
        
    except Exception as e:
        print(f"Error getting users: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get users',
            'message': str(e)
        }), 500

@users_bp.route('/<int:user_id>', methods=['GET'])
@admin_required
def get_user(user_id):
    """Get details of a specific user (admin only)."""
    try:
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'msg': 'User not found'}), 404
            
        return jsonify({
            'success': True,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_active': user.is_active,
                'is_email_verified': user.is_email_verified,
                'last_login': user.last_login.isoformat() if user.last_login else None
            }   
        }), 200
        
    except Exception as e:
        print(f"Error getting user: {str(e)}")
        return jsonify({'msg': 'Failed to get user'}), 500

@users_bp.route('/<int:user_id>/activate', methods=['POST'])
@admin_required
def activate_user(user_id):
    """Activate a user account (admin only)."""
    try:
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'msg': 'User not found'}), 404
            
        user.is_active = True
        user.save()
        
        return jsonify({
            'msg': 'User activated successfully',
            'user_id': user.id
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error activating user: {str(e)}")
        return jsonify({'msg': 'Failed to activate user'}), 500

@users_bp.route('/<int:user_id>/deactivate', methods=['POST'])
@admin_required
def deactivate_user(user_id):
    """Deactivate a user account (admin only)."""
    try:
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'msg': 'User not found'}), 404
            
        # Prevent deactivating the last admin
        if user.role == 'admin' and User.query.filter_by(role='admin', is_active=True).count() <= 1:
            return jsonify({'msg': 'Cannot deactivate the last admin user'}), 403
            
        user.is_active = False
        user.save()
        
        return jsonify({
            'msg': 'User deactivated successfully',
            'user_id': user.id
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error deactivating user: {str(e)}")
        return jsonify({'msg': 'Failed to deactivate user'}), 500

@users_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return {'status': 'ok', 'message': 'Users API is running'}

@users_bp.route('/', methods=['POST'])
@admin_required
def create_user():
    """Create a new user (admin only)."""
    try:
        data = request.get_json()
        
        print(data)
        """{'username': 'testuser42', 'email': 'testuserCreate@studyhub.com', 'password': '1234', 'first_name': 'TestUser1', 'last_name': 'TestLast', 'role': 'student', 'is_active': True}
        2025-02-14 16:41:07,602 - studybot - INFO - Response: {"timestamp": "2025-02-14T11:11:07.602354", "method": "POST", "path": "/api/v1/users", "status_code": 200, "duration_ms": 63.88, "response_size": 24, "content_type": "application/json"}"""

        # Check if all fields are there 
        required_fields = ['username', 'email', 'password', 'role']
        for field in required_fields:
            if field not in data:
                return jsonify({'msg': f'{field} is required'}), 400
        
        # Check email already created or not (hoping only email is unique key, if username is also unique key need to check that also)
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            return jsonify({'msg': 'Email already exists'}), 409

        user = User(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            role=data['role'],
            is_active=data.get('is_active', False)
        )
        user.save()

        return jsonify({
            'success': True,
            'msg': 'User created successfully',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_active': user.is_active,
                'is_email_verified': user.is_email_verified,
                'last_login': user.last_login.isoformat() if user.last_login else None
            }
        }), 201
    except:
        return jsonify({'msg': 'Invalid data'}), 400
