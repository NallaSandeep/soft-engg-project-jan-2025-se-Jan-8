"""Personal resources models."""
from datetime import datetime
from app import db
from .base import BaseModel
from sqlalchemy.dialects.postgresql import JSON

class PersonalResource(BaseModel):
    """Model for personal resources"""
    __tablename__ = 'personal_resources'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    settings = db.Column(JSON)

    # Relationships
    user = db.relationship('User', back_populates='personal_resources')
    course = db.relationship('Course', back_populates='personal_resources')
    files = db.relationship('ResourceFile', back_populates='resource', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<PersonalResource {self.name} (User: {self.user_id}, Course: {self.course_id})>'

    def to_dict(self):
        """Convert resource to dictionary representation"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'course_id': self.course_id,
            'name': self.name,
            'description': self.description,
            'is_active': self.is_active,
            'settings': self.settings,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'files': [f.to_dict() for f in self.files],
            'course': {
                'id': self.course.id,
                'code': self.course.code,
                'name': self.course.name
            } if self.course else None
        }

class ResourceFile(BaseModel):
    """Model for resource files"""
    __tablename__ = 'resource_files'

    id = db.Column(db.Integer, primary_key=True)
    resource_id = db.Column(db.Integer, db.ForeignKey('personal_resources.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # text, file, url
    content = db.Column(db.Text)  # For text/notes
    file_path = db.Column(db.String(255))  # For uploaded files
    file_type = db.Column(db.String(50))  # MIME type
    file_size = db.Column(db.Integer)

    # Relationship
    resource = db.relationship('PersonalResource', back_populates='files')

    def __repr__(self):
        return f'<ResourceFile {self.name} (Type: {self.type})>'

    def to_dict(self):
        """Convert file to dictionary representation"""
        return {
            'id': self.id,
            'resource_id': self.resource_id,
            'name': self.name,
            'type': self.type,
            'content': self.content if self.type in ['text', 'url'] else None,
            'file_path': self.file_path if self.type == 'file' else None,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        } 