"""Assignment management endpoints."""
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from datetime import datetime, date
from ...models import (
    User, Week, Assignment, Question, AssignmentQuestion, 
    CourseEnrollment, AssignmentSubmission
)
from ...utils.auth import ta_required
from ...decorators import admin_or_ta_required
from ... import db
import json

assignments_bp = Blueprint('assignments', __name__, url_prefix='/assignments')

# Constants for validation
VALID_ASSIGNMENT_TYPES = ['practice', 'graded']
VALID_ASSIGNMENT_STATUS = ['draft', 'published', 'archived']

def validate_assignment_data(data, check_required=True):
    """Validate assignment data"""
    errors = []
    
    # Check required fields
    if check_required:
        required_fields = ['title', 'type']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            errors.append(f"Missing required fields: {', '.join(missing_fields)}")
    
    # Validate type if provided
    if 'type' in data:
        if data['type'] not in VALID_ASSIGNMENT_TYPES:
            errors.append(f"Invalid assignment type. Must be one of: {', '.join(VALID_ASSIGNMENT_TYPES)}")
        
        # For graded assignments, start_date and due_date are required
        if data['type'] == 'graded':
            if check_required and not all(k in data for k in ['start_date', 'due_date']):
                errors.append("Graded assignments must have start_date and due_date")
    
    # Validate dates if provided
    if 'start_date' in data and 'due_date' in data:
        try:
            start = datetime.fromisoformat(data['start_date'].replace('Z', '+00:00'))
            due = datetime.fromisoformat(data['due_date'].replace('Z', '+00:00'))
            if start >= due:
                errors.append("start_date must be before due_date")
        except (ValueError, TypeError):
            errors.append("Invalid date format. Use ISO format (YYYY-MM-DDTHH:MM:SSZ)")
    
    # Validate points_possible if provided
    if 'points_possible' in data:
        try:
            points = int(data['points_possible'])
            if points < 0:
                errors.append("points_possible must be non-negative")
        except (ValueError, TypeError):
            errors.append("points_possible must be an integer")
    
    # Validate late_submission_penalty if provided
    if 'late_submission_penalty' in data:
        try:
            penalty = float(data['late_submission_penalty'])
            if penalty < 0:
                errors.append("late_submission_penalty must be non-negative")
        except (ValueError, TypeError):
            errors.append("late_submission_penalty must be a number")
    
    return errors

@assignments_bp.route('/', methods=['GET', 'OPTIONS'])
def list_all_assignments():
    """List all assignments with filters for admin/teacher view"""
    if request.method == 'OPTIONS':
        return '', 200

    @jwt_required()
    def get_assignments():
        try:
            current_user = User.query.get(get_jwt_identity())
            
            # Build query
            query = Assignment.query

            # For students, only show published assignments from their enrolled courses
            if current_user.role == 'student':
                enrolled_courses = [e.course_id for e in current_user.course_enrollments if e.status == 'active']
                query = query.join(Week).filter(
                    Week.course_id.in_(enrolled_courses),
                    Assignment.is_published == True
                )

            # Get query parameters
            course_id = request.args.get('course_id', type=int)
            week_id = request.args.get('week_id', type=int)
            assignment_type = request.args.get('type')
            status = request.args.get('status')
            search = request.args.get('search')

            # Apply filters
            if course_id:
                query = query.join(Week).filter(Week.course_id == course_id)
            if week_id:
                query = query.filter(Assignment.week_id == week_id)
            if assignment_type and assignment_type in VALID_ASSIGNMENT_TYPES:
                query = query.filter(Assignment.type == assignment_type)
            if status and current_user.role in ['admin', 'ta']:
                if status == 'published':
                    query = query.filter(Assignment.is_published == True)
                elif status == 'draft':
                    query = query.filter(Assignment.is_published == False)
            if search:
                search_term = f"%{search}%"
                query = query.filter(Assignment.title.ilike(search_term))

            # Execute query
            assignments = query.all()

            # Convert to dict with calculated points
            assignments_data = []
            for assignment in assignments:
                assignment_dict = assignment.to_dict()
                # Calculate total points from questions
                total_points = sum(aq.question.points for aq in assignment.questions.all())
                assignment_dict['points_possible'] = total_points
                assignments_data.append(assignment_dict)

            return jsonify({
                'success': True,
                'data': assignments_data
            }), 200

        except Exception as e:
            return jsonify({
                'success': False,
                'message': str(e)
            }), 500

    return get_assignments()

