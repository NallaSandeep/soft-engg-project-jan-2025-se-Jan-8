from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ...models import User, Course, CourseEnrollment, Week, Lecture, Assignment, Question
from ...utils.auth import admin_required, student_or_ta_required, ta_required, roles_required
from ... import db
import json

courses_bp = Blueprint('courses', __name__)

@courses_bp.route('/', methods=['GET'])
@jwt_required()
def get_courses():
    """Get all courses based on user role"""
    try:
        current_user = User.query.get(get_jwt_identity())
        if not current_user:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404

        if current_user.role == 'admin':
            # Admin sees all courses
            courses = Course.query.all()
        elif current_user.role == 'ta':
            # TA sees courses where they are enrolled as TA
            ta_enrollments = CourseEnrollment.query.filter_by(
                user_id=current_user.id,
                role='ta'
            ).all()
            courses = [enrollment.course for enrollment in ta_enrollments]
        else:  # student
            # Students see courses they are enrolled in
            student_enrollments = CourseEnrollment.query.filter_by(
                user_id=current_user.id,
                role='student'
            ).all()
            courses = [enrollment.course for enrollment in student_enrollments]

        return jsonify({
            'success': True,
            'data': [course.to_dict() for course in courses],
            'message': 'Courses retrieved successfully'
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Failed to retrieve courses'
        }), 500

@courses_bp.route('/', methods=['POST'])
@admin_required
def create_course():
    """Create a new course (admin only)"""
    try:
        data = request.get_json()
        required_fields = ['code', 'name', 'description']
        if not all(field in data for field in required_fields):
            return jsonify({
                'success': False,
                'message': 'Missing required fields'
            }), 400

        # Check if course code already exists
        if Course.query.filter_by(code=data['code']).first():
            return jsonify({
                'success': False,
                'message': 'Course code already exists'
            }), 409

        # Parse dates if provided
        start_date = None
        end_date = None
        if 'start_date' in data:
            start_date = datetime.fromisoformat(data['start_date']).date()
        if 'end_date' in data:
            end_date = datetime.fromisoformat(data['end_date']).date()

        current_user = User.query.get(get_jwt_identity())
        course = Course(
            code=data['code'],
            name=data['name'],
            description=data['description'],
            created_by_id=current_user.id,
            start_date=start_date,
            end_date=end_date,
            max_students=data.get('max_students'),
            enrollment_type=data.get('enrollment_type', 'open')
        )

        db.session.add(course)
        db.session.commit()

        return jsonify({
            'success': True,
            'data': course.to_dict(),
            'message': 'Course created successfully'
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Failed to create course'
        }), 500

@courses_bp.route('/<int:course_id>', methods=['GET'])
@jwt_required()
def get_course(course_id):
    """Get details of a specific course"""
    try:
        course = Course.query.get(course_id)
        if not course:
            return jsonify({
                'success': False,
                'message': 'Course not found'
            }), 404

        return jsonify({
            'success': True,
            'data': course.to_dict(),
            'message': 'Course retrieved successfully'
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Failed to retrieve course'
        }), 500

