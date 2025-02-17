from datetime import datetime
from app import db

class Resource(db.Model):
    """Model for managing course resources"""
    __tablename__ = 'resources'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    type = db.Column(db.String(20), nullable=False)  # file, link, text
    content = db.Column(db.Text)  # For text resources or links
    file_path = db.Column(db.String(255))  # For uploaded files
    file_type = db.Column(db.String(50))  # MIME type for files
    file_size = db.Column(db.Integer)  # Size in bytes
    
    # Foreign keys
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    week_id = db.Column(db.Integer, db.ForeignKey('weeks.id'))  # Optional, can be course-level resource
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Metadata
    is_active = db.Column(db.Boolean, default=True)
    is_public = db.Column(db.Boolean, default=True)  # If false, only enrolled students can access
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    course = db.relationship('Course', back_populates='resources')
    week = db.relationship('Week', back_populates='resources')
    created_by = db.relationship('User',
                               back_populates='resources_uploaded',
                               foreign_keys=[created_by_id],
                               overlaps="uploader")

    def __repr__(self):
        return f'<Resource {self.title} ({self.type})>'

    def to_dict(self):
        """Convert resource to dictionary representation"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'type': self.type,
            'content': self.content if self.type in ['link', 'text'] else None,
            'file_path': self.file_path if self.type == 'file' else None,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'course_id': self.course_id,
            'week_id': self.week_id,
            'created_by': {
                'id': self.created_by.id,
                'name': f"{self.created_by.first_name} {self.created_by.last_name}"
            },
            'is_active': self.is_active,
            'is_public': self.is_public,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def can_access(self, user):
        """Check if a user can access this resource"""
        # Admin can access all resources
        if user.role == 'admin':
            return True
            
        # If resource is public, any authenticated user can access
        if self.is_public:
            return True
            
        # For private resources, check if user is enrolled in the course
        enrollment = self.course.enrollments.filter_by(
            user_id=user.id,
            status='active'
        ).first()
        
        return enrollment is not None

    def can_modify(self, user):
        """Check if a user can modify this resource"""
        # Admin can modify all resources
        if user.role == 'admin':
            return True
            
        # Resource creator can modify their own resources
        if self.created_by_id == user.id:
            return True
            
        # TAs can modify resources in their courses
        enrollment = self.course.enrollments.filter_by(
            user_id=user.id,
            role='ta',
            status='active'
        ).first()
        
        return enrollment is not None
