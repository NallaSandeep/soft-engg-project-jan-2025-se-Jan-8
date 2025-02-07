from datetime import datetime
from app import db
from .base import BaseModel
from .question import Question
import json

class Assignment(db.Model):
    """Assignment model"""
    __tablename__ = 'assignments'

    id = db.Column(db.Integer, primary_key=True)
    week_id = db.Column(db.Integer, db.ForeignKey('weeks.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    type = db.Column(db.String(50), nullable=False)  # 'practice' or 'graded'
    start_date = db.Column(db.DateTime)
    due_date = db.Column(db.DateTime)
    late_submission_penalty = db.Column(db.Float, default=0)  # Percentage penalty
    is_published = db.Column(db.Boolean, default=False)
    points_possible = db.Column(db.Integer, default=0)  # Added explicit points_possible field
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    # Relationships
    week = db.relationship('Week', back_populates='assignments', lazy='joined')
    questions = db.relationship('AssignmentQuestion', back_populates='assignment', lazy='dynamic', cascade='all, delete-orphan')
    submissions = db.relationship('AssignmentSubmission', back_populates='assignment', lazy='dynamic', cascade='all, delete-orphan')
    legacy_submissions = db.relationship('Submission', back_populates='assignment', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Assignment {self.id}: {self.title}>'

    @property
    def total_points(self):
        """Calculate total points from all questions"""
        return sum(aq.question.points for aq in self.questions)

    def to_dict(self):
        """Convert assignment to dictionary"""
        week = self.week
        course = week.course if week else None
        
        # Calculate total points
        points = self.total_points
        self.points_possible = points  # Update points_possible field
        
        # Get questions with their points
        questions_data = []
        for aq in self.questions:
            if aq.question:
                question_dict = aq.question.to_dict()
                question_dict['order'] = aq.order
                question_dict['points'] = aq.question.points  # Use question's points directly
                questions_data.append(question_dict)
        
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'type': self.type,
            'week_id': self.week_id,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'points_possible': points,
            'late_submission_penalty': self.late_submission_penalty,
            'is_published': self.is_published,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'questions': questions_data,
            'week': {
                'id': week.id,
                'number': week.number,
                'title': week.title,
                'course_id': week.course_id
            } if week else None,
            'course': {
                'id': course.id,
                'code': course.code,
                'name': course.name
            } if course else None,
            # Add direct course access for frontend compatibility
            'course_id': course.id if course else None,
            'course_name': course.name if course else None,
            'course_code': course.code if course else None
        }

    def is_available(self):
        """Check if assignment is available for students"""
        now = datetime.utcnow()
        if not self.is_published:
            return False
        if self.start_date and now < self.start_date:
            return False
        if self.type == 'graded' and self.due_date and now > self.due_date:
            return False
        return True

    def calculate_total_points(self):
        """Calculate total points from assigned questions"""
        return sum(q.question.points for q in self.questions)

    def update_points_possible(self):
        """Update points_possible based on assigned questions"""
        self.points_possible = self.calculate_total_points()

class AssignmentQuestion(db.Model):
    """Junction model between Assignment and Question"""
    __tablename__ = 'assignment_questions'

    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignments.id', ondelete='CASCADE'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id', ondelete='CASCADE'), nullable=False)
    order = db.Column(db.Integer, nullable=False)

    # Relationships
    assignment = db.relationship('Assignment', back_populates='questions')
    question = db.relationship('Question', lazy='joined')

    __table_args__ = (
        db.UniqueConstraint('assignment_id', 'question_id', name='unique_assignment_question'),
    )

    def __repr__(self):
        return f'<AssignmentQuestion {self.assignment_id}:{self.question_id}>'

    @property
    def points(self):
        """Get points from the associated question"""
        return self.question.points if self.question else 0

    def to_dict(self):
        """Convert to dictionary with question details"""
        question_dict = self.question.to_dict() if self.question else {}
        return {
            'id': self.id,
            'assignment_id': self.assignment_id,
            'question_id': self.question_id,
            'order': self.order,
            'points': self.points,
            'question': question_dict
        }