@courses_bp.route('/<int:course_id>', methods=['PUT'])
@admin_required
def update_course(course_id):
    """Update course details (admin only)"""
    try:
        course = Course.query.get(course_id)
        if not course:
            return jsonify({'error': 'Course not found'}), 404

        data = request.get_json()
        
        # Update fields if provided
        if 'name' in data:
            course.name = data['name']
        if 'description' in data:
            course.description = data['description']
        if 'start_date' in data:
            course.start_date = datetime.fromisoformat(data['start_date']).date()
        if 'end_date' in data:
            course.end_date = datetime.fromisoformat(data['end_date']).date()
        if 'max_students' in data:
            course.max_students = data['max_students']
        if 'enrollment_type' in data:
            course.enrollment_type = data['enrollment_type']
        if 'is_active' in data:
            course.is_active = data['is_active']

        db.session.commit()

        return jsonify({
            'msg': 'Course updated successfully',
            'course': course.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@courses_bp.route('/<int:course_id>', methods=['DELETE'])
@admin_required
def delete_course(course_id):
    """Delete a course (admin only)"""
    try:
        course = Course.query.get(course_id)
        if not course:
            return jsonify({'error': 'Course not found'}), 404

        db.session.delete(course)
        db.session.commit()

        return jsonify({
            'msg': 'Course deleted successfully',
            'course_id': course_id
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@courses_bp.route('/<int:course_id>/enroll', methods=['POST'])
@student_or_ta_required
def enroll_in_course(course_id):
    """Enroll in a course (student/TA only)"""
    try:
        course = Course.query.get(course_id)
        if not course:
            return jsonify({'error': 'Course not found'}), 404

        current_user = User.query.get(get_jwt_identity())
        
        # Check if already enrolled
        existing_enrollment = CourseEnrollment.query.filter_by(
            course_id=course_id,
            user_id=current_user.id
        ).first()
        
        if existing_enrollment:
            return jsonify({'error': 'Already enrolled in this course'}), 409

        # Check enrollment conditions
        if not course.is_active:
            return jsonify({'error': 'Course is not active'}), 400
        
        if course.enrollment_type == 'closed':
            return jsonify({'error': 'Course enrollment is closed'}), 400
        
        if course.max_students and course.get_enrolled_count('student') >= course.max_students:
            return jsonify({'error': 'Course has reached maximum enrollment'}), 400

        # Create enrollment
        enrollment = CourseEnrollment(
            course_id=course_id,
            user_id=current_user.id,
            role='student' if current_user.role == 'student' else 'ta'
        )

        db.session.add(enrollment)
        db.session.commit()

        return jsonify({
            'msg': 'Successfully enrolled in course',
            'enrollment': enrollment.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@courses_bp.route('/<int:course_id>/enroll/<int:user_id>', methods=['POST'])
@admin_required
def enroll_user(course_id, user_id):
    """Enroll a user (student or TA) in a course (admin only)"""
    try:
        course = Course.query.get(course_id)
        if not course:
            return jsonify({'error': 'Course not found'}), 404

        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Check if already enrolled
        existing_enrollment = CourseEnrollment.query.filter_by(
            course_id=course_id,
            user_id=user_id
        ).first()
        
        if existing_enrollment:
            return jsonify({'error': 'User already enrolled in this course'}), 409

        # Check enrollment conditions
        if not course.is_active:
            return jsonify({'error': 'Course is not active'}), 400
        
        if course.enrollment_type == 'closed':
            return jsonify({'error': 'Course enrollment is closed'}), 400
        
        if course.max_students and course.get_enrolled_count('student') >= course.max_students:
            return jsonify({'error': 'Course has reached maximum enrollment'}), 400

        # Determine role based on user role
        role = 'student' if user.role == 'student' else 'ta'

        # Create enrollment
        enrollment = CourseEnrollment(
            course_id=course_id,
            user_id=user_id,
            role=role
        )

        db.session.add(enrollment)
        db.session.commit()

        return jsonify({
            'msg': 'Successfully enrolled user in course',
            'enrollment': enrollment.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@courses_bp.route('/<int:course_id>/enroll-ta/<int:user_id>', methods=['POST'])
@admin_required
def enroll_ta(course_id, user_id):
    """Enroll a TA in a course (admin only)"""
    return enroll_user(course_id, user_id)

@courses_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return {'status': 'ok', 'message': 'Courses API is running'}

@courses_bp.route('/<int:course_id>/weeks', methods=['GET'])
@jwt_required()
def get_course_weeks(course_id):
    """Get all weeks for a course"""
    try:
        course = Course.query.get_or_404(course_id)
        weeks = Week.query.filter_by(course_id=course_id).order_by(Week.number).all()
        
        return jsonify({
            'success': True,
            'data': [week.to_dict() for week in weeks],
            'message': 'Course weeks retrieved successfully'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Failed to retrieve course weeks'
        }), 500

@courses_bp.route('/<int:course_id>/weeks', methods=['POST'])
@jwt_required()
@roles_required('admin', 'ta')  # Allow both admin and TA
def create_week(course_id):
    """Create a new week in a course"""
    try:
        data = request.get_json()
        if not all(k in data for k in ['number', 'title']):
            return jsonify({
                'success': False,
                'message': 'Missing required fields'
            }), 400
            
        course = Course.query.get_or_404(course_id)
        
        # Check if week number already exists in this course
        existing_week = Week.query.filter_by(
            course_id=course_id,
            number=data['number']
        ).first()
        if existing_week:
            return jsonify({
                'success': False,
                'message': f'Week {data["number"]} already exists in this course'
            }), 400
            
        week = Week(
            course_id=course_id,
            number=data['number'],
            title=data['title'],
            description=data.get('description', ''),
            is_published=data.get('is_published', False)
        )
        db.session.add(week)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': week.to_dict(),
            'message': 'Week created successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        # Check if it's a unique constraint violation
        if 'unique_week_number' in str(e):
            return jsonify({
                'success': False,
                'message': f'Week {data["number"]} already exists in this course'
            }), 400
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Failed to create week'
        }), 500

@courses_bp.route('/<int:course_id>/weeks/<int:week_id>', methods=['PUT'])
@jwt_required()
@roles_required('admin', 'ta')
def update_week(course_id, week_id):
    """Update an existing week in a course"""
    try:
        data = request.get_json()
        if not all(k in data for k in ['number', 'title']):
            return jsonify({
                'success': False,
                'message': 'Missing required fields'
            }), 400
            
        course = Course.query.get_or_404(course_id)
        week = Week.query.get_or_404(week_id)
        
        if week.course_id != course_id:
            return jsonify({
                'success': False,
                'message': 'Week does not belong to this course'
            }), 404
            
        # Check if the new week number conflicts with another week
        if data['number'] != week.number:
            existing_week = Week.query.filter_by(
                course_id=course_id,
                number=data['number']
            ).first()
            if existing_week and existing_week.id != week_id:
                return jsonify({
                    'success': False,
                    'message': f'Week {data["number"]} already exists in this course'
                }), 400
        
        week.number = data['number']
        week.title = data['title']
        week.description = data.get('description', '')
        week.is_published = data.get('is_published', False)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': week.to_dict(),
            'message': 'Week updated successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@courses_bp.route('/weeks/<int:week_id>/lectures', methods=['GET'])
@jwt_required()
@roles_required('admin', 'ta')
def get_lectures(week_id):
    """Get all lectures for a week"""
    try:
        week = Week.query.get_or_404(week_id)
        lectures = Lecture.query.filter_by(week_id=week_id).order_by(Lecture.order).all()
        
        return jsonify({
            'success': True,
            'data': [lecture.to_dict() for lecture in lectures],
            'message': 'Lectures retrieved successfully'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Failed to retrieve lectures'
        }), 500

@courses_bp.route('/weeks/<int:week_id>/lectures', methods=['POST'])
@jwt_required()
@roles_required('admin', 'ta')  # Allow both admin and TA
def create_lecture(week_id):
    """Create a new lecture in a week"""
    try:
        data = request.get_json()
        if not all(k in data for k in ['title', 'youtube_url']):
            return jsonify({
                'success': False,
                'message': 'Missing required fields'
            }), 400
            
        week = Week.query.get_or_404(week_id)
        
        # Get the highest order number and add 1
        last_lecture = Lecture.query.filter_by(week_id=week_id).order_by(Lecture.order.desc()).first()
        new_order = (last_lecture.order + 1) if last_lecture else 1
        
        lecture = Lecture(
            week_id=week_id,
            title=data['title'],
            description=data.get('description', ''),
            youtube_url=data['youtube_url'],
            transcript=data.get('transcript', ''),
            order=new_order,
            is_published=data.get('is_published', False)
        )
        db.session.add(lecture)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': lecture.to_dict(),
            'message': 'Lecture created successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Failed to create lecture'
        }), 500

@courses_bp.route('/lectures/<int:lecture_id>', methods=['PUT'])
@jwt_required()
@roles_required('admin', 'ta')
def update_lecture(lecture_id):
    """Update a lecture"""
    try:
        data = request.get_json()
        lecture = Lecture.query.get_or_404(lecture_id)
        
        # Update fields if provided
        if 'title' in data:
            lecture.title = data['title']
        if 'description' in data:
            lecture.description = data['description']
        if 'youtube_url' in data:
            lecture.youtube_url = data['youtube_url']
        if 'transcript' in data:
            lecture.transcript = data['transcript']
        if 'is_published' in data:
            lecture.is_published = data['is_published']
            
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': lecture.to_dict(),
            'message': 'Lecture updated successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Failed to update lecture'
        }), 500

@courses_bp.route('/lectures/<int:lecture_id>', methods=['DELETE'])
@jwt_required()
@roles_required('admin', 'ta')
def delete_lecture(lecture_id):
    """Delete a lecture"""
    try:
        lecture = Lecture.query.get_or_404(lecture_id)
        db.session.delete(lecture)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Lecture deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Failed to delete lecture'
        }), 500

