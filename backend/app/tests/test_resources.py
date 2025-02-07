import unittest
import json
import os
from io import BytesIO
from datetime import datetime
from app import create_app, db
from app.models.user import User
from app.models.course import Course
from app.models.resource import Resource

class ResourceTestCase(unittest.TestCase):
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

    def test_create_text_resource(self):
        """Test creating a text resource"""
        # Test successful creation
        response = self.client.post(f'/api/v1/courses/{self.course.id}/resources',
            headers={'Authorization': f'Bearer {self.teacher_token}'},
            data={
                'title': 'Test Resource',
                'description': 'Test Description',
                'type': 'text',
                'content': 'Test content'
            })
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['resource']['title'], 'Test Resource')
        self.assertEqual(data['resource']['type'], 'text')
        self.assertEqual(data['resource']['content'], 'Test content')

        # Test missing title
        response = self.client.post(f'/api/v1/courses/{self.course.id}/resources',
            headers={'Authorization': f'Bearer {self.teacher_token}'},
            data={
                'description': 'Test Description',
                'type': 'text',
                'content': 'Test content'
            })
        
        self.assertEqual(response.status_code, 400)

        # Test unauthorized user
        response = self.client.post(f'/api/v1/courses/{self.course.id}/resources',
            headers={'Authorization': f'Bearer {self.student_token}'},
            data={
                'title': 'Test Resource',
                'type': 'text',
                'content': 'Test content'
            })
        
        self.assertEqual(response.status_code, 403)

    def test_create_file_resource(self):
        """Test creating a file resource"""
        # Create a test file
        file_content = b'Test file content'
        file = (BytesIO(file_content), 'test.txt')

        # Test successful file upload
        response = self.client.post(f'/api/v1/courses/{self.course.id}/resources',
            headers={'Authorization': f'Bearer {self.teacher_token}'},
            data={
                'title': 'Test File',
                'description': 'Test Description',
                'file': file
            },
            content_type='multipart/form-data')
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['resource']['title'], 'Test File')
        self.assertEqual(data['resource']['type'], 'file')
        self.assertIsNotNone(data['resource']['file_path'])

    def test_get_resources(self):
        """Test getting course resources"""
        # Create test resources
        resource1 = Resource(
            title='Resource 1',
            description='Description 1',
            type='text',
            content='Content 1',
            course_id=self.course.id,
            created_by_id=self.teacher.id
        )
        resource2 = Resource(
            title='Resource 2',
            description='Description 2',
            type='text',
            content='Content 2',
            course_id=self.course.id,
            created_by_id=self.teacher.id,
            is_public=False
        )
        db.session.add_all([resource1, resource2])
        db.session.commit()

        # Test teacher view (all resources)
        response = self.client.get(f'/api/v1/courses/{self.course.id}/resources',
            headers={'Authorization': f'Bearer {self.teacher_token}'})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data['resources']), 2)

        # Test student view (only public resources)
        response = self.client.get(f'/api/v1/courses/{self.course.id}/resources',
            headers={'Authorization': f'Bearer {self.student_token}'})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data['resources']), 1)

    def test_get_resource(self):
        """Test getting a specific resource"""
        # Create test resource
        resource = Resource(
            title='Test Resource',
            description='Test Description',
            type='text',
            content='Test content',
            course_id=self.course.id,
            created_by_id=self.teacher.id
        )
        db.session.add(resource)
        db.session.commit()

        # Test successful retrieval
        response = self.client.get(f'/api/v1/resources/{resource.id}',
            headers={'Authorization': f'Bearer {self.teacher_token}'})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['resource']['title'], 'Test Resource')

        # Test non-existent resource
        response = self.client.get('/api/v1/resources/999',
            headers={'Authorization': f'Bearer {self.teacher_token}'})
        
        self.assertEqual(response.status_code, 404)

    def test_update_resource(self):
        """Test updating a resource"""
        # Create test resource
        resource = Resource(
            title='Test Resource',
            description='Test Description',
            type='text',
            content='Test content',
            course_id=self.course.id,
            created_by_id=self.teacher.id
        )
        db.session.add(resource)
        db.session.commit()

        # Test successful update
        response = self.client.put(f'/api/v1/resources/{resource.id}',
            headers={'Authorization': f'Bearer {self.teacher_token}'},
            data={
                'title': 'Updated Resource',
                'description': 'Updated Description',
                'content': 'Updated content'
            })
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['resource']['title'], 'Updated Resource')
        self.assertEqual(data['resource']['content'], 'Updated content')

        # Test unauthorized update
        response = self.client.put(f'/api/v1/resources/{resource.id}',
            headers={'Authorization': f'Bearer {self.student_token}'},
            data={
                'title': 'Unauthorized Update'
            })
        
        self.assertEqual(response.status_code, 403)

    def test_delete_resource(self):
        """Test deleting a resource"""
        # Create test resource
        resource = Resource(
            title='Test Resource',
            description='Test Description',
            type='text',
            content='Test content',
            course_id=self.course.id,
            created_by_id=self.teacher.id
        )
        db.session.add(resource)
        db.session.commit()

        # Test unauthorized deletion
        response = self.client.delete(f'/api/v1/resources/{resource.id}',
            headers={'Authorization': f'Bearer {self.student_token}'})
        
        self.assertEqual(response.status_code, 403)

        # Test successful deletion
        response = self.client.delete(f'/api/v1/resources/{resource.id}',
            headers={'Authorization': f'Bearer {self.teacher_token}'})
        
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(Resource.query.get(resource.id))

    def test_download_resource(self):
        """Test downloading a resource file"""
        # Create a test file resource
        file_content = b'Test file content'
        file = (BytesIO(file_content), 'test.txt')

        response = self.client.post(f'/api/v1/courses/{self.course.id}/resources',
            headers={'Authorization': f'Bearer {self.teacher_token}'},
            data={
                'title': 'Test File',
                'description': 'Test Description',
                'file': file
            },
            content_type='multipart/form-data')
        
        resource_id = json.loads(response.data)['resource']['id']

        # Test successful download
        response = self.client.get(f'/api/v1/resources/{resource_id}/download',
            headers={'Authorization': f'Bearer {self.teacher_token}'})
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, file_content)

        # Test downloading non-file resource
        text_resource = Resource(
            title='Text Resource',
            type='text',
            content='Test content',
            course_id=self.course.id,
            created_by_id=self.teacher.id
        )
        db.session.add(text_resource)
        db.session.commit()

        response = self.client.get(f'/api/v1/resources/{text_resource.id}/download',
            headers={'Authorization': f'Bearer {self.teacher_token}'})
        
        self.assertEqual(response.status_code, 404)

if __name__ == '__main__':
    unittest.main() 