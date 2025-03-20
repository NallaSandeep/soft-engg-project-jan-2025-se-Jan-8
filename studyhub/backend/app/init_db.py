def create_personal_resources(db):
    """Create sample personal resources for testing."""
    from app.models import User, Course, PersonalResource, ResourceFile
    
    # Get all students
    students = User.query.filter_by(role='student').all()
    courses = Course.query.all()
    
    # Sample resource types and content
    resource_templates = [
        {
            'name': 'Lecture Notes',
            'description': 'My personal notes from lectures',
            'files': [
                {
                    'name': 'Week 1 Notes.txt',
                    'type': 'note',
                    'content': 'Key points from week 1:\n- Introduction to the course\n- Basic concepts\n- Important definitions',
                    'file_type': 'text/plain',
                    'file_size': 150
                },
                {
                    'name': 'Week 2 Summary.txt',
                    'type': 'note',
                    'content': 'Summary of week 2:\n- Advanced topics\n- Practice problems\n- Study tips',
                    'file_type': 'text/plain',
                    'file_size': 120
                }
            ]
        },
        {
            'name': 'Study Materials',
            'description': 'Collection of reference materials and links',
            'files': [
                {
                    'name': 'Important Links.txt',
                    'type': 'link',
                    'content': 'https://example.com/study-guide\nhttps://example.com/practice-problems',
                    'file_type': 'text/plain',
                    'file_size': 80
                },
                {
                    'name': 'Study Schedule.txt',
                    'type': 'note',
                    'content': 'Monday: Review lectures\nTuesday: Practice problems\nWednesday: Group study',
                    'file_type': 'text/plain',
                    'file_size': 100
                }
            ]
        },
        {
            'name': 'Assignment Drafts',
            'description': 'Working drafts and notes for assignments',
            'files': [
                {
                    'name': 'Assignment 1 Draft.txt',
                    'type': 'note',
                    'content': 'Draft ideas for Assignment 1:\n- Main approach\n- Key algorithms\n- Implementation plan',
                    'file_type': 'text/plain',
                    'file_size': 200
                }
            ]
        },
        {
            'name': 'Exam Preparation',
            'description': 'Study materials and practice questions for exams',
            'files': [
                {
                    'name': 'Practice Questions.txt',
                    'type': 'note',
                    'content': 'Sample questions:\n1. Explain the concept of X\n2. Solve problem Y\n3. Compare approaches A and B',
                    'file_type': 'text/plain',
                    'file_size': 250
                },
                {
                    'name': 'Formula Sheet.txt',
                    'type': 'note',
                    'content': 'Important formulas:\n- Formula 1\n- Formula 2\n- Formula 3',
                    'file_type': 'text/plain',
                    'file_size': 150
                }
            ]
        }
    ]
    
    # Create resources for each student in each course
    for student in students:
        for course in courses:
            # Check if student is enrolled in the course
            enrollment = student.enrollments.filter_by(course_id=course.id).first()
            if not enrollment:
                continue
                
            # Create 2-3 resources per course for each student
            for template in resource_templates[:3]:  # Use first 3 templates
                resource = PersonalResource(
                    user_id=student.id,
                    course_id=course.id,
                    name=f"{template['name']} - {course.code}",
                    description=template['description'],
                    is_active=True,
                    settings={'visibility': 'private'}
                )
                db.session.add(resource)
                db.session.flush()  # Get the resource ID
                
                # Create associated files
                for file_template in template['files']:
                    file = ResourceFile(
                        resource_id=resource.id,
                        name=file_template['name'],
                        type=file_template['type'],
                        content=file_template['content'],
                        file_type=file_template['file_type'],
                        file_size=file_template['file_size']
                    )
                    db.session.add(file)
    
    db.session.commit()
    print("Created sample personal resources for all students")

def init_db():
    """Initialize the database with sample data."""
    db.drop_all()
    db.create_all()
    
    create_users(db)
    create_courses(db)
    create_course_content(db)
    create_assignments(db)
    create_personal_resources(db)  # Add this line to create personal resources
    
    db.session.commit() 