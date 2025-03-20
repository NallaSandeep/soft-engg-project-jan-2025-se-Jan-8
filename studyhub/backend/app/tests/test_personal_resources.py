import unittest
import json
from datetime import datetime
from app import create_app, db
from app.models import User, Course, CourseEnrollment, PersonalResource, ResourceFile
from config import config

class PersonalResourceTestCase(unittest.TestCase):
    def setUp(self):
        """Set up test environment before each test"""
        self.app = create_app(config['testing'])
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Drop all tables and recreate them
        db.drop_all()
        db.create_all()

        # Create test users (matching init_db.py pattern)
        self.student = User(
            username='student1',
            email='student1@studyhub.com',
            password='student123',
            role='student',
            first_name='Student1',
            last_name='User',
            is_email_verified=True,
            is_active=True
        )
        self.student.password = 'student123'

        self.teacher = User(
            username='teacher',
            email='teacher@studyhub.com',
            password='teacher123',
            role='teacher',
            first_name='John',
            last_name='Smith',
            is_email_verified=True,
            is_active=True
        )
        self.teacher.password = 'teacher123'

        db.session.add_all([self.teacher, self.student])
        db.session.commit()

        # Create test course (matching init_db.py pattern)
        self.course = Course(
            code='CS101',
            name='Introduction to Programming',
            description='Learn Python programming fundamentals',
            created_by_id=self.teacher.id,
            max_students=30,
            enrollment_type='open',
            start_date=datetime.now().date(),
            end_date=datetime.now().date(),
            is_active=True
        )
        db.session.add(self.course)
        db.session.commit()

        # Enroll student
        self.enrollment = CourseEnrollment(
            user_id=self.student.id,
            course_id=self.course.id,
            status='active',
            role='student'  # Adding role field
        )
        db.session.add(self.enrollment)
        db.session.commit()

        # Create a test personal resource
        self.resource = PersonalResource(
            name='Lecture Notes - CS101',
            description='My personal notes from lectures',
            user_id=self.student.id,
            course_id=self.course.id,
            is_active=True,
            settings={'visibility': 'private'}
        )
        db.session.add(self.resource)
        db.session.commit()

        # Create test resource files
        self.files = [
            ResourceFile(
                name='Week 1 Notes.txt',
                type='text',
                content='Key points from week 1:\n- Introduction to the course\n- Basic concepts\n- Important definitions',
                file_type='text/plain',
                file_size=150,
                resource_id=self.resource.id
            ),
            ResourceFile(
                name='Week 2 Summary.txt',
                type='text',
                content='Summary of week 2:\n- Advanced topics\n- Practice problems\n- Study tips',
                file_type='text/plain',
                file_size=120,
                resource_id=self.resource.id
            )
        ]
        db.session.add_all(self.files)
        db.session.commit()

        # Get authentication token
        response = self.client.post('/api/v1/auth/login',
            json={'email': 'student1@studyhub.com', 'password': 'student123'})
        data = json.loads(response.data)
        self.student_token = data['data']['access_token']

    def tearDown(self):
        """Clean up test environment after each test"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_get_personal_resources(self):
        """Test getting personal resources list"""
        response = self.client.get('/api/v1/personal-resources/',
            headers={'Authorization': f'Bearer {self.student_token}'})

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue('data' in data)
        self.assertEqual(len(data['data']), 1)
        self.assertEqual(data['data'][0]['name'], 'Lecture Notes - CS101')

    def test_get_resource_files(self):
        """Test getting files for a specific resource"""
        response = self.client.get(
            f'/api/v1/personal-resources/{self.resource.id}/files',
            headers={'Authorization': f'Bearer {self.student_token}'}
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['name'], 'Week 1 Notes.txt')
        self.assertEqual(data[1]['name'], 'Week 2 Summary.txt')

    def test_create_personal_resource(self):
        """Test creating a new personal resource"""
        response = self.client.post('/api/v1/personal-resources/',
            headers={'Authorization': f'Bearer {self.student_token}'},
            json={
                'course_id': self.course.id,
                'name': 'Study Materials - CS101',
                'description': 'Collection of reference materials and links'
            })
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['data']['name'], 'Study Materials - CS101')

    def test_update_resource_file(self):
        """Test updating a file's content"""
        file = self.files[0]  # Get the first file
        new_content = 'Updated content for Week 1'
        
        response = self.client.put(
            f'/api/v1/personal-resources/{self.resource.id}/files/{file.id}',
            json={'content': new_content},
            headers={'Authorization': f'Bearer {self.student_token}'}
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['content'], new_content)

if __name__ == '__main__':
    unittest.main()