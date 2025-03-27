from datetime import datetime
from flask import Blueprint, request, jsonify, send_file, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from ...models import User, Course, CourseEnrollment, Week, Lecture, Assignment, Question, LectureProgress
from ...utils.auth import admin_required, student_or_ta_required, ta_required, roles_required
from ... import db
import json
import os
from werkzeug.utils import secure_filename
import traceback

courses_bp = Blueprint('courses', __name__)

def allowed_file(filename):
    """Check if the file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() == 'pdf'

def save_lecture_pdf(file, lecture_id):
    """Save uploaded PDF file and return the file path"""
    filename = f"Lecture_{lecture_id}.pdf"
    
    # Create upload directory if it doesn't exist
    upload_dir = current_app.config['UPLOAD_FOLDER']
    os.makedirs(upload_dir, exist_ok=True)
    
    file_path = os.path.join(upload_dir, filename)
    file.save(file_path)
    
    return filename

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
            'success': True,
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

@courses_bp.route('/<int:course_id>/enroll/<int:student_id>', methods=['POST'])
@admin_required
def enroll_in_course(course_id,student_id):

    
    """Enroll in a course (student/TA only)"""
    try:
        course = Course.query.get(course_id)
        
        if not course:
            return jsonify({'error': 'Course not found'}), 404

        current_user = User.query.get(get_jwt_identity())
        
        # Check if already enrolled
        existing_enrollment = CourseEnrollment.query.filter_by(
            course_id=course_id,
            user_id=student_id
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
            user_id=student_id,
            # role='student' if current_user.role == 'student' else 'ta'
            role='student'
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

        # Update lecture progress for the student
        if current_user.role == 'student':
            lecture_progress = LectureProgress.query.filter_by(
                lecture_id=lecture_id,
                user_id=current_user.id
            ).first()
            
            if not lecture_progress:
                lecture_progress = LectureProgress(
                    lecture_id=lecture_id,
                    user_id=current_user.id,
                    completed=True,
                    completed_at=datetime.utcnow()
                )
                db.session.add(lecture_progress)
            else:
                lecture_progress.completed = True
                lecture_progress.completed_at = datetime.utcnow()
            
            db.session.commit()
            
        response_data = lecture.to_dict()
        
        # Add content-specific data
        if lecture.content_type == 'youtube':
            if not lecture.youtube_url:
                return jsonify({
                    'success': False,
                    'message': 'YouTube URL not found for this lecture'
                }), 404
        elif lecture.content_type == 'pdf':
            if not lecture.file_path:
                return jsonify({
                    'success': False,
                    'message': 'PDF file not found for this lecture'
                }), 404
            
        return jsonify({
            'success': True,
            'data': response_data
        }), 200
        
    except Exception as e:
        import traceback
        print("Error in get_lecture_content:", str(e))
        print("Traceback:", traceback.format_exc())
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
        for aq in assignment.questions.order_by(Question.order):
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

@courses_bp.route('/enroll/', methods=['POST'])
@jwt_required()
@roles_required('admin', 'ta')
def enroll_student():
    """Enroll a student or TA in a course"""
    try:
        data = request.get_json()
        course_id = data.get('courseId')
        student_id = data.get('studentId')
        role = data.get('role', 'student')

        # Validate input
        if not course_id or not student_id:
            return jsonify({'success': False, 'message': 'Missing courseId or studentId'}), 400

        course = Course.query.get(course_id)
        if not course:
            return jsonify({'success': False, 'message': 'Course not found'}), 404

        student = User.query.get(student_id)
        if not student:
            return jsonify({'success': False, 'message': 'Student not found'}), 404

        # Check if already enrolled
        existing_enrollment = CourseEnrollment.query.filter_by(course_id=course_id, user_id=student_id).first()
        if existing_enrollment:
            return jsonify({'success': False, 'message': 'Already enrolled in this course'}), 409

        # Check enrollment conditions
        if not course.is_active:
            return jsonify({'success': False, 'message': 'Course is not active'}), 400

        if course.enrollment_type == 'closed':
            return jsonify({'success': False, 'message': 'Course enrollment is closed'}), 400

        if course.max_students and course.get_enrolled_count('student') >= course.max_students:
            return jsonify({'success': False, 'message': 'Course has reached maximum enrollment'}), 400

        # Create enrollment
        enrollment = CourseEnrollment(course_id=course_id, user_id=student_id, role=role)
        db.session.add(enrollment)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Successfully enrolled in course', 'enrollment': enrollment.to_dict()}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e), 'message': 'Failed to enroll student'}), 500

@courses_bp.route('/lectures/<int:lecture_id>/progress', methods=['POST'])
@jwt_required()
def mark_lecture_completed(lecture_id):
    """Mark a lecture as completed for the current user"""
    try:
        current_user = User.query.get(get_jwt_identity())
        if not current_user:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404

        lecture = Lecture.query.get_or_404(lecture_id)
        
        # Check if user is enrolled in the course
        enrollment = CourseEnrollment.query.filter_by(
            user_id=current_user.id,
            course_id=lecture.week.course_id,
            status='active'
        ).first()
        
        if not enrollment:
            return jsonify({
                'success': False,
                'message': 'Not enrolled in this course'
            }), 403

        # Create or update progress record
        progress = LectureProgress.query.filter_by(
            lecture_id=lecture_id,
            user_id=current_user.id
        ).first()

        if not progress:
            progress = LectureProgress(
                lecture_id=lecture_id,
                user_id=current_user.id,
                completed=True,
                completed_at=datetime.utcnow()
            )
            db.session.add(progress)
        else:
            progress.completed = True
            progress.completed_at = datetime.utcnow()

        db.session.commit()

        # Calculate updated progress
        course = lecture.week.course
        course_progress = course.calculate_progress(current_user.id)
        
        return jsonify({
            'success': True,
            'data': {
                'lecture_progress': progress.to_dict(),
                'course_progress': course_progress
            },
            'message': 'Lecture marked as completed'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@courses_bp.route('/<int:course_id>/progress', methods=['GET', 'OPTIONS'])
@jwt_required()
def get_course_progress(course_id):
    """Get course progress for the current user"""
    # Handle OPTIONS request for CORS
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        current_user = User.query.get(get_jwt_identity())
        if not current_user:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404

        course = Course.query.get_or_404(course_id)
        
        # Check if user is enrolled in the course
        enrollment = CourseEnrollment.query.filter_by(
            user_id=current_user.id,
            course_id=course_id,
            status='active'
        ).first()
        
        if not enrollment and current_user.role not in ['admin', 'teacher']:
            return jsonify({
                'success': False,
                'message': 'Not enrolled in this course'
            }), 403

        progress = course.calculate_progress(current_user.id)
        
        return jsonify({
            'success': True,
            'data': progress,
            'message': 'Course progress retrieved successfully'
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@courses_bp.route('/lectures/<int:lecture_id>/pdf', methods=['GET', 'OPTIONS'])
@jwt_required()
def get_lecture_pdf(lecture_id):
    """Get lecture PDF file"""
    print(f"\n=== PDF Request ===")
    print(f"Method: {request.method}")
    print(f"Headers: {dict(request.headers)}")
    print(f"Lecture ID: {lecture_id}")
    
    # Handle OPTIONS request for CORS
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': 'http://127.0.0.1:3000',
            'Access-Control-Allow-Methods': 'GET, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
            'Access-Control-Allow-Credentials': 'true'
        }
        return '', 200, headers
        
    try:
        # Get lecture
        lecture = Lecture.query.get_or_404(lecture_id)
        print(f"Found lecture: {lecture.title}")
        print(f"Content type: {lecture.content_type}")
        print(f"File path: {lecture.file_path}")
        
        # Check if lecture has PDF content
        if lecture.content_type != 'pdf' or not lecture.file_path:
            print("Error: No PDF content found")
            return jsonify({
                'success': False,
                'message': 'PDF not found for this lecture'
            }), 404
            
        # Get full file path
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], lecture.file_path)
        print(f"Full file path: {file_path}")
        print(f"File exists: {os.path.exists(file_path)}")
        
        if not os.path.exists(file_path):
            print("Error: File not found at path")
            return jsonify({
                'success': False,
                'message': 'PDF file not found on server'
            }), 404
            
        try:
            # Send file with proper headers for PDF display
            response = send_file(
                file_path,
                mimetype='application/pdf',
                as_attachment=False,  # This allows the browser to display the PDF
                download_name=lecture.file_path  # Provide the filename
            )
            
            # Set required headers for PDF display and CORS
            response.headers['Content-Type'] = 'application/pdf'
            response.headers['Content-Disposition'] = 'inline'
            response.headers['Access-Control-Allow-Origin'] = 'http://127.0.0.1:3000'
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
            response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
            
            print("Successfully sending file response")
            print(f"Response headers: {dict(response.headers)}")
            return response
            
        except Exception as file_error:
            print(f"Error sending file: {str(file_error)}")
            print(f"Error type: {type(file_error)}")
            print(f"Error traceback: {traceback.format_exc()}")
            return jsonify({
                'success': False,
                'message': f'Error serving PDF file: {str(file_error)}'
            }), 500
            
    except Exception as e:
        print(f"Error in get_lecture_pdf: {str(e)}")
        print(f"Error type: {type(e)}")
        print(f"Error traceback: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@courses_bp.route('/lectures/<int:lecture_id>/pdf', methods=['POST'])
@jwt_required()
@roles_required('admin', 'ta')
def upload_lecture_pdf(lecture_id):
    """Upload a PDF file for a lecture"""
    try:
        # Get lecture
        lecture = Lecture.query.get_or_404(lecture_id)
        
        # Check if file is provided
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'message': 'No file provided'
            }), 400
            
        file = request.files['file']
        if not file or not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'message': 'Invalid file type. Only PDF files are allowed.'
            }), 400
            
        # Save file and update lecture
        filename = save_lecture_pdf(file, lecture_id)
        
        # Delete old file if exists
        if lecture.file_path:
            old_file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], lecture.file_path)
            try:
                os.remove(old_file_path)
            except OSError:
                pass  # Ignore if file doesn't exist
        
        # Update lecture record
        lecture.content_type = 'pdf'
        lecture.file_path = filename
        
        # Extract text from PDF if possible
        # TODO: Add PDF text extraction here if needed
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': lecture.to_dict(),
            'message': 'PDF uploaded successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print("Error uploading PDF:", str(e))
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


