from marshmallow import Schema, fields, validate, ValidationError
from datetime import datetime

# Base Schemas
class PaginationSchema(Schema):
    page = fields.Int(missing=1, validate=validate.Range(min=1))
    per_page = fields.Int(missing=10, validate=validate.Range(min=1, max=100))

# Auth Schemas
class LoginSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True)

# Course Schemas
class CourseCreateSchema(Schema):
    code = fields.Str(required=True, validate=validate.Length(min=2, max=20))
    name = fields.Str(required=True, validate=validate.Length(min=3, max=100))
    description = fields.Str(required=True)
    start_date = fields.Date(allow_none=True)
    end_date = fields.Date(allow_none=True)
    max_students = fields.Int(allow_none=True, validate=validate.Range(min=1))
    enrollment_type = fields.Str(validate=validate.OneOf(['open', 'closed', 'invite_only']))

class WeekCreateSchema(Schema):
    number = fields.Int(required=True, validate=validate.Range(min=1))
    title = fields.Str(required=True, validate=validate.Length(min=3, max=200))
    description = fields.Str(allow_none=True)
    is_published = fields.Bool(missing=False)

class LectureCreateSchema(Schema):
    title = fields.Str(required=True, validate=validate.Length(min=3, max=200))
    description = fields.Str(allow_none=True)
    youtube_url = fields.Str(required=True, validate=validate.URL())
    transcript = fields.Str(allow_none=True)
    is_published = fields.Bool(missing=False)

# Assignment Schemas
class QuestionCreateSchema(Schema):
    title = fields.Str(required=True, validate=validate.Length(min=3, max=200))
    content = fields.Str(required=True)
    type = fields.Str(required=True, validate=validate.OneOf(['multiple_choice', 'true_false', 'text']))
    correct_answer = fields.Str(required=True)  # JSON string
    points = fields.Int(missing=1, validate=validate.Range(min=1))
    explanation = fields.Str(allow_none=True)

class AssignmentCreateSchema(Schema):
    title = fields.Str(required=True, validate=validate.Length(min=3, max=200))
    description = fields.Str(allow_none=True)
    type = fields.Str(required=True, validate=validate.OneOf(['practice', 'graded']))
    due_date = fields.DateTime(allow_none=True)
    is_published = fields.Bool(missing=False)

class AssignmentQuestionSchema(Schema):
    question_ids = fields.List(fields.Int(), required=True, validate=validate.Length(min=1))

def validate_request(schema_class):
    """Decorator to validate request data against a schema"""
    def decorator(f):
        def wrapper(*args, **kwargs):
            schema = schema_class()
            try:
                # Handle both form data and JSON
                if request.is_json:
                    data = request.get_json()
                else:
                    data = request.form.to_dict()
                
                # Validate and get the cleaned data
                validated_data = schema.load(data)
                
                # Add validated data to request object
                request.validated_data = validated_data
                
                return f(*args, **kwargs)
            except ValidationError as err:
                return jsonify({
                    'success': False,
                    'message': 'Validation error',
                    'errors': err.messages
                }), 400
        wrapper.__name__ = f.__name__
        return wrapper
    return decorator 