import unittest
import json
import os
from io import BytesIO
from datetime import datetime, timedelta
from app import create_app, db
from app.models.user import User
from app.models.course import Course
from app.models.assignment import Assignment, Submission

class AssignmentTestCase(unittest.TestCase):
    def setUp(self):
        """Set up test environment before each test"""
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Create test users
        self.admin = User(
            username='admin_test',
            email='admin@test.com',
            password='password123',
            role='admin',
            first_name='Admin',
            last_name='User',
            is_active=True
        )

        self.teacher = User(
            username='teacher_test',
            email='teacher@test.com',
            password='password123',
            role='teacher',
            first_name='Teacher',
            last_name='User',
            is_active=True
        )

        self.student = User(
            username='student_test',
            email='student@test.com',
            password='password123',
            role='student',
            first_name='Student',
            last_name='User',
            is_active=True
        )

        self.ta = User(
            username='ta_test',
            email='ta@test.com',
            password='password123',
            role='ta',
            first_name='TA',
            last_name='User',
            is_active=True
        )

        db.session.add_all([self.admin, self.teacher, self.student, self.ta])
        db.session.commit()

        # Create test course
        self.course = Course(
            code='CS101',
            name='Test Course',
            description='Test Description',
            instructor_id=self.teacher.id
        )
        db.session.add(self.course)
        db.session.commit()

        # Enroll student and TA
        self.course.enrollments.extend([
            CourseEnrollment(user_id=self.student.id, role='student'),
            CourseEnrollment(user_id=self.ta.id, role='ta')
        ])
        db.session.commit()

        # Get tokens for each user
        self.admin_token = self._get_token('admin_test', 'password123')
        self.teacher_token = self._get_token('teacher_test', 'password123')
        self.student_token = self._get_token('student_test', 'password123')
        self.ta_token = self._get_token('ta_test', 'password123')

    def tearDown(self):
        """Clean up test environment after each test"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

        # Clean up uploaded files
        upload_dir = self.app.config['UPLOAD_FOLDER']
        if os.path.exists(upload_dir):
            for file in os.listdir(upload_dir):
                os.remove(os.path.join(upload_dir, file))
            os.rmdir(upload_dir)

    def _get_token(self, username, password):
        """Helper method to get JWT token"""
        response = self.client.post('/api/v1/auth/login', json={
            'username': username,
            'password': password
        })
        return json.loads(response.data)['access_token']

    def test_create_assignment(self):
        """Test creating an assignment"""
        # Test successful creation
        start_date = datetime.utcnow()
        due_date = start_date + timedelta(days=7)
        
        response = self.client.post(f'/api/v1/courses/{self.course.id}/assignments',
            headers={'Authorization': f'Bearer {self.teacher_token}'},
            json={
                'title': 'Test Assignment',
                'description': 'Test Description',
                'instructions': 'Test Instructions',
                'max_score': 100,
                'weight': 1.0,
                'start_date': start_date.isoformat(),
                'due_date': due_date.isoformat(),
                'submission_type': 'text',
                'is_published': True
            })
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['assignment']['title'], 'Test Assignment')
        self.assertEqual(data['assignment']['max_score'], 100)

        # Test missing required fields
        response = self.client.post(f'/api/v1/courses/{self.course.id}/assignments',
            headers={'Authorization': f'Bearer {self.teacher_token}'},
            json={
                'title': 'Test Assignment'
            })
        
        self.assertEqual(response.status_code, 400)

        # Test unauthorized user
        response = self.client.post(f'/api/v1/courses/{self.course.id}/assignments',
            headers={'Authorization': f'Bearer {self.student_token}'},
            json={
                'title': 'Test Assignment',
                'max_score': 100,
                'submission_type': 'text'
            })
        
        self.assertEqual(response.status_code, 403)

    def test_get_assignments(self):
        """Test getting course assignments"""
        # Create test assignments
        start_date = datetime.utcnow()
        due_date = start_date + timedelta(days=7)
        
        assignment1 = Assignment(
            title='Assignment 1',
            description='Description 1',
            max_score=100,
            submission_type='text',
            start_date=start_date,
            due_date=due_date,
            course_id=self.course.id,
            created_by_id=self.teacher.id,
            is_published=True
        )
        assignment2 = Assignment(
            title='Assignment 2',
            description='Description 2',
            max_score=100,
            submission_type='text',
            start_date=start_date,
            due_date=due_date,
            course_id=self.course.id,
            created_by_id=self.teacher.id,
            is_published=False
        )
        db.session.add_all([assignment1, assignment2])
        db.session.commit()

        # Test teacher view (all assignments)
        response = self.client.get(f'/api/v1/courses/{self.course.id}/assignments',
            headers={'Authorization': f'Bearer {self.teacher_token}'})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data['assignments']), 2)

        # Test student view (only published assignments)
        response = self.client.get(f'/api/v1/courses/{self.course.id}/assignments',
            headers={'Authorization': f'Bearer {self.student_token}'})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data['assignments']), 1)

    def test_update_assignment(self):
        """Test updating an assignment"""
        # Create test assignment
        start_date = datetime.utcnow()
        due_date = start_date + timedelta(days=7)
        
        assignment = Assignment(
            title='Test Assignment',
            description='Test Description',
            max_score=100,
            submission_type='text',
            start_date=start_date,
            due_date=due_date,
            course_id=self.course.id,
            created_by_id=self.teacher.id
        )
        db.session.add(assignment)
        db.session.commit()

        # Test successful update
        response = self.client.put(f'/api/v1/assignments/{assignment.id}',
            headers={'Authorization': f'Bearer {self.teacher_token}'},
            json={
                'title': 'Updated Assignment',
                'description': 'Updated Description',
                'max_score': 150
            })
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['assignment']['title'], 'Updated Assignment')
        self.assertEqual(data['assignment']['max_score'], 150)

        # Test unauthorized update
        response = self.client.put(f'/api/v1/assignments/{assignment.id}',
            headers={'Authorization': f'Bearer {self.student_token}'},
            json={
                'title': 'Unauthorized Update'
            })
        
        self.assertEqual(response.status_code, 403)

    def test_submit_assignment(self):
        """Test submitting an assignment"""
        # Create test assignment
        start_date = datetime.utcnow()
        due_date = start_date + timedelta(days=7)
        
        assignment = Assignment(
            title='Test Assignment',
            description='Test Description',
            max_score=100,
            submission_type='text',
            start_date=start_date,
            due_date=due_date,
            course_id=self.course.id,
            created_by_id=self.teacher.id,
            is_published=True
        )
        db.session.add(assignment)
        db.session.commit()

        # Test successful text submission
        response = self.client.post(f'/api/v1/assignments/{assignment.id}/submit',
            headers={'Authorization': f'Bearer {self.student_token}'},
            data={
                'content': 'Test submission content'
            })
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['submission']['content'], 'Test submission content')
        self.assertEqual(data['submission']['status'], 'pending')

        # Test file submission
        assignment.submission_type = 'file'
        assignment.allowed_file_types = 'txt,pdf'
        db.session.commit()

        file_content = b'Test file content'
        file = (BytesIO(file_content), 'test.txt')

        response = self.client.post(f'/api/v1/assignments/{assignment.id}/submit',
            headers={'Authorization': f'Bearer {self.student_token}'},
            data={
                'file': file
            },
            content_type='multipart/form-data')
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertIsNotNone(data['submission']['file_path'])

        # Test submission to unpublished assignment
        assignment.is_published = False
        db.session.commit()

        response = self.client.post(f'/api/v1/assignments/{assignment.id}/submit',
            headers={'Authorization': f'Bearer {self.student_token}'},
            data={
                'content': 'Test content'
            })
        
        self.assertEqual(response.status_code, 403)

    def test_grade_submission(self):
        """Test grading a submission"""
        # Create test assignment and submission
        start_date = datetime.utcnow()
        due_date = start_date + timedelta(days=7)
        
        assignment = Assignment(
            title='Test Assignment',
            description='Test Description',
            max_score=100,
            submission_type='text',
            start_date=start_date,
            due_date=due_date,
            course_id=self.course.id,
            created_by_id=self.teacher.id,
            is_published=True
        )
        db.session.add(assignment)
        db.session.commit()

        submission = Submission(
            content='Test submission content',
            assignment_id=assignment.id,
            submitted_by_id=self.student.id
        )
        db.session.add(submission)
        db.session.commit()

        # Test successful grading by teacher
        response = self.client.post(f'/api/v1/submissions/{submission.id}/grade',
            headers={'Authorization': f'Bearer {self.teacher_token}'},
            json={
                'score': 85,
                'feedback': 'Good work!'
            })
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['submission']['score'], 85)
        self.assertEqual(data['submission']['feedback'], 'Good work!')
        self.assertEqual(data['submission']['status'], 'graded')

        # Test grading by TA
        submission2 = Submission(
            content='Another submission',
            assignment_id=assignment.id,
            submitted_by_id=self.student.id
        )
        db.session.add(submission2)
        db.session.commit()

        response = self.client.post(f'/api/v1/submissions/{submission2.id}/grade',
            headers={'Authorization': f'Bearer {self.ta_token}'},
            json={
                'score': 90,
                'feedback': 'Excellent!'
            })
        
        self.assertEqual(response.status_code, 200)

        # Test invalid score
        response = self.client.post(f'/api/v1/submissions/{submission.id}/grade',
            headers={'Authorization': f'Bearer {self.teacher_token}'},
            json={
                'score': 150,  # Above max_score
                'feedback': 'Invalid score'
            })
        
        self.assertEqual(response.status_code, 400)

        # Test unauthorized grading
        response = self.client.post(f'/api/v1/submissions/{submission.id}/grade',
            headers={'Authorization': f'Bearer {self.student_token}'},
            json={
                'score': 80,
                'feedback': 'Unauthorized'
            })
        
        self.assertEqual(response.status_code, 403)

if __name__ == '__main__':
    unittest.main() 