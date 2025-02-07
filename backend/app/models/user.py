from werkzeug.security import generate_password_hash, check_password_hash
from .base import BaseModel
from .. import db

class User(BaseModel):
    """User model for storing user account information."""
    
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    is_email_verified = db.Column(db.Boolean, default=False)
    reset_token = db.Column(db.String(100), unique=True)
    reset_token_expires = db.Column(db.DateTime)

    # Relationships
    courses_created = db.relationship('Course', 
                                    back_populates='created_by',
                                    lazy='dynamic',
                                    foreign_keys='Course.created_by_id')
    
    course_enrollments = db.relationship('CourseEnrollment',
                                       back_populates='user',
                                       lazy='dynamic',
                                       overlaps="students,courses_enrolled")
    
    courses_enrolled = db.relationship('Course',
                                     secondary='course_enrollments',
                                     lazy='dynamic',
                                     overlaps="course_enrollments,enrollments",
                                     viewonly=True)
    
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

    @property
    def password(self):
        """Prevent password from being accessed."""
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        """Set password to a hashed password."""
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        """Check if password matches the hashed password."""
        return check_password_hash(self.password_hash, password)

    def get_courses(self):
        """Get all courses associated with the user based on their role."""
        if self.role == 'admin':
            from .course import Course
            return Course.query.all()
        else:
            return self.courses_enrolled

    def __repr__(self):
        return f'<User {self.username}>'
