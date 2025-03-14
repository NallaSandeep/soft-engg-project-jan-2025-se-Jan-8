from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from ...models import User
from ... import db
from datetime import timedelta
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST', 'OPTIONS'])
def register():
    """Register a new user."""
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['username', 'email', 'password', 'role']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'msg': f'Missing required field: {field}'}), 400

        # Validate role
        valid_roles = ['student', 'teacher', 'ta']
        if data['role'] not in valid_roles:
            return jsonify({'msg': f'Invalid role. Must be one of: {", ".join(valid_roles)}'}), 400

        # Check if username or email already exists
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'msg': 'Username already exists'}), 409
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'msg': 'Email already exists'}), 409

        # Create new user
        user = User(
            username=data['username'],
            email=data['email'],
            password=data['password'],  # Password will be hashed by the model
            role=data['role'],
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            is_active=True
        )
        user.save()

        return jsonify({
            'msg': 'User registered successfully',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        print(f"Error in registration: {str(e)}")
        return jsonify({'msg': 'Failed to register user'}), 500

@auth_bp.route('/login', methods=['POST', 'OPTIONS'])
def login():
    """Authenticate user and return token."""
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        data = request.get_json()

        # Validate required fields
        if not data.get('email') or not data.get('password'):
            return jsonify({
                'success': False,
                'message': 'Missing email or password',
                'error': 'Missing credentials'
            }), 400

        # Find and verify user
        user = User.query.filter_by(email=data['email']).first()
        if not user or not user.verify_password(data['password']):
            return jsonify({
                'success': False,
                'message': 'Invalid email or password',
                'error': 'Invalid credentials'
            }), 401

        if not user.is_active:
            return jsonify({
                'success': False,
                'message': 'Account is deactivated',
                'error': 'Account inactive'
            }), 403

        # Create access token with string ID
        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={'role': user.role}
        )

        # Update last login
        user.last_login = db.func.now()
        user.save()

        return jsonify({
            'success': True,
            'data': {
                'access_token': access_token,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'role': user.role,
                    'first_name': user.first_name,
                    'last_name': user.last_name
                }
            },
            'message': 'Login successful'
        }), 200

    except Exception as e:
        print(f"Error in login: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Login failed',
            'error': str(e)
        }), 500

@auth_bp.route('/verify-token', methods=['GET', 'OPTIONS'])
@jwt_required()
def verify_token():
    """Verify if the current token is valid."""
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'msg': 'User not found'}), 404
            
        return jsonify({
            'msg': 'Token is valid',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role
            }
        }), 200
        
    except Exception as e:
        print(f"Error verifying token: {str(e)}")
        return jsonify({'msg': 'Token verification failed'}), 500

def send_reset_email(user_email, reset_token):
    """Send password reset email to user."""
    try:
        msg = MIMEMultipart()
        msg['From'] = current_app.config['MAIL_DEFAULT_SENDER']
        msg['To'] = user_email
        msg['Subject'] = 'Password Reset Request'

        body = f"""
        You have requested to reset your password.
        Please use the following token to reset your password:
        
        {reset_token}
        
        This token will expire in 1 hour.
        If you did not request this reset, please ignore this email.
        """
        
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(current_app.config['MAIL_SERVER'], current_app.config['MAIL_PORT'])
        server.starttls()
        server.login(current_app.config['MAIL_USERNAME'], current_app.config['MAIL_PASSWORD'])
        server.send_message(msg)
        server.quit()
        
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False

@auth_bp.route('/request-password-reset', methods=['POST', 'OPTIONS'])
def request_password_reset():
    """Request a password reset token."""
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        data = request.get_json()
        
        if not data or not data.get('email'):
            return jsonify({'msg': 'Email is required'}), 400
            
        user = User.query.filter_by(email=data['email']).first()
        if not user:
            # Return success even if user not found to prevent email enumeration
            return jsonify({'msg': 'If the email exists, a reset token will be sent'}), 200
            
        # Generate reset token
        reset_token = secrets.token_urlsafe(32)
        user.reset_token = reset_token
        user.reset_token_expires = db.func.now() + timedelta(hours=1)
        user.save()
        
        # Send reset email
        if send_reset_email(user.email, reset_token):
            return jsonify({'msg': 'Reset token has been sent to your email'}), 200
        else:   
            return jsonify({'msg': 'Failed to send reset email'}), 500
            
    except Exception as e:
        db.session.rollback()
        print(f"Error in password reset request: {str(e)}")
        return jsonify({'msg': 'Failed to process reset request'}), 500

@auth_bp.route('/reset-password', methods=['POST', 'OPTIONS'])
def reset_password():
    """Reset password using token."""
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        data = request.get_json()
        
        if not data or not data.get('token') or not data.get('new_password'):
            return jsonify({'msg': 'Token and new password are required'}), 400
            
        user = User.query.filter(
            User.reset_token == data['token'],
            User.reset_token_expires > db.func.now()
        ).first()
        if not user:
            return jsonify({'msg': 'Invalid or expired reset token'}), 400
            
        # Update password
        user.password = data['new_password']
        user.reset_token = None
        user.reset_token_expires = None
        user.save()
        
        return jsonify({'msg': 'Password has been reset successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error in password reset: {str(e)}")
        return jsonify({'msg': 'Failed to reset password'}), 500

@auth_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return {'status': 'ok', 'message': 'Auth API is running'}
