import unittest
import json
from datetime import datetime, timedelta
from app import create_app, db
from app.models.user import User
from app.models.course import Course
from app.models.ai_learning import (
    LearningProfile, StudySession, LearningRecommendation, ProgressAnalytics
)

class AILearningTestCase(unittest.TestCase):
    def setUp(self):
        """Set up test environment before each test"""
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Create test users
        self.student = User(
            username='student_test',
            email='student@test.com',
            password='password123',
            role='student',
            first_name='Student',
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

        db.session.add_all([self.student, self.teacher])
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

        # Get tokens
        self.student_token = self._get_token('student_test', 'password123')
        self.teacher_token = self._get_token('teacher_test', 'password123')

    def tearDown(self):
        """Clean up test environment after each test"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def _get_token(self, username, password):
        """Helper method to get JWT token"""
        response = self.client.post('/api/v1/auth/login', json={
            'username': username,
            'password': password
        })
        return json.loads(response.data)['access_token']

    def test_get_learning_profile(self):
        """Test getting learning profile"""
        # Test initial profile creation
        response = self.client.get('/api/v1/ai-learning/profile',
            headers={'Authorization': f'Bearer {self.student_token}'})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('profile', data)
        self.assertEqual(data['profile']['user_id'], self.student.id)

        # Test existing profile retrieval
        profile = LearningProfile(
            user_id=self.student.id,
            preferred_learning_style='visual',
            difficulty_preference='moderate',
            study_time_preference=60
        )
        db.session.add(profile)
        db.session.commit()

        response = self.client.get('/api/v1/ai-learning/profile',
            headers={'Authorization': f'Bearer {self.student_token}'})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['profile']['preferred_learning_style'], 'visual')
        self.assertEqual(data['profile']['study_time_preference'], 60)

    def test_update_learning_profile(self):
        """Test updating learning profile"""
        # Create initial profile
        profile = LearningProfile(user_id=self.student.id)
        db.session.add(profile)
        db.session.commit()

        # Test successful update
        response = self.client.put('/api/v1/ai-learning/profile',
            headers={'Authorization': f'Bearer {self.student_token}'},
            json={
                'preferred_learning_style': 'auditory',
                'difficulty_preference': 'challenging',
                'study_time_preference': 90,
                'topic_interests': ['python', 'algorithms'],
                'peak_study_hours': [9, 14, 20]
            })
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['profile']['preferred_learning_style'], 'auditory')
        self.assertEqual(data['profile']['study_time_preference'], 90)
        self.assertIn('python', data['profile']['topic_interests'])

    def test_get_recommendations(self):
        """Test getting learning recommendations"""
        # Create learning profile and study sessions
        profile = LearningProfile(user_id=self.student.id)
        db.session.add(profile)
        
        session1 = StudySession(
            profile_id=profile.id,
            course_id=self.course.id,
            topic='Python Basics',
            resource_type='resource',
            resource_id=1,
            score=65,
            completion_status='completed'
        )
        session2 = StudySession(
            profile_id=profile.id,
            course_id=self.course.id,
            topic='Algorithms',
            resource_type='assignment',
            resource_id=2,
            score=90,
            completion_status='completed'
        )
        db.session.add_all([session1, session2])
        db.session.commit()

        # Test getting recommendations
        response = self.client.get(f'/api/v1/ai-learning/courses/{self.course.id}/recommendations',
            headers={'Authorization': f'Bearer {self.student_token}'})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('recommendations', data)
        self.assertIsInstance(data['recommendations'], list)

    def test_update_recommendation_status(self):
        """Test updating recommendation status"""
        # Create learning profile and recommendation
        profile = LearningProfile(user_id=self.student.id)
        db.session.add(profile)
        db.session.commit()

        recommendation = LearningRecommendation(
            profile_id=profile.id,
            course_id=self.course.id,
            type='resource',
            priority=4,
            title='Review Python Basics',
            status='pending'
        )
        db.session.add(recommendation)
        db.session.commit()

        # Test updating status
        response = self.client.put(f'/api/v1/ai-learning/recommendations/{recommendation.id}/status',
            headers={'Authorization': f'Bearer {self.student_token}'},
            json={
                'status': 'completed',
                'effectiveness_rating': 4
            })
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['recommendation']['status'], 'completed')
        self.assertEqual(data['recommendation']['effectiveness_rating'], 4)

        # Test invalid status
        response = self.client.put(f'/api/v1/ai-learning/recommendations/{recommendation.id}/status',
            headers={'Authorization': f'Bearer {self.student_token}'},
            json={
                'status': 'invalid'
            })
        
        self.assertEqual(response.status_code, 400)

    def test_get_analytics(self):
        """Test getting learning analytics"""
        # Create learning profile and study sessions
        profile = LearningProfile(user_id=self.student.id)
        db.session.add(profile)
        db.session.commit()

        # Create study sessions over the past month
        start_date = datetime.utcnow() - timedelta(days=25)
        for i in range(10):
            session = StudySession(
                profile_id=profile.id,
                course_id=self.course.id,
                start_time=start_date + timedelta(days=i),
                end_time=start_date + timedelta(days=i, hours=2),
                duration=120,
                topic=f'Topic {i+1}',
                completion_status='completed',
                score=75 + i,
                focus_score=0.8,
                time_on_task=100
            )
            db.session.add(session)
        db.session.commit()

        # Test getting analytics
        response = self.client.get(f'/api/v1/ai-learning/courses/{self.course.id}/analytics',
            headers={'Authorization': f'Bearer {self.student_token}'})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('analytics', data)
        self.assertIsNotNone(data['analytics']['average_score'])
        self.assertIsNotNone(data['analytics']['study_consistency'])
        self.assertIsNotNone(data['analytics']['predicted_performance'])

    def test_study_session_management(self):
        """Test study session creation and updates"""
        # Create learning profile
        profile = LearningProfile(user_id=self.student.id)
        db.session.add(profile)
        db.session.commit()

        # Test starting a session
        response = self.client.post(f'/api/v1/ai-learning/courses/{self.course.id}/study-sessions',
            headers={'Authorization': f'Bearer {self.student_token}'},
            json={
                'resource_type': 'assignment',
                'resource_id': 1
            })
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        session_id = data['session']['id']
        self.assertIsNone(data['session']['end_time'])

        # Test ending the session
        response = self.client.put(f'/api/v1/ai-learning/study-sessions/{session_id}',
            headers={'Authorization': f'Bearer {self.student_token}'},
            json={
                'completion_status': 'completed',
                'focus_score': 0.85,
                'difficulty_rating': 3,
                'comprehension_rating': 4,
                'notes': 'Good study session'
            })
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['session']['completion_status'], 'completed')
        self.assertEqual(data['session']['focus_score'], 0.85)
        self.assertIsNotNone(data['session']['end_time'])

    def test_get_study_sessions(self):
        """Test getting study sessions"""
        # Create learning profile and sessions
        profile = LearningProfile(user_id=self.student.id)
        db.session.add(profile)
        db.session.commit()

        # Create multiple sessions
        for i in range(5):
            session = StudySession(
                profile_id=profile.id,
                course_id=self.course.id,
                start_time=datetime.utcnow() - timedelta(days=i),
                end_time=datetime.utcnow() - timedelta(days=i, hours=-2),
                duration=120,
                topic=f'Topic {i+1}',
                completion_status='completed'
            )
            db.session.add(session)
        db.session.commit()

        # Test getting sessions
        response = self.client.get(f'/api/v1/ai-learning/courses/{self.course.id}/study-sessions',
            headers={'Authorization': f'Bearer {self.student_token}'})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data['sessions']), 5)
        self.assertEqual(data['sessions'][0]['topic'], 'Topic 1')  # Most recent first

if __name__ == '__main__':
    unittest.main() 