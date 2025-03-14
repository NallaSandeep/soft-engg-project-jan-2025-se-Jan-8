import unittest
from flask import Flask, json
from flask_jwt_extended import create_access_token, JWTManager
from app.models.user import User  # Absolute import
from app.api.v1.users import users_bp  # Absolute import
from app import create_app, db


class UserTestCase(unittest.TestCase):
    def setUp(self):
        """Set up test environment before each test"""
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.app.register_blueprint(users_bp)
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
        # Get tokens for each user
        self.admin_token = self._get_token('admin@test.com','password123')
        self.teacher_token = self._get_token('teacher@test.com', 'password123')
        self.student_token = self._get_token('student@test.com','password123')
        # self.admin_token = self._get_token('admin_test', 'password123')
        # self.teacher_token = self._get_token('teacher_test', 'password123')
        # self.student_token = self._get_token('student_test', 'password123')
    
    def tearDown(self):
        """Clean up test environment after each test"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

     

    # auth login test
    def _get_token(self, email, password):
   
        response = self.client.post('/api/v1/auth/login', json={
            # 'username': username,
            'email':email,
            'password': password
        })
        data = json.loads(response.data)
        
        # Check if 'access_token' is nested inside 'data'
        if 'data' in data and 'access_token' in data['data']:
            return data['data']['access_token']
        else:
            raise ValueError(f"Login failed: {data}")
        headers = {'Authorization': f'Bearer {self.admin_token}'}
        response = self.client.get('/', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn('users', response.json)

    def test_health_check(self):
        """Test the health check endpoint."""
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {'status': 'ok', 'message': 'Users API is running'})

    def test_get_current_user(self):
        """Test getting the current user's details."""
        headers = {'Authorization': f'Bearer {self.student_token}'}
        response = self.client.get('/me', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn('user', response.json)

    def test_update_current_user(self):
        """Test updating the current user's details."""
        headers = {'Authorization': f'Bearer {self.student_token}'}
        update_data = {'first_name': 'Updated', 'last_name': 'User'}
        response = self.client.put('/me', json=update_data, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['msg'], 'User updated successfully')
        self.assertEqual(response.json['user']['first_name'], 'Updated')
        self.assertEqual(response.json['user']['last_name'], 'User')

    def test_get_users(self):
        """Test getting all users."""
        headers = {'Authorization': f'Bearer {self.admin_token}'}
        response = self.client.get('/', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn('users', response.json)

    def test_get_user(self):
        """Test getting a specific user's details."""
        headers = {'Authorization': f'Bearer {self.admin_token}'}
        response = self.client.get(f'/{self.student.id}', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn('user', response.json)



    def test_activate_user(self):
        """Test activating a user."""
        headers = {'Authorization': f'Bearer {self.admin_token}'}
        response = self.client.post(f'/{self.student.id}/activate', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['msg'], 'User activated successfully')

    def test_deactivate_user(self):
        """Test deactivating a user."""
        headers = {'Authorization': f'Bearer {self.admin_token}'}
        response = self.client.post(f'/{self.student.id}/deactivate', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['msg'], 'User deactivated successfully')

    # def test_deactivate_last_admin(self):
    #     """Test deactivating the last admin user."""
    #     # Make the test user an admin
    #     with self.app.app_context():
    #         self.user.role = 'admin'
    #         db.session.commit()
        
    #     headers = {'Authorization': f'Bearer {self.admin_token}'}
    #     response = self.client.post(f'/{self.student.id}/deactivate', headers=headers)
    #     self.assertEqual(response.status_code, 403)
    #     self.assertEqual(response.json['msg'], 'Cannot deactivate the last admin user')

if __name__ == '__main__':
    unittest.main()
