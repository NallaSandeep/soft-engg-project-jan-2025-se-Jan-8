import unittest
import json
from datetime import datetime, timedelta
from app import create_app, db
from app.models.user import User
from app.models.course import Course, CourseEnrollment
from config import TestingConfig
import logging

logger = logging.getLogger(__name__)

class CourseTestCase(unittest.TestCase):
    def setUp(self):
        """Set up test environment before each test"""
        self.app = create_app(TestingConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.drop_all()
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

        db.session.add_all([self.admin, self.teacher, self.student])
        db.session.commit()

        # Get tokens for each user
        self.admin_token = self._get_token('admin@test.com', 'password123')
        self.teacher_token = self._get_token('teacher@test.com', 'password123')
        self.student_token = self._get_token('student@test.com', 'password123')

    def tearDown(self):
        """Clean up test environment after each test"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def _get_token(self, username, password):
        """Helper method to get JWT token"""
        response = self.client.post('/api/v1/auth/login', json={
            'email': username,
            'password': password
        })
        return json.loads(response.data)['data']['access_token']

    def test_create_course(self):
        """Test course creation"""
        # Test successful course creation
        response = self.client.post('/api/v1/courses/', 
            headers={'Authorization': f'Bearer {self.admin_token}'},
            json={
                'code': 'CS101',
                'name': 'Introduction to Computer Science',
                'description': 'Basic programming concepts',
                'created_by_id': self.teacher.id,
                'start_date': (datetime.now() + timedelta(days=1)).date().isoformat(),
                'end_date': (datetime.now() + timedelta(days=90)).date().isoformat(),
                'max_students': 30,
                'enrollment_type': 'open'
            })
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['data']['code'], 'CS101')
        self.assertEqual(data['data']['name'], 'Introduction to Computer Science')

        # Test duplicate course code
        response = self.client.post('/api/v1/courses/',
            headers={'Authorization': f'Bearer {self.admin_token}'},
            json={
                'code': 'CS101',
                'name': 'Another Course',
                'description': 'Description',
                'created_by_id': self.teacher.id
            })
        
        self.assertEqual(response.status_code, 409)

        # Test non-admin user
        response = self.client.post('/api/v1/courses/',
            headers={'Authorization': f'Bearer {self.teacher_token}'},
            json={
                'code': 'CS102',
                'name': 'Another Course',
                'description': 'Description',
                'created_by_id': self.teacher.id
            })
        
        self.assertEqual(response.status_code, 403)

    def test_get_courses(self):
        """Test getting courses list"""
        # Create test courses
        course1 = Course(
            code='CS101',
            name='Course 1',
            description='Description 1',
            created_by_id=self.teacher.id
        )
        course2 = Course(
            code='CS102',
            name='Course 2',
            description='Description 2',
            created_by_id=self.teacher.id
        )
        db.session.add_all([course1, course2])
        db.session.commit()

        # Test admin view (all courses)
        response = self.client.get('/api/v1/courses/',
            headers={'Authorization': f'Bearer {self.admin_token}'})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data['data']), 2)

        # Test teacher view (only their courses)
        response = self.client.get('/api/v1/courses/',
            headers={'Authorization': f'Bearer {self.teacher_token}'})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data['data']), 2)

        # Test student view (only enrolled courses)
        response = self.client.get('/api/v1/courses/',
            headers={'Authorization': f'Bearer {self.student_token}'})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data['data']), 0)

    def test_get_course(self):
        """Test getting a specific course"""
        # Create test course
        course = Course(
            code='CS101',
            name='Test Course',
            description='Test Description',
            created_by_id=self.admin.id
        )
        db.session.add(course)
        db.session.commit()

        # Test successful retrieval
        response = self.client.get(f'/api/v1/courses/{course.id}',
            headers={'Authorization': f'Bearer {self.admin_token}'})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['data']['code'], 'CS101')

        # Test non-existent course
        response = self.client.get('/api/v1/courses/999',
            headers={'Authorization': f'Bearer {self.admin_token}'})
        
        self.assertEqual(response.status_code, 404)

    def test_update_course(self):
        """Test updating a course"""
        # Create test course
        course = Course(
            code='CS101',
            name='Test Course',
            description='Test Description',
            created_by_id=self.teacher.id
        )
        db.session.add(course)
        db.session.commit()

        # Test successful update by instructor
        response = self.client.put(f'/api/v1/courses/{course.id}',
            headers={'Authorization': f'Bearer {self.admin_token}'},
            json={
                'name': 'Updated Course',
                'description': 'Updated Description'
            })
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['course']['name'], 'Updated Course')
        self.assertEqual(data['course']['description'], 'Updated Description')

        # Test update by non-instructor
        other_teacher = User(
            username='teacher2_test',
            email='teacher2@test.com',
            password='password123',
            role='teacher',
            first_name='Teacher2',
            last_name='User',
            is_active=True
        )
        db.session.add(other_teacher)
        db.session.commit()
        other_teacher_token = self._get_token('teacher2@test.com', 'password123')

        response = self.client.put(f'/api/v1/courses/{course.id}',
            headers={'Authorization': f'Bearer {other_teacher_token}'},
            json={
                'name': 'Unauthorized Update'
            })
        
        self.assertEqual(response.status_code, 403)

    def test_delete_course(self):
        """Test deleting a course"""
        # Create test course
        course = Course(
            code='CS101',
            name='Test Course',
            description='Test Description',
            created_by_id=self.admin.id
        )
        db.session.add(course)
        db.session.commit()

        # Test deletion by non-admin
        response = self.client.delete(f'/api/v1/courses/{course.id}',
            headers={'Authorization': f'Bearer {self.teacher_token}'})
        
        self.assertEqual(response.status_code, 403)

        # Test successful deletion by admin
        response = self.client.delete(f'/api/v1/courses/{course.id}',
            headers={'Authorization': f'Bearer {self.admin_token}'})
        
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(Course.query.get(course.id))

    def test_enroll_in_course(self):
        """Test course enrollment"""
        # Create test course
        course = Course(
            code='CS101',
            name='Test Course',
            description='Test Description',
            created_by_id=self.teacher.id,
            max_students=2
        )
        db.session.add(course)
        db.session.commit()

        # Test successful enrollment
        response = self.client.post(f'/api/v1/courses/{course.id}/enroll',
            headers={'Authorization': f'Bearer {self.student_token}'})
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['enrollment']['course_id'], course.id)
        self.assertEqual(data['enrollment']['user_id'], self.student.id)

        # Test duplicate enrollment
        response = self.client.post(f'/api/v1/courses/{course.id}/enroll',
            headers={'Authorization': f'Bearer {self.student_token}'})
        
        self.assertEqual(response.status_code, 409)

        # Test enrollment in full course
        other_student = User(
            username='student2_test',
            email='student2@test.com',
            password='password123',
            role='student',
            first_name='Student2',
            last_name='User',
            is_active=True
        )
        db.session.add(other_student)
        db.session.commit()
        other_student_token = self._get_token('student2@test.com', 'password123')

        # First enrollment should succeed
        response = self.client.post(f'/api/v1/courses/{course.id}/enroll',
            headers={'Authorization': f'Bearer {other_student_token}'})
        self.assertEqual(response.status_code, 201)

        # Third enrollment should fail (max_students=2)
        third_student = User(
            username='student3_test',
            email='student3@test.com',
            password='password123',
            role='student',
            first_name='Student3',
            last_name='User',
            is_active=True
        )
        db.session.add(third_student)
        db.session.commit()
        third_student_token = self._get_token('student3@test.com', 'password123')

        response = self.client.post(f'/api/v1/courses/{course.id}/enroll',
            headers={'Authorization': f'Bearer {third_student_token}'})
        self.assertEqual(response.status_code, 400)

if __name__ == '__main__':
    unittest.main() 