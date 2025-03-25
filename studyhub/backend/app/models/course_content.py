"""
Course Content Module
------------------
Manages the content structure and progress tracking for courses.
Contains Week, Lecture, and LectureProgress models.

Week Model Features:
- Organizes course content into weekly units
- Manages week metadata and publication status
- Tracks relationships with lectures and assignments
- Calculates student progress for the week

Lecture Model Features:
- Manages course lecture content
- Supports multiple content types (youtube, pdf)
- Handles file and video content
- Tracks lecture ordering and publication status

LectureProgress Model Features:
- Tracks student progress in lectures
- Records completion status and timestamps
- Supports progress calculation for courses
- Enables progress-based features

Key Relationships:
Week:
- course: Parent course
- lectures: Week's lectures
- assignments: Week's assignments
- resources: Week's resources

Lecture:
- week: Parent week
- progress_records: Student progress records

LectureProgress:
- lecture: Associated lecture
- user: Student whose progress is tracked

Note: These models are essential for content organization
and progress tracking in the learning platform.
"""

from datetime import datetime
from app import db
from .base import BaseModel

class Week(db.Model):
    """Model for course weeks"""
    __tablename__ = 'weeks'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id', ondelete='CASCADE'), nullable=False)
    number = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    is_published = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    # Relationships
    course = db.relationship('Course', back_populates='weeks')
    lectures = db.relationship('Lecture', back_populates='week', lazy='dynamic', cascade='all, delete-orphan')
    assignments = db.relationship('Assignment', back_populates='week', lazy='dynamic', cascade='all, delete-orphan')
    resources = db.relationship('Resource', back_populates='week', lazy='dynamic', cascade='all, delete-orphan')

    __table_args__ = (
        db.UniqueConstraint('course_id', 'number', name='unique_week_number'),
    )

    def __repr__(self):
        return f'<Week {self.number} of Course {self.course_id}>'

    def calculate_progress(self, user_id):
        """Calculate progress for a specific user in this week"""
        total_items = 0
        completed_items = 0

        # Count lectures and their completion
        lectures = self.lectures.all()
        total_items += len(lectures)
        for lecture in lectures:
            if lecture.progress_records.filter_by(user_id=user_id, completed=True).first():
                completed_items += 1

        # Count assignments and their completion
        assignments = self.assignments.all()
        total_items += len(assignments)
        for assignment in assignments:
            if assignment.submissions.filter_by(user_id=user_id).first():
                completed_items += 1

        # Calculate percentage
        progress_percentage = (completed_items / total_items * 100) if total_items > 0 else 0
        return {
            'total_items': total_items,
            'completed_items': completed_items,
            'percentage': round(progress_percentage, 2)
        }

    def to_dict(self, user_id=None):
        """Convert week to dictionary representation"""
        data = {
            'id': self.id,
            'course_id': self.course_id,
            'number': self.number,
            'title': self.title,
            'description': self.description,
            'is_published': self.is_published,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'lectures': [lecture.to_dict() for lecture in self.lectures],
            'assignments': [assignment.to_dict() for assignment in self.assignments],
            'resources': [resource.to_dict() for resource in self.resources]
        }
        
        # Add progress information if user_id is provided
        if user_id:
            data['progress'] = self.calculate_progress(user_id)
            
        return data

class Lecture(BaseModel):
    """Model for managing course lectures
    
    Content Types:
    - youtube: Uses youtube_url for video and transcript for video transcript
    - pdf: Uses file_path for PDF location and transcript for extracted text
    """
    __tablename__ = 'lectures'

    id = db.Column(db.Integer, primary_key=True)
    week_id = db.Column(db.Integer, db.ForeignKey('weeks.id'), nullable=False)
    lecture_number = db.Column(db.Integer, nullable=False)  # Represents the lecture number within a week
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    content_type = db.Column(db.String(20), nullable=False)  # 'youtube' or 'pdf'
    youtube_url = db.Column(db.String(500))  # Used when content_type is 'youtube'
    file_path = db.Column(db.String(500))    # Used when content_type is 'pdf'
    transcript = db.Column(db.Text)          # Stores video transcript or PDF text
    order = db.Column(db.Integer, nullable=False)  # For display/sort order
    is_published = db.Column(db.Boolean, default=False)

    # Relationships
    week = db.relationship('Week', back_populates='lectures')

    __table_args__ = (
        db.UniqueConstraint('week_id', 'lecture_number', name='unique_lecture_number'),
    )

    def __repr__(self):
        return f'<Lecture {self.lecture_number} of Week {self.week_id}>'

    def to_dict(self):
        """Convert lecture to dictionary representation"""
        return {
            'id': self.id,
            'week_id': self.week_id,
            'lecture_number': self.lecture_number,
            'title': self.title,
            'description': self.description,
            'content_type': self.content_type,
            'youtube_url': self.youtube_url if self.content_type == 'youtube' else None,
            'file_path': self.file_path if self.content_type == 'pdf' else None,
            'transcript': self.transcript,
            'order': self.order,
            'is_published': self.is_published
        }

class LectureProgress(BaseModel):
    """Model for tracking student progress in lectures"""
    __tablename__ = 'lecture_progress'

    id = db.Column(db.Integer, primary_key=True)
    lecture_id = db.Column(db.Integer, db.ForeignKey('lectures.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    completed = db.Column(db.Boolean, default=True)  # True when lecture is visited
    completed_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    # Relationships
    lecture = db.relationship('Lecture', backref=db.backref('progress_records', lazy='dynamic', cascade='all, delete-orphan'))
    user = db.relationship('User', backref=db.backref('lecture_progress', lazy='dynamic', cascade='all, delete-orphan'))

    __table_args__ = (
        db.UniqueConstraint('lecture_id', 'user_id', name='unique_lecture_progress'),
    )

    def __repr__(self):
        return f'<LectureProgress {self.user_id} - {self.lecture_id}>'

    def to_dict(self):
        """Convert progress to dictionary representation"""
        return {
            'id': self.id,
            'lecture_id': self.lecture_id,
            'user_id': self.user_id,
            'completed': self.completed,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        } 