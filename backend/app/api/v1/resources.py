import os
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from app import db
from app.models.user import User
from app.models.course import Course
from app.models.resource import Resource
from app.utils.auth import teacher_required

resources_bp = Blueprint('resources', __name__)

def allowed_file(filename):
    """Check if the file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_FILE_EXTENSIONS']

def save_file(file):
    """Save uploaded file and return the file path"""
    filename = secure_filename(file.filename)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    unique_filename = f"{timestamp}_{filename}"
    
    # Create upload directory if it doesn't exist
    upload_dir = current_app.config['UPLOAD_FOLDER']
    os.makedirs(upload_dir, exist_ok=True)
    
    file_path = os.path.join(upload_dir, unique_filename)
    file.save(file_path)
    
    return unique_filename

@resources_bp.route('/courses/<int:course_id>/resources', methods=['GET'])
@jwt_required()
def get_resources(course_id):
    """Get all resources for a course"""
    try:
        course = Course.query.get(course_id)
        if not course:
            return jsonify({'error': 'Course not found'}), 404

        current_user = User.query.get(get_jwt_identity())
        if not current_user:
            return jsonify({'error': 'User not found'}), 404

        # Filter resources based on access permissions
        resources = [r for r in course.resources if r.can_access(current_user)]

        return jsonify({
            'resources': [resource.to_dict() for resource in resources]
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@resources_bp.route('/courses/<int:course_id>/resources', methods=['POST'])
@teacher_required
def create_resource(course_id):
    """Create a new resource"""
    try:
        course = Course.query.get(course_id)
        if not course:
            return jsonify({'error': 'Course not found'}), 404

        current_user = User.query.get(get_jwt_identity())
        
        # Check if user can add resources to this course
        if course.instructor_id != current_user.id and current_user.role != 'admin':
            enrollment = course.enrollments.filter_by(
                user_id=current_user.id,
                role='ta',
                status='active'
            ).first()
            if not enrollment:
                return jsonify({'error': 'Not authorized to add resources to this course'}), 403

        data = request.form.to_dict()
        if 'title' not in data:
            return jsonify({'error': 'Title is required'}), 400

        resource = Resource(
            title=data['title'],
            description=data.get('description'),
            type=data.get('type', 'text'),
            content=data.get('content'),
            course_id=course_id,
            created_by_id=current_user.id,
            is_public=data.get('is_public', 'true').lower() == 'true'
        )

        # Handle file upload if present
        if 'file' in request.files:
            file = request.files['file']
            if file and allowed_file(file.filename):
                filename = save_file(file)
                resource.type = 'file'
                resource.file_path = filename
                resource.file_type = file.content_type
                resource.file_size = os.path.getsize(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))

        db.session.add(resource)
        db.session.commit()

        return jsonify({
            'msg': 'Resource created successfully',
            'resource': resource.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@resources_bp.route('/resources/<int:resource_id>', methods=['GET'])
@jwt_required()
def get_resource(resource_id):
    """Get a specific resource"""
    try:
        resource = Resource.query.get(resource_id)
        if not resource:
            return jsonify({'error': 'Resource not found'}), 404

        current_user = User.query.get(get_jwt_identity())
        if not resource.can_access(current_user):
            return jsonify({'error': 'Not authorized to access this resource'}), 403

        return jsonify({'resource': resource.to_dict()}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@resources_bp.route('/resources/<int:resource_id>/download', methods=['GET'])
@jwt_required()
def download_resource(resource_id):
    """Download a resource file"""
    try:
        resource = Resource.query.get(resource_id)
        if not resource or resource.type != 'file':
            return jsonify({'error': 'Resource not found or not a file'}), 404

        current_user = User.query.get(get_jwt_identity())
        if not resource.can_access(current_user):
            return jsonify({'error': 'Not authorized to access this resource'}), 403

        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], resource.file_path)
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404

        return send_file(
            file_path,
            mimetype=resource.file_type,
            as_attachment=True,
            download_name=resource.file_path.split('_', 2)[2]  # Remove timestamp prefix
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@resources_bp.route('/resources/<int:resource_id>', methods=['PUT'])
@jwt_required()
def update_resource(resource_id):
    """Update a resource"""
    try:
        resource = Resource.query.get(resource_id)
        if not resource:
            return jsonify({'error': 'Resource not found'}), 404

        current_user = User.query.get(get_jwt_identity())
        if not resource.can_modify(current_user):
            return jsonify({'error': 'Not authorized to modify this resource'}), 403

        data = request.form.to_dict()
        
        # Update basic fields if provided
        if 'title' in data:
            resource.title = data['title']
        if 'description' in data:
            resource.description = data['description']
        if 'content' in data and resource.type in ['text', 'link']:
            resource.content = data['content']
        if 'is_public' in data:
            resource.is_public = data['is_public'].lower() == 'true'

        # Handle file update if present
        if 'file' in request.files:
            file = request.files['file']
            if file and allowed_file(file.filename):
                # Delete old file if exists
                if resource.file_path:
                    old_file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], resource.file_path)
                    if os.path.exists(old_file_path):
                        os.remove(old_file_path)

                filename = save_file(file)
                resource.type = 'file'
                resource.file_path = filename
                resource.file_type = file.content_type
                resource.file_size = os.path.getsize(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))

        db.session.commit()

        return jsonify({
            'msg': 'Resource updated successfully',
            'resource': resource.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@resources_bp.route('/resources/<int:resource_id>', methods=['DELETE'])
@jwt_required()
def delete_resource(resource_id):
    """Delete a resource"""
    try:
        resource = Resource.query.get(resource_id)
        if not resource:
            return jsonify({'error': 'Resource not found'}), 404

        current_user = User.query.get(get_jwt_identity())
        if not resource.can_modify(current_user):
            return jsonify({'error': 'Not authorized to delete this resource'}), 403

        # Delete file if exists
        if resource.type == 'file' and resource.file_path:
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], resource.file_path)
            if os.path.exists(file_path):
                os.remove(file_path)

        db.session.delete(resource)
        db.session.commit()

        return jsonify({
            'msg': 'Resource deleted successfully',
            'resource_id': resource_id
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@resources_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return {'status': 'ok', 'message': 'Resources API is running'}
