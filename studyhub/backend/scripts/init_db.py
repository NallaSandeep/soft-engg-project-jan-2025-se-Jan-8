import os
import sys
import json
from datetime import datetime, timedelta

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(backend_dir)

from app import create_app, db
from app.models import (
    User, Course, CourseEnrollment,
    Week, Lecture, Assignment,
    Question, AssignmentQuestion, Resource,
    AssignmentSubmission, PersonalResource,
    ResourceFile
)

# Configuration
RECREATE_DB = False
VERBOSE = True

def log(message):
    """Helper function for logging to console if VERBOSE is True."""
    if VERBOSE:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")

def check_existing_data():
    """Check if there is existing data in the database."""
    try:
        user_count = User.query.count()
        course_count = Course.query.count()
        return user_count > 0 or course_count > 0
    except:
        return False

def create_users():
    """Create sample users with different roles."""
    users_data = {
        'admin': {
            'username': 'admin',
            'email': 'admin@studyhub.com',
            'password': 'admin123',
            'role': 'admin',
            'first_name': 'Admin',
            'last_name': 'User',
        },
        'teacher': {
            'username': 'teacher',
            'email': 'teacher@studyhub.com',
            'password': 'teacher123',
            'role': 'teacher',
            'first_name': 'John',
            'last_name': 'Smith',
        }
    }
    
    # Create sample student accounts
    for i in range(1, 6):
        users_data[f'student{i}'] = {
            'username': f'student{i}',
            'email': f'student{i}@studyhub.com',
            'password': 'student123',
            'role': 'student',
            'first_name': f'Student{i}',
            'last_name': f'User',
        }
    
    created_users = {}
    for key, data in users_data.items():
        user = User.query.filter_by(username=data['username']).first()
        if not user:
            user = User(
                username=data['username'],
                email=data['email'],
                role=data['role'],
                first_name=data['first_name'],
                last_name=data['last_name'],
                is_email_verified=True,
                is_active=True
            )
            user.password = data['password']
            db.session.add(user)
            log(f"Created {data['role']} user: {data['username']}")
        created_users[key] = user
    
    db.session.commit()
    return created_users

def create_sample_questions(teacher_id, course_id, week_id, lecture_id):
    """Create sample questions for a lecture."""
    return [
        Question(
            created_by_id=teacher_id,
            title='Sample MCQ Question',
            content='What is the capital of France?',
            type='MCQ',
            question_options=['London', 'Paris', 'Berlin', 'Madrid'],
            correct_answer=1,  # Paris
            points=1,
            explanation='Paris is the capital of France',
            course_id=course_id,
            week_id=week_id,
            lecture_id=lecture_id,
            status='active'
        ),
        Question(
            created_by_id=teacher_id,
            title='Sample MSQ Question',
            content='Which of these are programming languages?',
            type='MSQ',
            question_options=['Python', 'Coffee', 'Java', 'Tea'],
            correct_answer=[0, 2],  # Python and Java
            points=2,
            explanation='Python and Java are programming languages',
            course_id=course_id,
            week_id=week_id,
            lecture_id=lecture_id,
            status='active'
        ),
        Question(
            created_by_id=teacher_id,
            title='Sample Numeric Question',
            content='What is 2 + 2?',
            type='NUMERIC',
            question_options=[],
            correct_answer=4,
            points=1,
            explanation='Basic arithmetic',
            course_id=course_id,
            week_id=week_id,
            lecture_id=lecture_id,
            status='active'
        )
    ]

def create_courses(teacher):
    """Create sample courses."""
    courses_data = [
        {
            'code': 'CS101',
            'name': 'Introduction to Programming',
            'description': 'Learn Python programming fundamentals',
            'max_students': 30,
            'enrollment_type': 'open'
        },
        {
            'code': 'CS102',
            'name': 'Data Structures',
            'description': 'Learn fundamental data structures using Python',
            'max_students': 25,
            'enrollment_type': 'open'
        }
    ]
    
    created_courses = []
    for data in courses_data:
        course = Course.query.filter_by(code=data['code']).first()
        if not course:
            # Convert datetime to date for start_date and end_date
            start = datetime.now().date()
            end = (datetime.now() + timedelta(days=90)).date()
            
            course = Course(
                code=data['code'],
                name=data['name'],
                description=data['description'],
                created_by_id=teacher.id,
                max_students=data['max_students'],
                enrollment_type=data['enrollment_type'],
                start_date=start,
                end_date=end,
                is_active=True
            )
            db.session.add(course)
            log(f"Created course: {data['code']}")
            created_courses.append(course)
    
    db.session.commit()
    return created_courses

