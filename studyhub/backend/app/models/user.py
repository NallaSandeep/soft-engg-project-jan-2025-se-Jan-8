from werkzeug.security import generate_password_hash, check_password_hash
from .base import BaseModel
from .. import db
from datetime import datetime

class User(BaseModel):
    """User model for storing user account information."""
    
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # admin, teacher, student
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    is_active = db.Column(db.Boolean, default=True)
    is_email_verified = db.Column(db.Boolean, default=False)
    last_login = db.Column(db.DateTime)
    profile_image = db.Column(db.String(255))
    reset_token = db.Column(db.String(100), unique=True)
    reset_token_expires = db.Column(db.DateTime)

    # Relationships
    courses_created = db.relationship('Course', 
                                    back_populates='created_by',
                                    lazy='dynamic',
                                    foreign_keys='Course.created_by_id')
    course_enrollments = db.relationship('CourseEnrollment',
                                       back_populates='user',
                                       lazy='dynamic')
    
    resources_uploaded = db.relationship('Resource',
                                       back_populates='created_by',
                                       lazy='dynamic',
                                       foreign_keys='Resource.created_by_id',
                                       overlaps="uploader")
    
    questions_created = db.relationship('Question',
                                      back_populates='created_by',
                                      lazy='dynamic',
                                      foreign_keys='Question.created_by_id')
    
    submissions = db.relationship('Submission',
                                back_populates='submitted_by',
                                lazy='dynamic',
                                foreign_keys='Submission.submitted_by_id')
    
    submissions_graded = db.relationship('Submission',
                                       back_populates='graded_by',
                                       lazy='dynamic',
                                       foreign_keys='Submission.graded_by_id')

    assignment_submissions = db.relationship('AssignmentSubmission', back_populates='student', lazy='dynamic')

    personal_resources = db.relationship('PersonalResource',
                                       back_populates='user',
                                       lazy='dynamic')

    @property
    def password(self):
        """Password getter"""
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        """Password setter"""
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        """Verify password"""
        return check_password_hash(self.password_hash, password)

    def update_last_login(self):
        """Update last login timestamp"""
        self.last_login = datetime.utcnow()
        db.session.commit()

    @property
    def courses_enrolled(self):
        """Get courses user is enrolled in"""
        return [enrollment.course for enrollment in self.course_enrollments]

    def to_dict(self):
        """Convert user to dictionary representation"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'is_active': self.is_active,
            'is_email_verified': self.is_email_verified,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'profile_image': self.profile_image,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def __repr__(self):
        return f'<User {self.username}>'
