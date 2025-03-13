import unittest
import json
from datetime import datetime, timedelta
from app import create_app, db
from app.models.user import User
from app.models.course import Course, CourseEnrollment
from config import config
import logging

logger = logging.getLogger(__name__)

# command to run test case
#  pytest --disable-warnings -n 1 .\app\tests\test_questions.py
class QuestionTestCase(unittest.TestCase):
    def setUp(self):
        """Set up test environment before each test"""
        self.app = create_app(config['testing'])
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

        self.ta = User(
            username='ta_test',
            email='ta@test.com',
            password='password123',
            role='ta',
            first_name='TA',
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
        # self.ta_token = self._get_token('ta@test.com', 'password123')
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
    
    def create_question(self, question_data):
        """Helper function to create a question."""
        response = self.client.post(
            '/api/v1/question-bank/questions',
            headers={'Authorization': f'Bearer {self.admin_token}'},
            json=question_data
        )
        return response

    ##########################
    # LISTING QUESTIONS
    ##########################

    def test_list_questions_with_filters(self):
        """Test listing questions with filters (course_id, week_id, lecture_id, status, type, search)."""
        # Create test questions
        question_data_1 = {
            "title": "MCQ Question 1",
            "content": "What is 2+2?",
            "type": "MCQ",
            "correct_answer": "4",
            "points": 1,
            "explanation": "Simple arithmetic!",
            "status": "active",
            "course_id": 1,
            "week_id": 1,
            "lecture_id": 1
        }
        question_data_2 = {
            "title": "Numeric Question 1",
            "content": "What is 3+3?",
            "type": "NUMERIC",
            "correct_answer": "6",
            "points": 2,
            "explanation": "Still simple arithmetic!",
            "status": "draft",
            "course_id": 1,
            "week_id": 1,
            "lecture_id": 1
        }
        self.create_question(question_data_1)
        self.create_question(question_data_2)

        # Test filters
        response = self.client.get(
            '/api/v1/question-bank/questions?course_id=1&week_id=1&lecture_id=1&status=active&type=MCQ&search=arithmetic',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data['questions']), 1)
        self.assertEqual(data['questions'][0]['title'], "MCQ Question 1")

    def test_list_questions_invalid_filters(self):
        """Test listing questions with invalid filters."""
        response = self.client.get(
            '/api/v1/question-bank/questions?status=invalid&type=invalid',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        self.assertEqual(response.status_code, 400)

    ##########################
    # CREATING QUESTIONS
    ##########################

    def test_create_question_mc(self):
        """Test creating an MCQ question."""
        question_data = {
            "title": "MCQ Question",
            "content": "What is 2+2?",
            "type": "MCQ",
            "correct_answer": "4",
            "points": 1,
            "explanation": "Simple arithmetic!",
            "status": "active"
        }
        response = self.create_question(question_data)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['type'], "MCQ")

    def test_create_question_ms(self):
        """Test creating an MSQ (Multiple Select) question."""
        question_data = {
            "title": "MSQ Question",
            "content": "Which are prime numbers?",
            "type": "MSQ",
            "correct_answer": ["2", "3", "5"],
            "points": 2,
            "explanation": "Prime numbers are numbers greater than 1.",
            "status": "active"
        }
        response = self.create_question(question_data)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['type'], "MSQ")

    def test_create_question_numeric(self):
        """Test creating a numeric question."""
        question_data = {
            "title": "Numeric Question",
            "content": "What is 3+3?",
            "type": "NUMERIC",
            "correct_answer": "6",
            "points": 1,
            "explanation": "Still simple arithmetic!",
            "status": "active"
        }
        response = self.create_question(question_data)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['type'], "NUMERIC")

    def test_create_question_bad_request(self):
        """Test creating a question with missing required fields."""
        question_data = {
            "title": "Incomplete Question",
            "content": "What is 2+2?"
        }
        response = self.create_question(question_data)
        self.assertEqual(response.status_code, 400)

    ##########################
    # UPDATING QUESTIONS
    ##########################

    def test_update_question_success(self):
        """Test updating a question successfully."""
        # Create a question first
        question_data = {
            "title": "Sample MCQ question",
            "content": "What is 2+2?",
            "type": "MCQ",
            "correct_answer": "4",
            "points": 1,
            "explanation": "Simple arithmetic!",
            "status": "active"
        }
        create_response = self.create_question(question_data)
        question_id = json.loads(create_response.data)['id']

        # Update the question
        updated_data = {
            "title": "Updated MCQ question",
            "content": "What is 3+3?",
            "type": "MCQ",
            "correct_answer": "6",
            "points": 2,
            "explanation": "Still simple arithmetic!",
            "status": "active"
        }
        response = self.client.put(
            f'/api/v1/question-bank/questions/{question_id}',
            headers={'Authorization': f'Bearer {self.admin_token}'},
            json=updated_data
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['title'], updated_data['title'])

    def test_update_question_bad_request(self):
        """Test updating a question with invalid data."""
        # Create a question first
        question_data = {
            "title": "Sample MCQ question",
            "content": "What is 2+2?",
            "type": "MCQ",
            "correct_answer": "4",
            "points": 1,
            "explanation": "Simple arithmetic!",
            "status": "active"
        }
        create_response = self.create_question(question_data)
        question_id = json.loads(create_response.data)['id']

        # Update with invalid data
        updated_data = {
            "type": "INVALID_TYPE"
        }
        response = self.client.put(
            f'/api/v1/question-bank/questions/{question_id}',
            headers={'Authorization': f'Bearer {self.admin_token}'},
            json=updated_data
        )
        self.assertEqual(response.status_code, 400)

    def test_update_question_not_found(self):
        """Test updating a non-existent question."""
        updated_data = {
            "title": "Updated MCQ question",
            "content": "What is 3+3?",
            "type": "MCQ",
            "correct_answer": "6",
            "points": 2,
            "explanation": "Still simple arithmetic!",
            "status": "active"
        }
        response = self.client.put(
            '/api/v1/question-bank/questions/999',
            headers={'Authorization': f'Bearer {self.admin_token}'},
            json=updated_data
        )
        self.assertEqual(response.status_code, 404)

    ##########################
    # RETRIEVING QUESTIONS
    ##########################

    def test_get_question_valid(self):
        """Test retrieving a valid question."""
        # Create a question first
        question_data = {
            "title": "Sample MCQ question",
            "content": "What is 2+2?",
            "type": "MCQ",
            "correct_answer": "4",
            "points": 1,
            "explanation": "Simple arithmetic!",
            "status": "active"
        }
        create_response = self.create_question(question_data)
        question_id = json.loads(create_response.data)['id']

        # Retrieve the question
        response = self.client.get(
            f'/api/v1/question-bank/questions/{question_id}',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['id'], question_id)

    def test_get_question_not_found(self):
        """Test retrieving a non-existent question."""
        response = self.client.get(
            '/api/v1/question-bank/questions/999',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        self.assertEqual(response.status_code, 404)

    ##########################
    # DELETING QUESTIONS
    ##########################

    def test_delete_question_success(self):
        """Test deleting a question successfully."""
        # Create a question first
        question_data = {
            "title": "Sample MCQ question",
            "content": "What is 2+2?",
            "type": "MCQ",
            "correct_answer": "4",
            "points": 1,
            "explanation": "Simple arithmetic!",
            "status": "active"
        }
        create_response = self.create_question(question_data)
        question_id = json.loads(create_response.data)['id']

        # Delete the question
        response = self.client.delete(
            f'/api/v1/question-bank/questions/{question_id}',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        self.assertEqual(response.status_code, 200)

    def test_delete_question_not_found(self):
        """Test deleting a non-existent question."""
        response = self.client.delete(
            '/api/v1/question-bank/questions/999',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        self.assertEqual(response.status_code, 404)

if __name__ == '__main__':
    unittest.main()