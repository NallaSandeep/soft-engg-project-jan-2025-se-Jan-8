"""Service layer for personal resources management."""
import os
from datetime import datetime
from typing import Optional, List, Dict, Any
from werkzeug.utils import secure_filename
from app.models import PersonalResource, ResourceFile, User, Course
from app import db
from flask import current_app

class PersonalResourceService:
    """Service for managing personal resources."""

    def __init__(self):
        """Initialize the service."""
        pass

    @property
    def upload_folder(self):
        """Get the upload folder path from current app config."""
        folder = current_app.config['UPLOAD_FOLDER']
        os.makedirs(os.path.join(folder, 'personal_resources'), exist_ok=True)
        return folder

    def get_user_resources(self, user_id: int, course_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get all resources for a user, optionally filtered by course."""
        query = PersonalResource.query.filter_by(user_id=user_id)
        if course_id:
            query = query.filter_by(course_id=course_id)
        return [resource.to_dict() for resource in query.all()]

    def create_resource(self, user_id: int, course_id: int, name: str, 
                       description: Optional[str] = None, settings: Optional[Dict] = None) -> PersonalResource:
        """Create a new personal resource."""
        resource = PersonalResource(
            user_id=user_id,
            course_id=course_id,
            name=name,
            description=description,
            settings=settings or {}
        )
        db.session.add(resource)
        db.session.commit()
        return resource

    def update_resource(self, resource_id: int, user_id: int, 
                       name: Optional[str] = None, description: Optional[str] = None,
                       settings: Optional[Dict] = None) -> PersonalResource:
        """Update an existing personal resource."""
        resource = PersonalResource.query.filter_by(
            id=resource_id,
            user_id=user_id
        ).first_or_404()
        
        if name:
            resource.name = name
        if description is not None:
            resource.description = description
        if settings:
            resource.settings.update(settings)

        db.session.commit()
        return resource

    def delete_resource(self, resource_id: int, user_id: int) -> None:
        """Delete a personal resource and its files."""
        resource = PersonalResource.query.filter_by(
            id=resource_id,
            user_id=user_id
        ).first_or_404()

        # Delete physical files
        for file in resource.files:
            if file.type == 'file' and file.file_path:
                try:
                    os.remove(os.path.join(self.upload_folder, file.file_path))
                except OSError:
                    pass  # Ignore if file doesn't exist
        
        db.session.delete(resource)
        db.session.commit()

    def add_file(self, resource_id: int, user_id: int, file_data: Dict[str, Any]) -> ResourceFile:
        """Add a file to a personal resource."""
        resource = PersonalResource.query.filter_by(
            id=resource_id,
            user_id=user_id
        ).first_or_404()
        
        file = ResourceFile(
            resource_id=resource_id,
            name=file_data.get('name'),
            type=file_data.get('type', 'note'),
            content=file_data.get('content'),
            file_type=file_data.get('file_type', 'text/plain'),
            file_size=file_data.get('file_size', 0)
        )
        
        db.session.add(file)
        db.session.commit()
        return file

    def delete_file(self, resource_id: int, file_id: int, user_id: int) -> None:
        """Delete a file from a personal resource."""
        resource = PersonalResource.query.filter_by(
            id=resource_id,
            user_id=user_id
        ).first_or_404()

        file = ResourceFile.query.filter_by(
            id=file_id,
            resource_id=resource_id
        ).first_or_404()
        
        # Delete physical file if it exists
        if file.type == 'file' and file.file_path:
            try:
                os.remove(os.path.join(self.upload_folder, file.file_path))
            except OSError:
                pass  # Ignore if file doesn't exist
        
        db.session.delete(file)
        db.session.commit()

    def handle_file_upload(self, file, resource_id: int, user_id: int) -> ResourceFile:
        """Handle file upload and storage."""
        resource = PersonalResource.query.filter_by(
            id=resource_id,
            user_id=user_id
        ).first_or_404()
        
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        file_path = os.path.join('personal_resources', unique_filename)
        
        # Save file
        os.makedirs(os.path.join(self.upload_folder, 'personal_resources'), exist_ok=True)
        file.save(os.path.join(self.upload_folder, file_path))
        
        # Create file record
        file_record = ResourceFile(
            resource_id=resource_id,
            name=filename,
            type='file',
            file_path=file_path,
            file_type=file.content_type,
            file_size=os.path.getsize(os.path.join(self.upload_folder, file_path))
        )
        
        db.session.add(file_record)
        db.session.commit()
        return file_record 