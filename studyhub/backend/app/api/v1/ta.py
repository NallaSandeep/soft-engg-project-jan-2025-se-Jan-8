from flask import Blueprint, jsonify
from app.models import User, Course, Assignment, Question, AssignmentSubmission, CourseEnrollment, Week, Lecture, LectureProgress
from app.decorators import admin_or_ta_required
from sqlalchemy import func
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity

ta_bp = Blueprint('ta', __name__)

@ta_bp.route('/dashboard/stats', methods=['GET'])
@admin_or_ta_required
def get_dashboard_stats():
    """Get statistics for TA dashboard."""
    try:
        current_user = User.query.get(get_jwt_identity())
        if not current_user:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404

        # Get courses where the current user is a TA
        ta_enrollments = CourseEnrollment.query.filter_by(
            user_id=current_user.id,
            role='ta'
        ).all()
        courses = [enrollment.course for enrollment in ta_enrollments]

        # Get total counts specific to the TA's courses
        total_courses = len(courses)
        total_students = sum(
            CourseEnrollment.query.filter_by(course_id=course.id, role='student').count()
            for course in courses
        )
        
        # Get total assignments by mapping course_id with weeks and then week_id with assignments
        total_assignments = sum(
            Assignment.query.join(Week, Assignment.week_id == Week.id)
            .filter(Week.course_id == course.id, Assignment.is_published == True)
            .count()
            for course in courses
        )
        total_questions = sum(
            Question.query.filter_by(course_id=course.id, status='active').count()
            for course in courses
        )

        # Get recent courses (last 5) managed by the TA
        recent_courses = sorted(courses, key=lambda c: c.created_at, reverse=True)[:5]

        # Get recent assignments (last 5) across all courses managed by the TA
        recent_assignments = Assignment.query.join(Week, Assignment.week_id == Week.id) \
            .filter(Week.course_id.in_([course.id for course in courses])) \
            .order_by(Assignment.created_at.desc()) \
            .limit(5).all()

        # Format the response
        response = {
            'success': True,
            'data': {
                'stats': {
                    'totalCourses': total_courses,
                    'totalStudents': total_students,
                    'totalAssignments': total_assignments,
                    'totalQuestions': total_questions
                },
                'recentCourses': [{
                    'id': course.id,
                    'name': course.name,
                    'code': course.code,
                    'created_at': course.created_at.isoformat()
                } for course in recent_courses],
                'recentAssignments': [{
                    'id': assignment.id,
                    'title': assignment.title,
                    'due_date': assignment.due_date.isoformat(),
                    'is_published': assignment.is_published,
                    'week': {
                        'week_number': assignment.week.number,
                        'course': {
                            'name': assignment.week.course.name
                        }
                    } if assignment.week else None
                } for assignment in recent_assignments]
            }
        }

        return jsonify(response), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500