def create_course_content(course, teacher_id):
    """Create weeks, lectures, assignments, and resources for a course."""
    # Create weeks
    for week_num in range(1, 5):  # 4 weeks
        week = Week(
            course_id=course.id,
            number=week_num,
            title=f"Week {week_num}",
            description=f"Content for Week {week_num}",
            is_published=True
        )
        db.session.add(week)
        db.session.flush()

        # Create lectures
        for lecture_num in range(1, 3):
            lecture = Lecture(
                week_id=week.id,
                title=f"Lecture {lecture_num}",
                description=f"Content for Lecture {lecture_num}",
                order=lecture_num,
                youtube_url=f"https://youtube.com/watch?v=example{lecture_num}",
                transcript=f"Sample transcript for Lecture {lecture_num}",
                is_published=True
            )
            db.session.add(lecture)
            db.session.flush()

            # Create questions for this lecture
            questions = create_sample_questions(teacher_id, course.id, week.id, lecture.id)
            for question in questions:
                db.session.add(question)

            # Create assignments with different due dates
            due_date = datetime.now()
            if week_num <= 2:
                # Past assignments
                due_date = datetime.now() - timedelta(days=(7 * (2 - week_num)))
            else:
                # Future assignments
                due_date = datetime.now() + timedelta(days=(7 * (week_num - 2)))

            # Alternate between practice and graded assignments
            assignment_type = 'practice' if (week_num + lecture_num) % 2 == 0 else 'graded'
            
            assignment = Assignment(
                week_id=week.id,
                title=f"{'Practice' if assignment_type == 'practice' else 'Graded'} Assignment {week_num}.{lecture_num}",
                description=f"{'Practice questions' if assignment_type == 'practice' else 'Graded assessment'} for Lecture {lecture_num}",
                type=assignment_type,
                start_date=due_date - timedelta(days=7),
                due_date=due_date,
                late_submission_penalty=10.0,
                is_published=True
            )
            db.session.add(assignment)
            db.session.flush()

            # Link questions to assignment
            for i, question in enumerate(questions, 1):
                assignment_question = AssignmentQuestion(
                    assignment_id=assignment.id,
                    question_id=question.id,
                    order=i
                )
                db.session.add(assignment_question)

            # Create resources
            resource = Resource(
                course_id=course.id,
                week_id=week.id,
                title=f"Lecture {lecture_num} Slides",
                description=f"Slides for Lecture {lecture_num}",
                type='file',
                content=None,
                file_path=f"/static/resources/week{week_num}/lecture{lecture_num}/slides.pdf",
                file_type='application/pdf',
                file_size=0,
                created_by_id=teacher_id,
                is_active=True,
                is_public=True
            )
            db.session.add(resource)

    db.session.commit()
    log(f"Created content for course: {course.code}")

def create_sample_submissions(student_id, assignment_id):
    """Create sample assignment submissions with varying scores"""
    assignment = Assignment.query.get(assignment_id)
    if not assignment:
        return

    # Only create submissions for past assignments
    if assignment.due_date > datetime.now():
        return

    # For practice assignments, create multiple submissions with improving scores
    if assignment.type == 'practice':
        scores = [65.0, 75.0, 85.0]  # Multiple attempts showing improvement
        for attempt, score in enumerate(scores, 1):
            create_single_submission(student_id, assignment_id, score, attempt)
    else:
        # For graded assignments, create a single submission with a random score
        import random
        score = random.uniform(60.0, 95.0)
        create_single_submission(student_id, assignment_id, score, 1)

