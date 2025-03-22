from datetime import datetime
from app import db

class Course(db.Model):
    """Course model for managing course information"""
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    is_active = db.Column(db.Boolean, default=True)
    max_students = db.Column(db.Integer)
    enrollment_type = db.Column(db.String(20), default='open')  # open, closed, invite_only
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    created_by = db.relationship('User', 
                               back_populates='courses_created',
                               foreign_keys=[created_by_id])
    enrollments = db.relationship('CourseEnrollment', 
                                back_populates='course',
                                lazy='dynamic',
                                cascade='all, delete-orphan',
                                overlaps="students,courses_enrolled")
    resources = db.relationship('Resource',
                              back_populates='course',
                              lazy='dynamic',
                              cascade='all, delete-orphan')
    personal_resources = db.relationship('PersonalResource',
                                       back_populates='course',
                                       lazy='dynamic',
                                       cascade='all, delete-orphan')
    weeks = db.relationship('Week',
                          back_populates='course',
                          lazy='dynamic',
                          cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Course {self.code}: {self.name}>'

    def to_dict(self):
        """Convert course to dictionary representation"""
        enrolled_count = self.get_enrolled_count('student')
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'description': self.description,
            'created_by_id': self.created_by_id,
            'created_by': f"{self.created_by.first_name} {self.created_by.last_name}",
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'is_active': self.is_active,
            'max_students': self.max_students or 0,
            'enrollment_type': self.enrollment_type,
            'created_at': self.created_at.isoformat(),
            'enrolled_count': enrolled_count,
            'enrolled_students': enrolled_count,  # Keep for backward compatibility
            'teaching_assistants': self.get_enrolled_count('ta')
        }

    def get_enrolled_count(self, role):
        """Get count of enrolled users by role"""
        return self.enrollments.filter_by(role=role, status='active').count()

class CourseEnrollment(db.Model):
    """Model for managing course enrollments"""
    __tablename__ = 'course_enrollments'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # student, ta
    status = db.Column(db.String(20), default='active')  # active, inactive, pending
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    course = db.relationship('Course', 
                           back_populates='enrollments',
                           overlaps="students,courses_enrolled")
    user = db.relationship('User', 
                         back_populates='course_enrollments',
                         overlaps="students,courses_enrolled")

    __table_args__ = (
        db.UniqueConstraint('course_id', 'user_id', name='unique_course_enrollment'),
    )

    def __repr__(self):
        return f'<CourseEnrollment {self.user_id} in {self.course_id}>'

    def to_dict(self):
        """Convert enrollment to dictionary representation"""
        return {
            'course_id': self.course_id,
            'user_id': self.user_id,
            'role': self.role,
            'status': self.status,
            'enrolled_at': self.enrolled_at.isoformat()
        }