@assignments_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return {'status': 'ok', 'message': 'Assignments API is running'}

@assignments_bp.route('/weeks/<int:week_id>/assignments', methods=['GET'])
@jwt_required()
def get_week_assignments(week_id):
    """Get all assignments for a week"""
    try:
        week = Week.query.get_or_404(week_id)
        assignments = Assignment.query.filter_by(week_id=week_id).all()
        
        return jsonify({
            'success': True,
            'data': [assignment.to_dict() for assignment in assignments]
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@assignments_bp.route('/weeks/<int:week_id>/assignments', methods=['POST'])
@jwt_required()
@ta_required
def create_assignment(week_id):
    """Create a new assignment in a week"""
    try:
        data = request.get_json()
        
        # Validate data
        errors = validate_assignment_data(data)
        if errors:
            return jsonify({
                'success': False,
                'message': 'Validation failed',
                'errors': errors
            }), 400
        
        # Ensure week exists
        week = Week.query.get_or_404(week_id)
        
        # Create assignment
        assignment = Assignment(
            week_id=week_id,
            title=data['title'],
            description=data.get('description', ''),
            type=data['type'],
            start_date=data.get('start_date'),
            due_date=data.get('due_date'),
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
            'message': str(e)
        }), 500

@assignments_bp.route('/questions', methods=['GET'])
@jwt_required()
@ta_required
def get_questions():
    """Get all questions (for question bank)"""
    try:
        current_user = User.query.get(get_jwt_identity())
        questions = Question.query.filter_by(created_by_id=current_user.id).all()
        
        return jsonify({
            'success': True,
            'data': [question.to_dict() for question in questions]
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@assignments_bp.route('/questions', methods=['POST'])
@jwt_required()
@ta_required
def create_question():
    """Create a new question"""
    try:
        data = request.get_json()
        required_fields = ['title', 'content', 'type', 'correct_answer']
        if not all(k in data for k in required_fields):
            return jsonify({
                'success': False,
                'message': 'Missing required fields'
            }), 400
            
        # Validate question type
        if data['type'] not in ['multiple_choice', 'true_false', 'text']:
            return jsonify({
                'success': False,
                'message': 'Invalid question type'
            }), 400
            
        current_user = User.query.get(get_jwt_identity())
        question = Question(
            created_by_id=current_user.id,
            title=data['title'],
            content=data['content'],
            type=data['type'],
            correct_answer=data['correct_answer'],
            points=data.get('points', 1),
            explanation=data.get('explanation', '')
        )
        db.session.add(question)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': question.to_dict(),
            'message': 'Question created successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@assignments_bp.route('/assignments/<int:assignment_id>', methods=['PUT'])
@jwt_required()
@ta_required
def update_assignment(assignment_id):
    """Update an assignment"""
    try:
        assignment = Assignment.query.get_or_404(assignment_id)
        data = request.get_json()
        
        # Validate data
        errors = validate_assignment_data(data, check_required=False)
        if errors:
            return jsonify({
                'success': False,
                'message': 'Validation failed',
                'errors': errors
            }), 400
        
        # Update fields
        for field in ['title', 'description', 'type', 'start_date', 'due_date',
                     'points_possible', 'late_submission_penalty', 'is_published']:
            if field in data:
                setattr(assignment, field, data[field])
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': assignment.to_dict(),
            'message': 'Assignment updated successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@assignments_bp.route('/assignments/<int:assignment_id>/questions', methods=['POST'])
@jwt_required()
@ta_required
def add_questions_to_assignment(assignment_id):
    """Add questions to an assignment"""
    try:
        data = request.get_json()
        if 'question_ids' not in data:
            return jsonify({
                'success': False,
                'message': 'Missing question_ids'
            }), 400
        
        # Validate question_ids is a list
        if not isinstance(data['question_ids'], list):
            return jsonify({
                'success': False,
                'message': 'question_ids must be a list'
            }), 400
            
        assignment = Assignment.query.get_or_404(assignment_id)
        
        # Get the highest order number
        last_question = AssignmentQuestion.query.filter_by(
            assignment_id=assignment_id
        ).order_by(AssignmentQuestion.order.desc()).first()
        next_order = (last_question.order + 1) if last_question else 1
        
        # Add questions
        added_questions = []
        for question_id in data['question_ids']:
            # Check if question exists and is active
            question = Question.query.filter_by(id=question_id, status='active').first()
            if not question:
                continue
                
            # Check if question is already in assignment
            existing = AssignmentQuestion.query.filter_by(
                assignment_id=assignment_id,
                question_id=question_id
            ).first()
            if existing:
                continue
                
            aq = AssignmentQuestion(
                assignment_id=assignment_id,
                question_id=question_id,
                order=next_order
            )
            db.session.add(aq)
            added_questions.append(question)
            next_order += 1
            
        # Update assignment points
        if added_questions:
            assignment.points_possible = sum(q.points for q in assignment.questions)
            
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': {
                'assignment': assignment.to_dict(),
                'added_questions': len(added_questions)
            },
            'message': f'Added {len(added_questions)} questions to assignment'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@assignments_bp.route('/assignments/<int:assignment_id>/questions/<int:question_id>', methods=['DELETE'])
@jwt_required()
@ta_required
def remove_question_from_assignment(assignment_id, question_id):
    """Remove a question from an assignment"""
    try:
        assignment = Assignment.query.get_or_404(assignment_id)
        aq = AssignmentQuestion.query.filter_by(
            assignment_id=assignment_id,
            question_id=question_id
        ).first_or_404()
        
        db.session.delete(aq)
        
        # Update assignment points
        assignment.points_possible = sum(q.points for q in assignment.questions) - aq.question.points
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': assignment.to_dict(),
            'message': 'Question removed from assignment successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@assignments_bp.route('/<int:assignment_id>/submissions', methods=['GET', 'OPTIONS'])
@jwt_required()
def get_assignment_submissions(assignment_id):
    """Get submissions for an assignment"""
    if request.method == 'OPTIONS':
        return '', 200

    try:
        current_user = User.query.get(get_jwt_identity())
        assignment = Assignment.query.get_or_404(assignment_id)

        # Get all submissions for this assignment by this student
        submissions = AssignmentSubmission.query.filter_by(
            assignment_id=assignment_id,
            student_id=current_user.id
        ).order_by(AssignmentSubmission.submitted_at.desc()).all()

        submissions_data = []
        for submission in submissions:
            submission_data = {
                'id': submission.id,
                'score': submission.score,
                'status': submission.status,
                'submitted_at': submission.submitted_at.isoformat(),
                'answers': submission.answers,
                'question_scores': submission.question_scores
            }
            submissions_data.append(submission_data)

        return jsonify({
            'success': True,
            'data': submissions_data
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@assignments_bp.route('/<int:assignment_id>', methods=['GET', 'PUT', 'DELETE', 'OPTIONS'])
def manage_assignment(assignment_id):
    """Manage a specific assignment"""
    if request.method == 'OPTIONS':
        return '', 200
        
    @jwt_required()
    def handle_request():
        try:
            assignment = Assignment.query.get_or_404(assignment_id)
            
            if request.method == 'GET':
                # Get assignment details with questions
                assignment_data = assignment.to_dict()
                
                # Add Week data
                week = assignment.week
                assignment_data['week'] = {
                    'id': week.id,
                    'number': week.number,
                    'title': week.title,
                    'course_id': week.course_id
                }
                
                # Process questions with full details
                questions_data = []
                for aq in assignment.questions.order_by(AssignmentQuestion.order):
                    question = aq.question
                    if question:
                        try:
                            # Parse options from JSON if it's a string
                            options = json.loads(question.question_options) if isinstance(question.question_options, str) else question.question_options
                            options = options if isinstance(options, list) else []
                        except (json.JSONDecodeError, TypeError):
                            options = []

                        question_data = {
                            'id': question.id,
                            'title': question.title,
                            'content': question.content,
                            'type': question.type,
                            'points': question.points,
                            'options': options,
                            'order': aq.order
                        }
                        questions_data.append(question_data)
                
                assignment_data['questions'] = questions_data
                assignment_data['points_possible'] = sum(q['points'] for q in questions_data)
                
                return jsonify({
                    'success': True,
                    'data': assignment_data
                }), 200
            
            # For PUT and DELETE, require admin or TA access
            current_user = User.query.get(get_jwt_identity())
            if current_user.role not in ['admin', 'ta']:
                return jsonify({
                    'success': False,
                    'message': 'Admin or TA access required for this operation'
                }), 403

            if request.method == 'PUT':
                data = request.get_json()
                
                # Validate data
                errors = validate_assignment_data(data, check_required=False)
                if errors:
                    return jsonify({
                        'success': False,
                        'message': 'Validation failed',
                        'errors': errors
                    }), 400
                
                # Update fields
                assignment.title = data.get('title', assignment.title)
                assignment.description = data.get('description', assignment.description)
                assignment.type = data.get('type', assignment.type)
                assignment.week_id = data.get('week_id', assignment.week_id)
                
                if 'start_date' in data:
                    assignment.start_date = datetime.fromisoformat(data['start_date'].replace('Z', '+00:00')) if data['start_date'] else None
                if 'due_date' in data:
                    assignment.due_date = datetime.fromisoformat(data['due_date'].replace('Z', '+00:00')) if data['due_date'] else None
                    
                assignment.late_submission_penalty = data.get('late_submission_penalty', assignment.late_submission_penalty)
                assignment.is_published = data.get('is_published', assignment.is_published)
                
                db.session.commit()
                
                return jsonify({
                    'success': True,
                    'data': assignment.to_dict(),
                    'message': 'Assignment updated successfully'
                }), 200
                
            elif request.method == 'DELETE':
                db.session.delete(assignment)
                db.session.commit()
                
                return jsonify({
                    'success': True,
                    'message': 'Assignment deleted successfully'
                }), 200
                
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'success': False,
                'message': str(e)
            }), 500
            
    return handle_request()

@assignments_bp.route('/student/assignments', methods=['GET'])
@jwt_required()
def get_student_assignments():
    """Get all assignments for the current student"""
    try:
        current_user = User.query.get(get_jwt_identity())
        if not current_user:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
            
        # Get all courses the student is enrolled in
        enrollments = CourseEnrollment.query.filter_by(
            user_id=current_user.id,
            role='student',
            status='active'
        ).all()
        
        course_ids = [e.course_id for e in enrollments]
        
        # Get all weeks for these courses
        weeks = Week.query.filter(Week.course_id.in_(course_ids)).all()
        week_ids = [w.id for w in weeks]
        
        # Get all assignments for these weeks
        assignments = Assignment.query.filter(
            Assignment.week_id.in_(week_ids),
            Assignment.is_published == True
        ).order_by(Assignment.due_date).all()
        
        # Get submissions for these assignments
        submissions = {
            s.assignment_id: s for s in current_user.submissions
        }
        
        # Prepare assignment data with submission status
        assignments_data = []
        for assignment in assignments:
            data = assignment.to_dict()
            submission = submissions.get(assignment.id)
            if submission:
                data['submission'] = {
                    'id': submission.id,
                    'score': submission.score,
                    'status': 'submitted',
                    'submitted_at': submission.submitted_at.isoformat() if submission.submitted_at else None
                }
            else:
                data['submission'] = None
            assignments_data.append(data)
        
        return jsonify({
            'success': True,
            'data': assignments_data
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@assignments_bp.route('/<int:assignment_id>/submit', methods=['POST'])
@jwt_required()
def submit_assignment(assignment_id):
    """Submit an assignment."""
    try:
        # Get current user
        current_user = User.query.get(get_jwt_identity())
        if not current_user:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404

        # Get the assignment
        assignment = Assignment.query.get_or_404(assignment_id)
        
        # Check if assignment exists and is published
        if not assignment.is_published:
            return jsonify({
                'success': False,
                'message': 'This assignment is not available for submission'
            }), 400
            
        # Check if user is enrolled in the course
        enrollment = CourseEnrollment.query.filter_by(
            user_id=current_user.id,
            course_id=assignment.week.course_id,
            status='active'
        ).first()
        
        if not enrollment:
            return jsonify({
                'success': False,
                'message': 'You are not enrolled in this course'
            }), 403
            
        # Get submission data
        data = request.get_json()
        if not data or 'answers' not in data:
            return jsonify({
                'success': False,
                'message': 'No answers provided'
            }), 400
            
        # Check for existing submission - only for graded assignments
        if assignment.type == 'practice'  and assignment.due_date < datetime.utcnow():
            submission = AssignmentSubmission.query.filter_by(
                assignment_id=assignment_id,
                student_id=current_user.id
            ).first()
            
            if submission:
                return jsonify({
                    'success': False,
                    'message': 'You have already submitted this assignment'
                }), 400
            
        # Calculate scores and format answers
        total_score = 0
        max_score = 0
        question_scores = {}
        formatted_answers = {}
        
        for aq in assignment.questions:
            question = aq.question
            question_id = str(question.id)
            max_score += question.points
            
            # Handle missing answers
            if question_id not in data['answers']:
                question_scores[question_id] = 0
                formatted_answers[question_id] = {
                    'answer': None,
                    'is_correct': False
                }
                continue
                
            student_answer = data['answers'][question_id]
            correct_answer = json.loads(question.correct_answer) if isinstance(question.correct_answer, str) else question.correct_answer
            
            # Check answer based on question type
            is_correct = False
            if question.type == 'MCQ':
                is_correct = student_answer == correct_answer
                formatted_answers[question_id] = {
                    'answer': student_answer,
                    'is_correct': is_correct
                }
            elif question.type == 'MSQ':
                student_set = set(student_answer if isinstance(student_answer, list) else [student_answer])
                correct_set = set(correct_answer if isinstance(correct_answer, list) else [correct_answer])
                is_correct = student_set == correct_set
                formatted_answers[question_id] = {
                    'answer': sorted(list(student_set)),
                    'is_correct': is_correct
                }
            elif question.type == 'NUMERIC':
                try:
                    student_value = float(student_answer)
                    correct_value = float(correct_answer)
                    tolerance = 0.001  # Small tolerance for floating-point comparison
                    is_correct = abs(student_value - correct_value) <= tolerance
                    formatted_answers[question_id] = {
                        'answer': student_value,
                        'is_correct': is_correct
                    }
                except (ValueError, TypeError):
                    formatted_answers[question_id] = {
                        'answer': student_answer,
                        'is_correct': False
                    }
            
            question_scores[question_id] = question.points if is_correct else 0
            total_score += question_scores[question_id]
        
        # Create new submission
        submission = AssignmentSubmission(
            assignment_id=assignment_id,
            student_id=current_user.id,
            answers=formatted_answers,
            score=total_score,
            question_scores=question_scores
        )
        
        # Calculate if submission is late
        if assignment.due_date and datetime.utcnow() > assignment.due_date:
            submission.status = 'late'
            if assignment.late_submission_penalty:
                submission.score = round(total_score * (1 - assignment.late_submission_penalty/100), 2)
        else:
            submission.status = 'submitted'
            
        # Save submission
        db.session.add(submission)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Assignment submitted successfully',
            'data': {
                'id': submission.id,
                'score': submission.score,
                'max_score': max_score,
                'status': submission.status,
                'question_scores': submission.question_scores,
                'answers': submission.answers,
                'submitted_at': submission.submitted_at.isoformat(),
                'is_practice': assignment.type == 'practice'
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@assignments_bp.route('/<int:assignment_id>/questions', methods=['GET', 'POST', 'OPTIONS'])
def manage_assignment_questions(assignment_id):
    """Manage questions for an assignment"""
    if request.method == 'OPTIONS':
        return '', 200
        
    @jwt_required()
    @admin_or_ta_required
    def handle_request():
        try:
            assignment = Assignment.query.get_or_404(assignment_id)
            
            if request.method == 'GET':
                questions_data = []
                for aq in assignment.questions.order_by(AssignmentQuestion.order):
                    if aq.question:
                        question_dict = aq.question.to_dict()
                        question_dict.update({
                            'order': aq.order,
                            'points': aq.points
                        })
                        questions_data.append(question_dict)
                
                return jsonify({
                    'success': True,
                    'data': questions_data
                }), 200
                
            elif request.method == 'POST':
                data = request.get_json()
                if not data or 'question_ids' not in data:
                    return jsonify({
                        'success': False,
                        'message': 'question_ids is required'
                    }), 400
                    
                # Get existing questions
                existing_question_ids = set(aq.question_id for aq in assignment.questions)
                
                # Get the highest order number
                last_question = AssignmentQuestion.query.filter_by(
                    assignment_id=assignment_id
                ).order_by(AssignmentQuestion.order.desc()).first()
                next_order = (last_question.order + 1) if last_question else 1
                
                # Add new questions (skip if already exists)
                added_questions = []
                for question_id in data['question_ids']:
                    if question_id not in existing_question_ids:
                        assignment_question = AssignmentQuestion(
                            assignment_id=assignment_id,
                            question_id=question_id,
                            order=next_order
                        )
                        db.session.add(assignment_question)
                        added_questions.append(assignment_question)
                        next_order += 1
                    
                db.session.commit()
                
                # Return updated assignment data with new total points
                return jsonify({
                    'success': True,
                    'data': {
                        'assignment': assignment.to_dict(),
                        'added_questions': len(added_questions)
                    },
                    'message': 'Questions added successfully'
                }), 200
                
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'success': False,
                'message': str(e)
            }), 500
            
    return handle_request()