@courses_bp.route('/<int:course_id>/content', methods=['GET'])
@jwt_required()
def get_course_content(course_id):
    """Get full course content for students"""
    try:
        current_user = User.query.get(get_jwt_identity())
        course = Course.query.get_or_404(course_id)

        # Check if user has access to the course
        if current_user.role not in ['admin', 'ta']:
            enrollment = CourseEnrollment.query.filter_by(
                user_id=current_user.id,
                course_id=course_id,
                status='active'
            ).first()
            if not enrollment:
                return jsonify({
                    'success': False,
                    'message': 'Not enrolled in this course'
                }), 403

        # Get all weeks with their content
        weeks = Week.query.filter_by(course_id=course_id).order_by(Week.number).all()
        
        # Convert course and weeks to dict format
        course_data = course.to_dict()
        course_data['weeks'] = [week.to_dict() for week in weeks]

        return jsonify({
            'success': True,
            'data': course_data,
            'message': 'Course content retrieved successfully'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Failed to retrieve course content'
        }), 500

@courses_bp.route('/lectures/<int:lecture_id>/content', methods=['GET'])
@jwt_required()
def get_lecture_content(lecture_id):
    """Get lecture content"""
    try:
        lecture = Lecture.query.get_or_404(lecture_id)
        
        # Check if user has access to this lecture
        current_user = User.query.get(get_jwt_identity())
        if not current_user:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
            
        # Check if user is enrolled in the course or is admin/TA
        if current_user.role == 'admin' or current_user.role == 'teacher':
            has_access = True
        else:
            enrollment = CourseEnrollment.query.filter_by(
                user_id=current_user.id,
                course_id=lecture.week.course_id,
                status='active'
            ).first()
            has_access = enrollment is not None
        
        if not has_access:
            return jsonify({
                'success': False,
                'message': 'Not enrolled in this course'
            }), 403
            
        return jsonify({
            'success': True,
            'data': lecture.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@courses_bp.route('/assignments/<int:assignment_id>/content', methods=['GET'])
@jwt_required()
def get_assignment_content(assignment_id):
    """Get assignment content for students"""
    try:
        current_user = User.query.get(get_jwt_identity())
        assignment = Assignment.query.get_or_404(assignment_id)
        
        # Check if assignment is published
        if not assignment.is_published:
            return jsonify({
                'success': False,
                'message': 'Assignment not available'
            }), 404

        # Get the course through week relationship
        course = Course.query.join(Week).join(Assignment).filter(
            Assignment.id == assignment_id
        ).first()

        # Check if user has access to the course
        if current_user.role not in ['admin', 'ta']:
            enrollment = CourseEnrollment.query.filter_by(
                user_id=current_user.id,
                course_id=course.id,
                status='active'
            ).first()
            if not enrollment:
                return jsonify({
                    'success': False,
                    'message': 'Not enrolled in this course'
                }), 403

        # Get questions without correct answers for students
        questions = []
        for aq in assignment.questions.order_by(AssignmentQuestion.order):
            question = aq.question
            question_data = {
                'id': question.id,
                'title': question.title,
                'content': question.content,
                'type': question.type,
                'points': question.points
            }
            
            # Include options for multiple choice questions
            if question.type == 'multiple_choice':
                options = json.loads(question.correct_answer)['options']
                question_data['options'] = options
            
            questions.append(question_data)

        return jsonify({
            'success': True,
            'data': {
                'id': assignment.id,
                'title': assignment.title,
                'description': assignment.description,
                'type': assignment.type,
                'due_date': assignment.due_date.isoformat() if assignment.due_date else None,
                'questions': questions
            }
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@courses_bp.route('/weeks/<int:week_id>/assignments', methods=['POST'])
@jwt_required()
@roles_required('admin', 'ta')
def create_week_assignment(week_id):
    """Create a new assignment in a week"""
    try:
        data = request.get_json()
        if not all(k in data for k in ['title', 'type']):
            return jsonify({
                'success': False,
                'message': 'Missing required fields'
            }), 400
            
        week = Week.query.get_or_404(week_id)
        
        assignment = Assignment(
            week_id=week_id,
            title=data['title'],
            description=data.get('description', ''),
            type=data['type'],
            due_date=datetime.fromisoformat(data['due_date']) if data.get('due_date') else None,
            points_possible=data.get('points_possible', 0),
            late_submission_penalty=data.get('late_submission_penalty', 0),
            is_published=data.get('is_published', False)
        )
        
        db.session.add(assignment)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': assignment.to_dict(),
            'message': 'Assignment created successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Failed to create assignment'
        }), 500

@courses_bp.route('/weeks', methods=['GET'])
@jwt_required()
def get_all_weeks():
    """Get all weeks across all courses for admin/teacher"""
    try:
        current_user = User.query.get(get_jwt_identity())
        if not current_user:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404

        # For admin, get all weeks
        if current_user.role == 'admin':
            weeks = Week.query.order_by(Week.course_id, Week.number).all()
        # For teacher/TA, get weeks from their courses
        elif current_user.role == 'teacher':
            course_ids = [e.course_id for e in current_user.enrollments if e.role == 'teacher']
            weeks = Week.query.filter(Week.course_id.in_(course_ids)).order_by(Week.course_id, Week.number).all()
        else:
            return jsonify({
                'success': False,
                'message': 'Unauthorized'
            }), 403

        return jsonify({
            'success': True,
            'data': [week.to_dict() for week in weeks]
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
