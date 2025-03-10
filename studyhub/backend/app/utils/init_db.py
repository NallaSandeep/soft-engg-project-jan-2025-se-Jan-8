from ..models.user import User
from ..models.course import Course
from ..models.resource import Resource
from ..models.assignment import Assignment
from ..models.enrollment import CourseEnrollment
from .. import db
from datetime import datetime, timedelta

def init_db():
    """Initialize database with test users and course data."""
    try:
        # Create admin user
        admin = User(
            username='admin',
            email='admin@studybot.com',
            password='admin123',
            role='admin',
            is_active=True
        )
        admin.save()

        # Create TA user
        ta = User(
            username='ta',
            email='ta@studybot.com',
            password='ta123',
            role='ta',
            is_active=True
        )
        ta.save()

        # Create student user
        student = User(
            username='student1',
            email='student1@studybot.com',
            password='student123',
            role='student',
            is_active=True
        )
        student.save()

        # Create courses
        cs201 = Course(
            code='CS201',
            name='Advanced Programming Concepts',
            description='Deep dive into advanced programming patterns and practices.',
            created_by_id=admin.id,
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow() + timedelta(days=90),
            max_students=30,
            enrollment_type='open'
        )
        cs201.save()

        se101 = Course(
            code='SE101',
            name='Introduction to Software Engineering',
            description='Fundamentals of software engineering and development processes',
            created_by_id=admin.id,
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow() + timedelta(days=90),
            max_students=30,
            enrollment_type='open'
        )
        se101.save()

        # Create enrollments
        enrollments = [
            CourseEnrollment(
                course_id=cs201.id,
                user_id=student.id,
                role='student',
                status='active'
            ),
            CourseEnrollment(
                course_id=cs201.id,
                user_id=ta.id,
                role='ta',
                status='active'
            ),
            CourseEnrollment(
                course_id=se101.id,
                user_id=student.id,
                role='student',
                status='active'
            )
        ]
        for enrollment in enrollments:
            enrollment.save()

        # Create SE101 lectures
        se_lectures = [
            Resource(
                title='Identifying Users and Requirements',
                description='Understanding user needs and requirements gathering',
                type='video',
                content='https://www.youtube.com/watch?v=L9-CUa0BlLk',
                course_id=se101.id,
                created_by_id=admin.id,
                is_public=True,
                week_number=1,
                order=1
            ),
            Resource(
                title='Functional and Non-functional Requirements',
                description='Understanding different types of requirements',
                type='video',
                content='https://www.youtube.com/watch?v=CKGjkKXpCsw',
                course_id=se101.id,
                created_by_id=admin.id,
                is_public=True,
                week_number=1,
                order=2
            ),
            Resource(
                title='Software Requirement Specification',
                description='Creating and managing software requirements specifications',
                type='video',
                content='https://www.youtube.com/watch?v=Ml0HET0Va_c',
                course_id=se101.id,
                created_by_id=admin.id,
                is_public=True,
                week_number=1,
                order=3
            )
        ]
        for lecture in se_lectures:
            lecture.save()

        # Create test assignment
        assignment = Assignment(
            title='Programming Assignment 1',
            description='Basic programming exercises',
            instructions='Complete the following exercises...',
            max_score=100,
            weight=1.0,
            start_date=datetime.utcnow(),
            due_date=datetime.utcnow() + timedelta(days=7),
            submission_type='text',
            course_id=cs201.id,
            created_by_id=admin.id,
            is_published=True
        )
        assignment.save()

        print("Database initialized with test users and course data!")
        return True
    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        db.session.rollback()
        return False 