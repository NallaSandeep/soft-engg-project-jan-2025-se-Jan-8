"""
Question Bank Module
-----------------
Manages the question bank system for assignments.
Supports multiple question types and automated grading.

Question Model Features:
- Multiple question types (MCQ, MSQ, NUMERIC, text)
- Question metadata and content management
- Points and scoring system
- Question bank organization by course/week/lecture
- Automated answer validation

Question Types:
- MCQ: Single correct answer
- MSQ: Multiple correct answers
- NUMERIC: Numerical answer with tolerance
- TEXT: Free-form text answer

Key Relationships:
- created_by: Teacher who created the question
- course: Associated course (optional)
- week: Associated week (optional)
- lecture: Associated lecture (optional)
- assignments: Assignments using this question

Note: This model is central to the assessment system,
providing reusable questions for both practice and graded assignments.
The flexible question type system supports various assessment needs.
"""

from datetime import datetime
from app import db
from .base import BaseModel
import json

class Question(BaseModel):
    """Model for managing questions in the question bank"""
    __tablename__ = 'questions'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    
    # Question type and content
    type = db.Column(db.String(20), nullable=False)  # MCQ, MSQ, NUMERIC, text
    question_options = db.Column(db.JSON)  # For MCQ/MSQ choices
    correct_answer = db.Column(db.JSON, nullable=False)  # JSON formatted answer(s)
    points = db.Column(db.Integer, default=1)
    explanation = db.Column(db.Text)
    
    # Question bank organization
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=True)
    week_id = db.Column(db.Integer, db.ForeignKey('weeks.id'), nullable=True)
    lecture_id = db.Column(db.Integer, db.ForeignKey('lectures.id'), nullable=True)
    
    # Status and metadata
    status = db.Column(db.String(20), default='active')  # active, inactive
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    # Relationships
    created_by = db.relationship('User', back_populates='questions_created')
    course = db.relationship('Course', backref='questions')
    week = db.relationship('Week', backref='questions')
    lecture = db.relationship('Lecture', backref='questions')
    assignments = db.relationship('AssignmentQuestion', back_populates='question', lazy='dynamic')

    def __repr__(self):
        return f'<Question {self.id}: {self.title}>'

    def to_dict(self):
        """Convert question to dictionary representation"""
        try:
            options = json.loads(self.question_options) if isinstance(self.question_options, str) else self.question_options
            options = options if isinstance(options, list) else []
            
            # Handle correct_answer based on question type
            if isinstance(self.correct_answer, str):
                correct_answer = json.loads(self.correct_answer)
            else:
                correct_answer = self.correct_answer

            if self.type == 'NUMERIC':
                correct_answer = float(correct_answer) if correct_answer else 0
            elif self.type == 'MCQ':
                correct_answer = int(correct_answer) if correct_answer else 0
            elif self.type == 'MSQ':
                correct_answer = list(correct_answer) if correct_answer else []
            
        except (TypeError, json.JSONDecodeError, ValueError):
            options = []
            correct_answer = [] if self.type == 'MSQ' else (0 if self.type == 'MCQ' else 0.0)

        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'type': self.type,
            'options': options,  # Frontend expects 'options'
            'question_options': options,  # Keep for backward compatibility
            'correct_answer': correct_answer,
            'points': self.points,
            'explanation': self.explanation,
            'course_id': self.course_id,
            'week_id': self.week_id,
            'lecture_id': self.lecture_id,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'created_by': {
                'id': self.created_by.id,
                'name': f"{self.created_by.first_name} {self.created_by.last_name}"
            } if self.created_by else None
        }
