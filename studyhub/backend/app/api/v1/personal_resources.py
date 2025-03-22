"""Personal resources API endpoints."""
from flask import Blueprint, request, jsonify, current_app, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import PersonalResource, ResourceFile, Course, CourseEnrollment
from app.services.personal_resource_service import PersonalResourceService
from app import db
from datetime import datetime
import os

bp = Blueprint('personal_resources', __name__, url_prefix='/personal-resources')
resource_service = PersonalResourceService()

@bp.route('/', methods=['GET'])
@jwt_required()
def get_personal_resources():
    """Get all personal resources for the current user."""
    user_id = get_jwt_identity()
    course_id = request.args.get('course_id', type=int)
    
    resources = resource_service.get_user_resources(user_id, course_id)
    return jsonify({
        'success': True,
        'data': resources,
        'message': 'Resources retrieved successfully'
    })

@bp.route('/', methods=['POST'])
@jwt_required()
def create_personal_resource():
    """Create a new personal resource."""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['course_id', 'name']
    for field in required_fields:
        if not data.get(field):
            return jsonify({
                'success': False,
                'message': f'Missing required field: {field}',
                'error': 'Validation error'
            }), 400
        
    enrollment = CourseEnrollment.query.filter_by(
        user_id=user_id,
        course_id=data['course_id'],
        status='active'
    ).first()
    
    if not enrollment:
        return jsonify({
            'success': False,
            'message': 'User is not enrolled in this course',
            'error': 'Permission denied'
        }), 403
    
    resource = resource_service.create_resource(
        user_id=user_id,
        course_id=data['course_id'],
        name=data['name'],
        description=data.get('description'),
        settings=data.get('settings', {})
    )
    
    # Create initial file if provided
    if 'file' in data:
        file_data = data['file']
        resource_service.add_file(resource.id, user_id, file_data)
    
    return jsonify({
        'success': True,
        'data': resource.to_dict(),
        'message': 'Resource created successfully'
    }), 201

@bp.route('/<int:resource_id>', methods=['GET'])
@jwt_required()
def get_personal_resource(resource_id):
    """Get a specific personal resource."""
    user_id = get_jwt_identity()
    resource = PersonalResource.query.filter_by(
        id=resource_id,
        user_id=user_id
    ).first_or_404()
    
    return jsonify(resource.to_dict())

@bp.route('/<int:resource_id>', methods=['PUT'])
@jwt_required()
def update_personal_resource(resource_id):
    """Update a personal resource."""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    resource = resource_service.update_resource(
        resource_id=resource_id,
        user_id=user_id,
        name=data.get('name'),
        description=data.get('description'),
        settings=data.get('settings')
    )
    
    return jsonify(resource.to_dict())

@bp.route('/<int:resource_id>', methods=['DELETE'])
@jwt_required()
def delete_personal_resource(resource_id):
    """Delete a personal resource."""
    user_id = get_jwt_identity()
    resource_service.delete_resource(resource_id, user_id)
    return '', 204

@bp.route('/<int:resource_id>/files', methods=['GET'])
@jwt_required()
def get_resource_files(resource_id):
    """Get all files for a personal resource."""
    user_id = get_jwt_identity()
    resource = PersonalResource.query.filter_by(
        id=resource_id,
        user_id=user_id
    ).first_or_404()
    
    return jsonify([file.to_dict() for file in resource.files])

@bp.route('/<int:resource_id>/files', methods=['POST'])
@jwt_required()
def add_resource_file(resource_id):
    """Add a file to a personal resource."""
    user_id = get_jwt_identity()
    
    if 'file' in request.files:
        file = request.files['file']
        file_record = resource_service.handle_file_upload(file, resource_id, user_id)
    else:
        data = request.get_json()
        file_record = resource_service.add_file(resource_id, user_id, data)
    
    return jsonify(file_record.to_dict()), 201

@bp.route('/<int:resource_id>/files/<int:file_id>', methods=['DELETE'])
@jwt_required()
def delete_resource_file(resource_id, file_id):
    """Delete a file from a personal resource."""
    user_id = get_jwt_identity()
    resource_service.delete_file(resource_id, file_id, user_id)
    return '', 204

@bp.route('/<int:resource_id>/files/<int:file_id>', methods=['PUT'])
@jwt_required()
def update_resource_file(resource_id, file_id):
    """Update a file's content."""
    user_id = get_jwt_identity()
    data = request.get_json()

    # Verify resource ownership
    resource = PersonalResource.query.filter_by(
        id=resource_id,
        user_id=user_id
    ).first_or_404()
    
    # Get the file
    file = ResourceFile.query.filter_by(
        id=file_id,
        resource_id=resource_id
    ).first_or_404()
    
    # Only text files can be updated
    if file.type != 'text':
        return jsonify({
            'success': False,
            'message': 'Only text files can be updated',
            'error': 'Invalid operation'
        }), 400
    
    # Update the file content
    if 'content' in data:
        file.content = data['content']
    if 'name' in data:
        file.name = data['name']
        
    db.session.commit()
    return jsonify(file.to_dict())

@bp.route('/<int:resource_id>/files/<int:file_id>/download', methods=['GET'])
@jwt_required()
def download_resource_file(resource_id, file_id):
    """Download a resource file."""
    user_id = get_jwt_identity()
    
    # Debug logging
    print(f"Download request - Resource ID: {resource_id}, File ID: {file_id}, User ID: {user_id}")
    
    # Verify resource ownership
    resource = PersonalResource.query.filter_by(
        id=resource_id,
        user_id=user_id
    ).first_or_404()
    
    # Get the file
    file = ResourceFile.query.filter_by(
        id=file_id,
        resource_id=resource_id
    ).first_or_404()
    
    # Debug logging
    print(f"File record found - Name: {file.name}, Path: {file.file_path}, Type: {file.file_type}")
    
    if not file.file_path:
        print("Error: No file path available")
        return jsonify({'error': 'No file available'}), 404
        
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], file.file_path)
    
    # Debug logging
    print(f"Full file path: {file_path}")
    print(f"File exists: {os.path.exists(file_path)}")
        
    if not os.path.exists(file_path):
        print("Error: File not found at path")
        return jsonify({'error': 'File not found'}), 404
        
    try:
        return send_file(
            file_path,
            mimetype=file.file_type,
            as_attachment=True,
            download_name=file.name
        )
    except Exception as e:
        print(f"Error sending file: {str(e)}")
        return jsonify({'error': 'Failed to send file'}), 500 