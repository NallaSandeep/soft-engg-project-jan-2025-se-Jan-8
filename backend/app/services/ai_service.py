import json
from datetime import datetime, timedelta
from app import db
from app.models.ai_learning import (
    LearningProfile, StudySession, LearningRecommendation, ProgressAnalytics
)
from app.models.assignment import Assignment, Submission
from app.models.resource import Resource

class AILearningService:
    """Service for AI-powered learning assistance features"""

    @staticmethod
    def analyze_learning_style(user_id, course_id):
        """Analyze user's learning style based on their interactions"""
        # Get user's study sessions and interactions
        profile = LearningProfile.query.filter_by(user_id=user_id).first()
        if not profile:
            return None

        sessions = StudySession.query.filter_by(
            profile_id=profile.id,
            course_id=course_id
        ).all()

        # Analyze resource preferences
        resource_preferences = {}
        for session in sessions:
            if session.resource_type not in resource_preferences:
                resource_preferences[session.resource_type] = {
                    'count': 0,
                    'total_time': 0,
                    'avg_focus': 0,
                    'avg_comprehension': 0
                }
            
            stats = resource_preferences[session.resource_type]
            stats['count'] += 1
            stats['total_time'] += session.time_on_task
            stats['avg_focus'] = (stats['avg_focus'] * (stats['count'] - 1) + session.focus_score) / stats['count']
            stats['avg_comprehension'] = (stats['avg_comprehension'] * (stats['count'] - 1) + session.comprehension_rating) / stats['count']

        # Determine primary learning style
        learning_style = 'reading'  # Default
        max_effectiveness = 0

        for resource_type, stats in resource_preferences.items():
            effectiveness = (
                stats['avg_focus'] * 0.4 +
                stats['avg_comprehension'] * 0.4 +
                (stats['total_time'] / stats['count']) * 0.2
            )
            if effectiveness > max_effectiveness:
                max_effectiveness = effectiveness
                if resource_type in ['video', 'interactive']:
                    learning_style = 'visual'
                elif resource_type in ['audio', 'lecture']:
                    learning_style = 'auditory'
                elif resource_type in ['practice', 'lab']:
                    learning_style = 'kinesthetic'

        return learning_style

    @staticmethod
    def generate_recommendations(user_id, course_id):
        """Generate personalized learning recommendations"""
        profile = LearningProfile.query.filter_by(user_id=user_id).first()
        if not profile:
            return []

        # Get recent study sessions and performance
        recent_sessions = StudySession.query.filter_by(
            profile_id=profile.id,
            course_id=course_id
        ).order_by(StudySession.created_at.desc()).limit(10).all()

        # Get assignments and submissions
        assignments = Assignment.query.filter_by(
            course_id=course_id,
            is_active=True,
            is_published=True
        ).all()

        # Analyze performance and patterns
        weak_topics = set()
        strong_topics = set()
        for session in recent_sessions:
            if session.score:
                if session.score < 70:
                    weak_topics.add(session.topic)
                elif session.score > 85:
                    strong_topics.add(session.topic)

        recommendations = []

        # Recommend resources for weak topics
        for topic in weak_topics:
            resources = Resource.query.filter_by(
                course_id=course_id,
                type=profile.preferred_learning_style
            ).filter(Resource.title.ilike(f'%{topic}%')).all()

            if resources:
                recommendation = LearningRecommendation(
                    profile_id=profile.id,
                    course_id=course_id,
                    type='resource',
                    priority=4,
                    title=f'Review {topic}',
                    description=f'Based on your recent performance, we recommend reviewing {topic}',
                    reason=f'Your score in {topic} was below average. These resources match your learning style.',
                    resource_type='resource',
                    resource_id=resources[0].id,
                    suggested_duration=60,
                    status='pending'
                )
                recommendations.append(recommendation)

        # Recommend upcoming assignments
        upcoming_assignments = [a for a in assignments if a.start_date <= datetime.utcnow() <= a.due_date]
        for assignment in upcoming_assignments:
            # Check if already submitted
            submission = Submission.query.filter_by(
                assignment_id=assignment.id,
                submitted_by_id=user_id
            ).first()

            if not submission:
                # Calculate recommended start time based on due date and estimated duration
                time_needed = assignment.max_score * 2  # Rough estimate: 2 minutes per point
                deadline = assignment.due_date
                suggested_start = deadline - timedelta(minutes=time_needed)

                recommendation = LearningRecommendation(
                    profile_id=profile.id,
                    course_id=course_id,
                    type='assignment',
                    priority=5,
                    title=f'Start Assignment: {assignment.title}',
                    description=f'This assignment is due on {deadline.strftime("%Y-%m-%d %H:%M")}',
                    reason='Starting early will help you manage your time better and achieve a better score.',
                    resource_type='assignment',
                    resource_id=assignment.id,
                    suggested_duration=time_needed,
                    suggested_start_time=suggested_start,
                    deadline=deadline,
                    status='pending'
                )
                recommendations.append(recommendation)

        # Generate study schedule recommendations
        if profile.study_time_preference and profile.peak_study_hours:
            peak_hours = json.loads(profile.peak_study_hours)
            for hour in peak_hours:
                # Find resources or assignments that match the time slot
                recommendation = LearningRecommendation(
                    profile_id=profile.id,
                    course_id=course_id,
                    type='study_schedule',
                    priority=3,
                    title='Recommended Study Time',
                    description=f'Schedule a study session at {hour}:00',
                    reason='This time slot matches your peak productivity hours.',
                    suggested_duration=profile.study_time_preference,
                    status='pending'
                )
                recommendations.append(recommendation)

        return recommendations

    @staticmethod
    def update_analytics(user_id, course_id):
        """Update learning analytics for a user in a course"""
        profile = LearningProfile.query.filter_by(user_id=user_id).first()
        if not profile:
            return None

        # Define analysis period
        period_end = datetime.utcnow()
        period_start = period_end - timedelta(days=30)

        # Get study sessions in the period
        sessions = StudySession.query.filter(
            StudySession.profile_id == profile.id,
            StudySession.course_id == course_id,
            StudySession.created_at.between(period_start, period_end)
        ).all()

        if not sessions:
            return None

        # Calculate metrics
        total_time = sum(s.duration for s in sessions if s.duration)
        productive_time = sum(s.time_on_task for s in sessions if s.time_on_task)
        avg_session_length = total_time / len(sessions) if sessions else 0

        # Calculate scores and completion rates
        completed_sessions = [s for s in sessions if s.completion_status == 'completed']
        completion_rate = len(completed_sessions) / len(sessions) if sessions else 0
        
        scores = [s.score for s in sessions if s.score is not None]
        avg_score = sum(scores) / len(scores) if scores else None

        # Analyze engagement
        engagement_scores = [s.focus_score for s in sessions if s.focus_score is not None]
        avg_engagement = sum(engagement_scores) / len(engagement_scores) if engagement_scores else None

        # Calculate study consistency
        study_days = len(set(s.created_at.date() for s in sessions))
        total_days = (period_end - period_start).days
        consistency = study_days / total_days if total_days > 0 else 0

        # Collect topics and identify strengths/weaknesses
        topics = {}
        for session in sessions:
            if session.topic:
                if session.topic not in topics:
                    topics[session.topic] = {'scores': [], 'time': 0}
                topics[session.topic]['scores'].append(session.score if session.score else 0)
                topics[session.topic]['time'] += session.duration if session.duration else 0

        strengths = []
        areas_for_improvement = []
        for topic, data in topics.items():
            avg_topic_score = sum(data['scores']) / len(data['scores'])
            if avg_topic_score >= 85:
                strengths.append(topic)
            elif avg_topic_score <= 70:
                areas_for_improvement.append(topic)

        # Predict performance and risk level
        predicted_performance = avg_score if avg_score else 0
        predicted_performance *= (completion_rate * 0.3 + consistency * 0.3 + (avg_engagement or 0) * 0.4)

        risk_level = 'low'
        if predicted_performance < 60:
            risk_level = 'high'
        elif predicted_performance < 75:
            risk_level = 'moderate'

        # Generate recommended actions
        recommended_actions = []
        if completion_rate < 0.8:
            recommended_actions.append('Improve assignment completion rate')
        if consistency < 0.5:
            recommended_actions.append('Establish a more regular study schedule')
        if avg_engagement and avg_engagement < 0.7:
            recommended_actions.append('Work on maintaining focus during study sessions')
        if areas_for_improvement:
            recommended_actions.append(f'Focus on improving understanding of: {", ".join(areas_for_improvement)}')

        # Create or update analytics
        analytics = ProgressAnalytics.query.filter_by(
            profile_id=profile.id,
            course_id=course_id
        ).first()

        if not analytics:
            analytics = ProgressAnalytics(
                profile_id=profile.id,
                course_id=course_id
            )

        analytics.period_start = period_start
        analytics.period_end = period_end
        analytics.average_score = avg_score
        analytics.completion_rate = completion_rate
        analytics.engagement_level = avg_engagement
        analytics.study_consistency = consistency
        analytics.total_study_time = total_time
        analytics.productive_time = productive_time
        analytics.average_session_length = avg_session_length
        analytics.topics_covered = json.dumps(list(topics.keys()))
        analytics.strengths = json.dumps(strengths)
        analytics.areas_for_improvement = json.dumps(areas_for_improvement)
        analytics.predicted_performance = predicted_performance
        analytics.risk_level = risk_level
        analytics.recommended_actions = json.dumps(recommended_actions)

        db.session.add(analytics)
        db.session.commit()

        return analytics

    @staticmethod
    def start_study_session(user_id, course_id, resource_type, resource_id):
        """Start a new study session"""
        profile = LearningProfile.query.filter_by(user_id=user_id).first()
        if not profile:
            return None

        # Check for any active sessions
        active_session = StudySession.query.filter_by(
            profile_id=profile.id,
            end_time=None
        ).first()

        if active_session:
            # End the previous session
            active_session.end_time = datetime.utcnow()
            active_session.duration = int((active_session.end_time - active_session.start_time).total_seconds() / 60)
            active_session.completion_status = 'interrupted'

        # Create new session
        session = StudySession(
            profile_id=profile.id,
            course_id=course_id,
            start_time=datetime.utcnow(),
            resource_type=resource_type,
            resource_id=resource_id
        )

        # Get topic from resource
        if resource_type == 'assignment':
            assignment = Assignment.query.get(resource_id)
            if assignment:
                session.topic = assignment.title
        elif resource_type == 'resource':
            resource = Resource.query.get(resource_id)
            if resource:
                session.topic = resource.title

        db.session.add(session)
        db.session.commit()

        return session

    @staticmethod
    def end_study_session(session_id, completion_status, focus_score=None, 
                         difficulty_rating=None, comprehension_rating=None, notes=None):
        """End a study session with feedback"""
        session = StudySession.query.get(session_id)
        if not session or session.end_time:
            return None

        session.end_time = datetime.utcnow()
        session.duration = int((session.end_time - session.start_time).total_seconds() / 60)
        session.completion_status = completion_status
        session.focus_score = focus_score
        session.difficulty_rating = difficulty_rating
        session.comprehension_rating = comprehension_rating
        session.notes = notes

        # Calculate time on task (excluding breaks/interruptions)
        session.time_on_task = int(session.duration * (focus_score if focus_score else 0.8))

        # Update progress percentage based on completion status
        if completion_status == 'completed':
            session.progress_percentage = 100
        elif completion_status == 'interrupted':
            session.progress_percentage = 50
        else:  # abandoned
            session.progress_percentage = 25

        db.session.commit()

        # Update learning profile
        profile = session.learning_profile
        
        # Update study streak
        today = datetime.utcnow().date()
        active_days = json.loads(profile.active_days) if profile.active_days else []
        
        if str(today) not in active_days:
            active_days.append(str(today))
            active_days.sort()
            profile.active_days = json.dumps(active_days)

            # Check if streak continues
            if len(active_days) >= 2:
                last_day = datetime.strptime(active_days[-2], '%Y-%m-%d').date()
                if (today - last_day).days == 1:
                    profile.study_streak += 1
                else:
                    profile.study_streak = 1
            else:
                profile.study_streak = 1

        db.session.commit()

        return session 