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

    def to_dict(self):
        """Convert week to dictionary representation"""
        return {
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

class Lecture(BaseModel):
    """Model for managing course lectures"""
    __tablename__ = 'lectures'

    id = db.Column(db.Integer, primary_key=True)
    week_id = db.Column(db.Integer, db.ForeignKey('weeks.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    youtube_url = db.Column(db.String(500))
    transcript = db.Column(db.Text)
    order = db.Column(db.Integer, nullable=False)
    is_published = db.Column(db.Boolean, default=False)

    # Relationships
    week = db.relationship('Week', back_populates='lectures')

    def __repr__(self):
        return f'<Lecture {self.title}>'

    def to_dict(self):
        """Convert lecture to dictionary representation"""
        return {
            'id': self.id,
            'week_id': self.week_id,
            'title': self.title,
            'description': self.description,
            'youtube_url': self.youtube_url,
            'transcript': self.transcript,
            'order': self.order,
            'is_published': self.is_published
        } 