class Submission(db.Model):
    """Model for managing assignment submissions"""
    __tablename__ = 'submissions'

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)  # For text submissions
    file_path = db.Column(db.String(255))  # For file submissions
    file_type = db.Column(db.String(50))  # MIME type for files
    file_size = db.Column(db.Integer)  # Size in bytes
    
    # Submission details
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_late = db.Column(db.Boolean, default=False)
    days_late = db.Column(db.Float)  # Number of days submission was late
    attempt_number = db.Column(db.Integer, default=1)
    
    # Grading
    score = db.Column(db.Float)
    feedback = db.Column(db.Text)
    graded_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    graded_at = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='pending')  # pending, graded
    
    # Foreign keys
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignments.id'), nullable=False)
    submitted_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    assignment = db.relationship('Assignment', back_populates='legacy_submissions')
    submitted_by = db.relationship('User', 
                                 foreign_keys=[submitted_by_id], 
                                 back_populates='submissions')
    graded_by = db.relationship('User', 
                               foreign_keys=[graded_by_id], 
                               back_populates='submissions_graded')

    def __repr__(self):
        return f'<Submission {self.id} for Assignment {self.assignment_id}>'

    def to_dict(self):
        """Convert submission to dictionary representation"""
        return {
            'id': self.id,
            'content': self.content if self.assignment.submission_type == 'text' else None,
            'file_path': self.file_path if self.assignment.submission_type == 'file' else None,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'submitted_at': self.submitted_at.isoformat(),
            'is_late': self.is_late,
            'days_late': self.days_late,
            'attempt_number': self.attempt_number,
            'score': self.score,
            'feedback': self.feedback,
            'status': self.status,
            'graded_at': self.graded_at.isoformat() if self.graded_at else None,
            'assignment_id': self.assignment_id,
            'submitted_by': {
                'id': self.submitted_by.id,
                'name': f"{self.submitted_by.first_name} {self.submitted_by.last_name}"
            },
            'graded_by': {
                'id': self.graded_by.id,
                'name': f"{self.graded_by.first_name} {self.graded_by.last_name}"
            } if self.graded_by else None
        }

    def calculate_late_penalty(self):
        """Calculate late submission penalty"""
        if not self.is_late or not self.assignment.late_submission_penalty:
            return 0
            
        return min(
            100,  # Cap at 100% penalty
            self.days_late * self.assignment.late_submission_penalty
        )

class AssignmentSubmission(db.Model):
    """Model for assignment submissions"""
    __tablename__ = 'assignment_submissions'

    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignments.id', ondelete='CASCADE'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    answers = db.Column(db.JSON, nullable=False)  # Store answers for each question
    score = db.Column(db.Float, nullable=True)  # Total score for the submission
    submitted_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False, default='submitted')  # submitted, late, graded
    question_scores = db.Column(db.JSON, nullable=True)  # Store individual question scores
    feedback = db.Column(db.Text, nullable=True)  # Optional feedback from grader
    is_late = db.Column(db.Boolean, default=False)
    days_late = db.Column(db.Float, nullable=True)

    # Relationships
    assignment = db.relationship('Assignment', back_populates='submissions')
    student = db.relationship('User', back_populates='assignment_submissions')

    def __repr__(self):
        return f'<AssignmentSubmission {self.id} by Student {self.student_id}>'

    def to_dict(self):
        """Convert submission to dictionary"""
        return {
            'id': self.id,
            'assignment_id': self.assignment_id,
            'student_id': self.student_id,
            'score': self.score,
            'status': self.status,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
            'answers': self.answers,
            'question_scores': self.question_scores,
            'feedback': self.feedback,
            'is_late': self.is_late,
            'days_late': self.days_late
        }