def create_single_submission(student_id, assignment_id, score, attempt=1):
    """Create a single assignment submission with the given score"""
    assignment = Assignment.query.get(assignment_id)
    
    # Create sample answers for each question
    answers = {}
    for idx, aq in enumerate(assignment.questions.all(), 1):
        if aq.question.type in ['MCQ', 'MSQ']:
            answers[str(idx)] = {
                'selected_option': 0 if aq.question.type == 'MCQ' else [0],
                'explanation': f'Attempt {attempt} explanation'
            }
        else:
            answers[str(idx)] = {
                'text': f'Attempt {attempt} answer',
                'explanation': f'Attempt {attempt} explanation'
            }

    # Calculate individual question scores based on total score
    num_questions = len(answers)
    base_question_score = score / num_questions
    question_scores = {str(i): round(base_question_score, 1) for i in range(1, num_questions + 1)}

    # Create submission with submission date based on attempt
    submission_date = datetime.now() - timedelta(days=3, hours=attempt)
    
    submission = AssignmentSubmission(
        assignment_id=assignment_id,
        student_id=student_id,
        answers=answers,
        score=round(score, 1),
        status='graded',
        question_scores=question_scores,
        feedback=f"Attempt {attempt} feedback - {'Good improvement!' if score > 80 else 'Keep practicing!'}"
    )
    submission.created_at = submission_date  # Set custom submission date
    db.session.add(submission)
    db.session.flush()
    log(f"Created sample submission (score: {score}) for assignment {assignment_id}")

def create_enrollments(users, courses):
    """Create course enrollments for users."""
    student1 = next(u for u in users.values() if u.username == 'student1')
    
    for course in courses:
        # Enroll all students
        for user in users.values():
            if user.role == 'student':
                enrollment = CourseEnrollment(
                    user_id=user.id,
                    course_id=course.id,
                    role='student',
                    status='active'
                )
                db.session.add(enrollment)
                log(f"Enrolled {user.username} in {course.code}")
        
        # Get all weeks for this course
        weeks = Week.query.filter_by(course_id=course.id).all()
        
        # Get all assignments for these weeks
        assignments = []
        for week in weeks:
            week_assignments = Assignment.query.filter_by(week_id=week.id).all()
            assignments.extend(week_assignments)
        
        # Only create submissions for some assignments for student1
        for idx, assignment in enumerate(assignments):
            # Only submit first 2 assignments in each course for student1
            if idx < 2:
                create_sample_submissions(student1.id, assignment.id)
    
    db.session.commit()

