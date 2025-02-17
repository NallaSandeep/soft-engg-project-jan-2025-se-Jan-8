''' please ignore '''
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
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    # Relationships
    week = db.relationship('Week', back_populates='assignments', lazy='joined')
    questions = db.relationship('AssignmentQuestion', back_populates='assignment', lazy='dynamic')
    submissions = db.relationship('AssignmentSubmission', back_populates='assignment', lazy='dynamic')

    @property
    def total_points(self):
        """Calculate total points from all questions"""
        return sum(aq.question.points for aq in self.questions.all())

    def to_dict(self):
        """Convert assignment to dictionary"""
        week = self.week
        course = week.course if week else None
        
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'type': self.type,
            'week_id': self.week_id,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'points_possible': self.total_points,
            'late_submission_penalty': self.late_submission_penalty,
            'is_published': self.is_published,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'week': {
                'id': week.id,
                'number': week.number,
                'title': week.title,
                'course_id': week.course_id,
                'course': {
                    'id': course.id,
                    'code': course.code,
                    'name': course.name
                } if course else None
            } if week else None
        } 
