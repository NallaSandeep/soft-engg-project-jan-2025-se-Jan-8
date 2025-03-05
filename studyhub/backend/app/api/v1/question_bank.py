"""Question bank management endpoints."""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ...models import Question, Course, Week, Lecture
from ...utils.auth import ta_required
from ... import db

question_bank_bp = Blueprint('question_bank', __name__)

# Constants for validation
VALID_QUESTION_TYPES = ['MCQ', 'MSQ', 'NUMERIC']
VALID_QUESTION_STATUS = ['draft', 'active', 'inactive']

def validate_question_data(data, check_required=True):
    """Validate question data"""
    errors = []
    
    # Check required fields
    if check_required:
        required_fields = ['title', 'content', 'type', 'correct_answer']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            errors.append(f"Missing required fields: {', '.join(missing_fields)}")
    
    # Validate type if provided
    if 'type' in data:
        if data['type'] not in VALID_QUESTION_TYPES:
            errors.append(f"Invalid question type. Must be one of: {', '.join(VALID_QUESTION_TYPES)}")
        
        # Validate options for MCQ/MSQ
        if data['type'] in ['MCQ', 'MSQ'] and not data.get('question_options'):
            errors.append(f"{data['type']} questions must have options")
    
    # Validate status if provided
    if 'status' in data and data['status'] not in VALID_QUESTION_STATUS:
        errors.append(f"Invalid status. Must be one of: {', '.join(VALID_QUESTION_STATUS)}")
    
    # Validate points if provided
    if 'points' in data and (not isinstance(data['points'], int) or data['points'] < 1):
        errors.append("Points must be a positive integer")
    
    return errors

@question_bank_bp.route('/questions', methods=['GET'])
@jwt_required()
@ta_required
def list_questions():
    """List questions with filters"""
    try:
        # Get query parameters
        status = request.args.get('status')
        q_type = request.args.get('type')
        difficulty = request.args.get('difficulty')
        search = request.args.get('search')
        course_id = request.args.get('course_id', type=int)
        week_id = request.args.get('week_id', type=int)
        lecture_id = request.args.get('lecture_id', type=int)
        
        # Validate filters
        if status and status not in VALID_QUESTION_STATUS:
            return jsonify({
                'success': False,
                'message': f"Invalid status. Must be one of: {', '.join(VALID_QUESTION_STATUS)}"
            }), 400
            
        if q_type and q_type not in VALID_QUESTION_TYPES:
            return jsonify({
                'success': False,
                'message': f"Invalid type. Must be one of: {', '.join(VALID_QUESTION_TYPES)}"
            }), 400
            
        if difficulty and difficulty not in ['easy', 'medium', 'hard']:
            return jsonify({
                'success': False,
                'message': "Invalid difficulty. Must be one of: easy, medium, hard"
            }), 400
        
        # Build query
        query = Question.query
        
        if status:
            query = query.filter(Question.status == status)
        if q_type:
            query = query.filter(Question.type == q_type)
        if difficulty:
            query = query.filter(Question.difficulty == difficulty)
        if course_id:
            query = query.filter(Question.course_id == course_id)
        if week_id:
            query = query.filter(Question.week_id == week_id)
        if lecture_id:
            query = query.filter(Question.lecture_id == lecture_id)
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                db.or_(
                    Question.title.ilike(search_term),
                    Question.content.ilike(search_term)
                )
            )
            
        # Execute query
        questions = query.all()
        
        return jsonify({
            'success': True,
            'data': [q.to_dict() for q in questions]
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@question_bank_bp.route('/questions', methods=['POST'])
@jwt_required()
@ta_required
def create_question():
    """Create a new question"""
    try:
        data = request.get_json()
        
        # Validate data
        errors = validate_question_data(data)
        if errors:
            return jsonify({
                'success': False,
                'message': 'Validation failed',
                'errors': errors
            }), 400
        
        # Create question
        question = Question(
            created_by_id=get_jwt_identity(),
            title=data['title'],
            content=data['content'],
            type=data['type'],
            question_options=data.get('question_options'),
            correct_answer=data['correct_answer'],
            points=data.get('points', 1),
            explanation=data.get('explanation'),
            course_id=data.get('course_id'),
            week_id=data.get('week_id'),
            lecture_id=data.get('lecture_id'),
            status=data.get('status', 'draft')
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

@question_bank_bp.route('/questions/<int:question_id>', methods=['GET'])
@jwt_required()
@ta_required
def get_question(question_id):
    """Get a specific question"""
    try:
        question = Question.query.get_or_404(question_id)
        
        return jsonify({
            'success': True,
            'data': question.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@question_bank_bp.route('/questions/<int:question_id>', methods=['PUT'])
@jwt_required()
@ta_required
def update_question(question_id):
    """Update a question"""
    try:
        question = Question.query.get_or_404(question_id)
        data = request.get_json()
        
        # Validate data
        errors = validate_question_data(data, check_required=False)
        if errors:
            return jsonify({
                'success': False,
                'message': 'Validation failed',
                'errors': errors
            }), 400
        
        # Update fields
        for field in ['title', 'content', 'type', 'question_options', 'correct_answer', 
                     'points', 'explanation', 'course_id', 'week_id', 
                     'lecture_id', 'status']:
            if field in data:
                setattr(question, field, data[field])
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': question.to_dict(),
            'message': 'Question updated successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@question_bank_bp.route('/questions/<int:question_id>', methods=['DELETE'])
@jwt_required()
@ta_required
def delete_question(question_id):
    """Delete a question"""
    try:
        question = Question.query.get_or_404(question_id)
        
        # Check if question is used in any assignments
        if question.assignments.count() > 0:
            return jsonify({
                'success': False,
                'message': 'Cannot delete question as it is used in assignments'
            }), 400
            
        db.session.delete(question)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Question deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@question_bank_bp.route('/questions/batch', methods=['POST'])
@jwt_required()
@ta_required
def batch_create_questions():
    """Create multiple questions at once"""
    try:
        data = request.get_json()
        if not isinstance(data, list):
            return jsonify({
                'success': False,
                'message': 'Expected a list of questions'
            }), 400
            
        questions = []
        errors = []
        
        for idx, q_data in enumerate(data):
            # Validate data
            validation_errors = validate_question_data(q_data)
            if validation_errors:
                errors.append({
                    'index': idx,
                    'title': q_data.get('title', 'Untitled'),
                    'errors': validation_errors
                })
                continue
                
            question = Question(
                created_by_id=get_jwt_identity(),
                title=q_data['title'],
                content=q_data['content'],
                type=q_data['type'],
                question_options=q_data.get('question_options'),
                correct_answer=q_data['correct_answer'],
                points=q_data.get('points', 1),
                explanation=q_data.get('explanation'),
                course_id=q_data.get('course_id'),
                week_id=q_data.get('week_id'),
                lecture_id=q_data.get('lecture_id'),
                status=q_data.get('status', 'draft')
            )
            questions.append(question)
        
        if errors:
            return jsonify({
                'success': False,
                'message': 'Validation failed for some questions',
                'errors': errors
            }), 400
            
        db.session.add_all(questions)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': [q.to_dict() for q in questions],
            'message': f'Successfully created {len(questions)} questions'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500 