def create_ml_course(admin, users):
    """Create an Introduction to Machine Learning course with structured content."""
    course_code = "ML101"
    course_name = "Introduction to Machine Learning"
    description = "A foundational course covering supervised and unsupervised learning, neural networks, and model evaluation."

    # Check if course already exists
    course = Course.query.filter_by(code=course_code).first()
    if not course:
        course = Course(
            code=course_code,
            name=course_name,
            description=description,
            created_by_id=admin.id,
            max_students=50,
            enrollment_type='open',
            start_date=datetime.now().date(),
            end_date=(datetime.now() + timedelta(days=90)).date(),
            is_active=True
        )
        db.session.add(course)
        db.session.commit()
        log(f"Created course: {course_name}")

    # Create Weeks
    weeks = []
    for week_num, week_title in enumerate([
        "Week 1: Introduction to Machine Learning",
        "Week 2: Supervised Learning",
        "Week 3: Unsupervised Learning",
        "Week 4: Neural Networks and Deep Learning"
    ], start=1):
        week = Week(
            course_id=course.id,
            number=week_num,
            title=week_title,
            description=f"Topics covered: {week_title}.",
            is_published=True
        )
        db.session.add(week)
        db.session.flush()
        weeks.append(week)

    # Create Lectures
    lecture_data = [
        {
            "week": weeks[0],  
            "title": "What is Machine Learning?",
            "youtube_url": "https://www.youtube.com/watch?v=Gv9_4yMHFhI",
            "transcript": "Machine learning is the field of study that gives computers the ability to learn without being explicitly programmed."
        },
        {
            "week": weeks[0],
            "title": "Types of Machine Learning",
            "youtube_url": "https://www.youtube.com/watch?v=wnZbxye9xP4",
            "transcript": "In this video, we explore Supervised, Unsupervised, and Reinforcement Learning."
        },
        {
            "week": weeks[1],
            "title": "Supervised Learning: Linear Regression",
            "youtube_url": "https://www.youtube.com/watch?v=ZkjP5RJLQF4",
            "transcript": "Linear Regression is one of the simplest models for Supervised Learning."
        },
        {
            "week": weeks[2],
            "title": "Clustering in Machine Learning",
            "youtube_url": "https://www.youtube.com/watch?v=2uqWgtrL2M0",
            "transcript": "Clustering helps in finding patterns in data, often used in customer segmentation."
        }
    ]

    for lecture_info in lecture_data:
        lecture = Lecture(
            week_id=lecture_info["week"].id,
            title=lecture_info["title"],
            description=f"Lecture: {lecture_info['title']}",
            youtube_url=lecture_info["youtube_url"],
            transcript=lecture_info["transcript"],
            order=1,
            is_published=True
        )
        db.session.add(lecture)

    db.session.commit()
    log("Created weeks and lectures for Machine Learning course.")

    # Create Questions for the Question Bank
    questions = [
        Question(
            created_by_id=admin.id,
            title="What is Machine Learning?",
            content="What is the primary goal of machine learning?",
            type="MCQ",
            question_options=json.dumps(["Improve database queries", "Allow machines to learn from data", "Automate Excel calculations", "Replace programming"]),
            correct_answer=json.dumps(1),
            points=2,
            explanation="Machine learning allows computers to learn patterns from data instead of being explicitly programmed."
        ),
        Question(
            created_by_id=admin.id,
            title="Supervised vs. Unsupervised Learning",
            content="Which of the following statements are true about Supervised and Unsupervised Learning?",
            type="MSQ",
            question_options=json.dumps([
                "Supervised learning requires labeled data",
                "Unsupervised learning finds hidden patterns in data",
                "Supervised learning does not require labeled data",
                "Unsupervised learning predicts future outcomes"
            ]),
            correct_answer=json.dumps([0, 1]),
            points=3,
            explanation="Supervised learning requires labeled data, while unsupervised learning uncovers patterns."
        ),
        Question(
            created_by_id=admin.id,
            title="Linear Regression Calculation",
            content="If a linear regression model has the equation y = 2x + 3, what is y when x = 5?",
            type="NUMERIC",
            correct_answer=json.dumps(13),
            points=2,
            explanation="Substituting x=5 in the equation gives y = 2(5) + 3 = 13."
        )
    ]

    for question in questions:
        db.session.add(question)

    db.session.commit()
    log("Added ML questions to the question bank.")

    # Create Assignments
    assignments = [
        {
            "week": weeks[0],
            "title": "Intro to ML Assignment",
            "description": "Answer questions related to machine learning basics.",
            "type": "graded",
            "due_date": datetime.now() + timedelta(days=14),
            "questions": [questions[0], questions[1]]
        },
        {
            "week": weeks[1],
            "title": "Supervised Learning Quiz",
            "description": "Multiple-choice questions on Supervised Learning.",
            "type": "practice",
            "due_date": datetime.now() + timedelta(days=21),
            "questions": [questions[1], questions[2]]
        }
    ]

    for assignment_data in assignments:
        assignment = Assignment(
            week_id=assignment_data["week"].id,
            title=assignment_data["title"],
            description=assignment_data["description"],
            type=assignment_data["type"],
            due_date=assignment_data["due_date"],
            is_published=True
        )
        db.session.add(assignment)
        db.session.flush()  # Commit to get assignment ID

        for question in assignment_data["questions"]:
            assignment_question = AssignmentQuestion(
                assignment_id=assignment.id,
                question_id=question.id,
                order=1
            )
            db.session.add(assignment_question)

    db.session.commit()
    log("Created assignments for ML course.")

    # Enroll all students
    for student_key, student in users.items():
        if student.role == 'student':
            enrollment = CourseEnrollment(
                course_id=course.id,
                user_id=student.id,
                role='student',
                status='active'
            )
            db.session.add(enrollment)
            log(f"Enrolled {student.username} in Machine Learning course.")

    db.session.commit()
    log("ML course setup completed successfully!")

