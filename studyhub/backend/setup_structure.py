import os
import shutil

def create_directory(path):
    """Create directory if it doesn't exist."""
    if not os.path.exists(path):
        os.makedirs(path)

def create_file(path, content=''):
    """Create file with optional content if it doesn't exist."""
    if not os.path.exists(path):
        with open(path, 'w') as f:
            f.write(content)

def setup_structure():
    """Set up the project directory structure."""
    # Root level directories
    create_directory('app')
    create_directory('migrations')
    create_directory('tests')
    create_directory('logs')
    create_directory('uploads')  # This will be created in the backend directory
    
    # Create a .gitkeep file in the uploads directory to track it in git
    create_file('uploads/.gitkeep')

    # App subdirectories
    create_directory('app/models')
    create_directory('app/api/v1')
    create_directory('app/utils')

    # Tests subdirectories
    create_directory('tests/test_models')
    create_directory('tests/test_api')

    # Create necessary __init__.py files
    init_files = [
        'app/__init__.py',
        'app/models/__init__.py',
        'app/api/__init__.py',
        'app/api/v1/__init__.py',
        'app/utils/__init__.py',
        'tests/__init__.py',
        'tests/test_models/__init__.py',
        'tests/test_api/__init__.py',
    ]

    for init_file in init_files:
        create_file(init_file)

    # Create placeholder files for models
    model_files = [
        'base.py',
        'user.py',
        'course.py',
        'course_enrollment.py',
        'resource.py',
        'resource_vector.py',
        'assignment.py',
        'assignment_submission.py',
        'study_progress.py',
    ]

    for model_file in model_files:
        create_file(f'app/models/{model_file}')

    # Create placeholder files for API routes
    api_files = [
        'auth.py',
        'users.py',
        'courses.py',
        'resources.py',
        'assignments.py',
        'progress.py',
    ]

    for api_file in api_files:
        create_file(f'app/api/v1/{api_file}')

    # Create utility files
    util_files = [
        'decorators.py',
        'validators.py',
        'helpers.py',
    ]

    for util_file in util_files:
        create_file(f'app/utils/{util_file}')

    print("Directory structure created successfully!")

if __name__ == '__main__':
    setup_structure() 