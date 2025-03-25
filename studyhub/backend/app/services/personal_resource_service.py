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
        folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'personal_resources')
        os.makedirs(folder, exist_ok=True)
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

    def handle_file_upload(self, file, resource_id, user_id):
        """Handle file upload for a resource."""
        # Verify resource ownership
        resource = PersonalResource.query.filter_by(
            id=resource_id,
            user_id=user_id
        ).first_or_404()

        # Create the resource directory if it doesn't exist
        resource_dir = os.path.join(self.upload_folder, str(resource_id))
        os.makedirs(resource_dir, exist_ok=True)

        # Save the file
        filename = secure_filename(file.filename)
        # Store only the relative path from the resource directory
        file_path = os.path.join(str(resource_id), filename)
        # Full path for saving the file
        full_path = os.path.join(self.upload_folder, file_path)

        print(f"Saving file to: {full_path}")  # Debug log
        file.save(full_path)

        # Create file record with the relative path
        file_record = ResourceFile(
            resource_id=resource_id,
            name=filename,
            file_path=file_path,  # Store relative path
            file_type='text/plain',
            type='file'
        )
        
        db.session.add(file_record)
        db.session.commit()
        
        print(f"File record created: {file_record.to_dict()}")  # Debug log
        return file_record

    def add_file(self, resource_id, user_id, file_data):
        """Add a text note or file to a resource."""
        # Verify resource ownership
        resource = PersonalResource.query.filter_by(
            id=resource_id,
            user_id=user_id
        ).first_or_404()

        if isinstance(file_data, dict) and 'content' in file_data:
            # Handle text note
            file_record = ResourceFile(
                resource_id=resource_id,
                name=file_data['name'],
                content=file_data['content'],
                type='text'
            )
        else:
            # Create the resource directory if it doesn't exist
            resource_dir = os.path.join(self.upload_folder, str(resource_id))
            os.makedirs(resource_dir, exist_ok=True)

            # Save the file
            filename = secure_filename(file_data.filename)
            # Store only the relative path from the resource directory
            file_path = os.path.join(str(resource_id), filename)
            # Full path for saving the file
            full_path = os.path.join(self.upload_folder, file_path)

            print(f"Saving file to: {full_path}")  # Debug log
            file_data.save(full_path)

            file_record = ResourceFile(
                resource_id=resource_id,
                name=filename,
                file_path=file_path,  # Store relative path
                file_type='text/plain',
                type='file'
            )
        
        db.session.add(file_record)
        db.session.commit()
        
        print(f"File record created: {file_record.to_dict()}")  # Debug log
        return file_record

    def update_resource(self, resource_id: int, user_id: int, name: Optional[str] = None,
                       description: Optional[str] = None, settings: Optional[Dict] = None) -> PersonalResource:
        """Update a personal resource."""
        resource = PersonalResource.query.filter_by(
            id=resource_id,
            user_id=user_id
        ).first_or_404()

        if name is not None:
            resource.name = name
        if description is not None:
            resource.description = description
        if settings is not None:
            resource.settings = settings

        db.session.commit()
        return resource

    def delete_resource(self, resource_id: int, user_id: int) -> None:
        """Delete a personal resource and its files."""
        resource = PersonalResource.query.filter_by(
            id=resource_id,
            user_id=user_id
        ).first_or_404()

        # Delete associated files from storage
        for file in resource.files:
            if file.file_path:
                try:
                    file_path = os.path.join(self.upload_folder, file.file_path)
                    if os.path.exists(file_path):
                        os.remove(file_path)
                except Exception as e:
                    print(f"Error deleting file {file.file_path}: {str(e)}")

        db.session.delete(resource)
        db.session.commit()

    def delete_file(self, resource_id: int, file_id: int, user_id: int) -> None:
        """Delete a file from a resource."""
        resource = PersonalResource.query.filter_by(
            id=resource_id,
            user_id=user_id
        ).first_or_404()

        file = ResourceFile.query.filter_by(
            id=file_id,
            resource_id=resource_id
        ).first_or_404()

        if file.file_path:
            try:
                file_path = os.path.join(self.upload_folder, file.file_path)
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(f"Error deleting file {file.file_path}: {str(e)}")

        db.session.delete(file)
        db.session.commit() 