def create_personal_resources(db):
    """Create sample personal resources for users."""
    # This function is now empty as the old create_personal_knowledge_bases function has been removed.
    pass

def init_db():
    """Initialize the database with sample data."""
    app = create_app()
    with app.app_context():
        # Check if there is existing data
        if check_existing_data() and not RECREATE_DB:
            log("Database already contains data. Use RECREATE_DB=True to force recreation.")
            return

        log("Dropping all tables...")
        db.drop_all()
        
        log("Creating all tables...")
        db.create_all()
        
        log("Creating users...")
        users = create_users()
        
        log("Creating courses...")
        courses = create_courses(users['teacher'])
        
        log("Creating course content...")
        for course in courses:
            create_course_content(course, users['teacher'].id)
        
        log("Creating enrollments...")
        create_enrollments(users, courses)
        
        log("Creating ML course...")
        create_ml_course(users['admin'], users)
        
        log("Creating personal resources...")
        # Create personal resources for each student in each course
        students = [u for u in users.values() if u.role == 'student']
        for student in students:
            for course in courses:
                # Create a sample resource for each student in each course
                resource = PersonalResource(
                    user_id=student.id,
                    course_id=course.id,
                    name=f"Course Notes - {course.code}",
                    description=f"My personal notes and materials for {course.name}",
                    is_active=True,
                    settings={'visibility': 'private'}
                )
                db.session.add(resource)
                db.session.flush()

                # Add a sample note file
                note = ResourceFile(
                    resource_id=resource.id,
                    name="Week 1 Notes.txt",
                    type="note",
                    content="Important points from Week 1:\n- Key concepts\n- Practice problems\n- Study tips",
                    file_type="text/plain",
                    file_size=150
                )
                db.session.add(note)

                # Add a sample link file
                link = ResourceFile(
                    resource_id=resource.id,
                    name="Useful Resources.txt",
                    type="link",
                    content="https://example.com/study-guide\nhttps://example.com/practice",
                    file_type="text/plain",
                    file_size=80
                )
                db.session.add(link)
        
        db.session.commit()
        log("Database initialization complete!")
        log("\nTest Credentials:")
        log("Admin     - username: admin    password: admin123")
        log("Teacher   - username: teacher  password: teacher123")
        log("Students  - username: student1 password: student123")
        log("           username: student2 password: student123")
        log("           ... up to student5")

def init_personal_resources():
    """Initialize only personal resources without affecting other data."""
    app = create_app()
    with app.app_context():
        log("Creating personal resources...")
        # Get existing students and courses
        students = User.query.filter_by(role='student').all()
        courses = Course.query.all()
        
        for student in students:
            for course in courses:
                # Check if student is enrolled in the course
                enrollment = CourseEnrollment.query.filter_by(
                    user_id=student.id,
                    course_id=course.id,
                    status='active'
                ).first()
                
                if not enrollment:
                    continue
                
                # Create a sample resource for each student in each course
                resource = PersonalResource(
                    user_id=student.id,
                    course_id=course.id,
                    name=f"Course Notes - {course.code}",
                    description=f"My personal notes and materials for {course.name}",
                    is_active=True,
                    settings={'visibility': 'private'}
                )
                db.session.add(resource)
                db.session.flush()

                # Add a sample note file
                note = ResourceFile(
                    resource_id=resource.id,
                    name="Week 1 Notes.txt",
                    type="note",
                    content="Important points from Week 1:\n- Key concepts\n- Practice problems\n- Study tips",
                    file_type="text/plain",
                    file_size=150
                )
                db.session.add(note)

                # Add a sample link file
                link = ResourceFile(
                    resource_id=resource.id,
                    name="Useful Resources.txt",
                    type="link",
                    content="https://example.com/study-guide\nhttps://example.com/practice",
                    file_type="text/plain",
                    file_size=80
                )
                db.session.add(link)
        
        db.session.commit()
        log("Personal resources initialization complete!")

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'personal_resources':
        init_personal_resources()
    else:
        init_db()
