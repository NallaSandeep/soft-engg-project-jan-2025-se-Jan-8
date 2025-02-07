from flask import Blueprint, jsonify
from app.models import User, Course, Assignment, Question, AssignmentSubmission
from app.decorators import admin_or_ta_required
from sqlalchemy import func
from datetime import datetime

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard/stats', methods=['GET'])
@admin_or_ta_required
def get_dashboard_stats():
    """Get statistics for admin dashboard."""
    try:
        # Get total counts
        total_courses = Course.query.filter_by(is_active=True).count()
        total_students = User.query.filter_by(role='student', is_active=True).count()
        total_assignments = Assignment.query.filter_by(is_published=True).count()
        total_questions = Question.query.filter_by(status='active').count()

        # Get recent courses (last 5)
        recent_courses = Course.query.order_by(Course.created_at.desc()).limit(5).all()
        
        # Get recent assignments (last 5)
        recent_assignments = Assignment.query.order_by(Assignment.created_at.desc()).limit(5).all()

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