"""
Database Initialization Script
------------------------------
This script initializes the StudyHub database with sample data for development and testing.
It creates a rich set of interconnected data, including:
- Users (admin, teachers, students)
- Courses with more extensive content structures
- Multiple weeks/lectures/resources
- Assignments (practice and graded) with detailed questions
- Student submissions
- Personal learning resources
"""

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
    ResourceFile, LectureProgress
)

# Configuration
RECREATE_DB = True  # Set to True to force recreation of database
VERBOSE = True      # Enable detailed logging

def log(message):
    """Helper function for logging to console if VERBOSE is True."""
    if VERBOSE:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")

def check_existing_data():
    """
    Check if there is existing data in the database.
    Returns True if either users or courses exist.
    Used to prevent accidental data recreation.
    """
    try:
        user_count = User.query.count()
        course_count = Course.query.count()
        return user_count > 0 or course_count > 0
    except:
        return False

def create_users():
    """
    Create sample users with different roles.
    Creates:
    - 1 admin user
    - 1 teacher
    - 5 students
    """
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
            'last_name': 'User',
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

def create_sample_questions(teacher_id, course_id, week_id, lecture_id, advanced=False):
    """
    Create sample questions for lectures and assignments.
    If 'advanced' is True, create some more advanced/complex questions.
    """
    base_questions = [
        {
            'title': 'Understanding Core Concepts',
            'content': 'Which of the following best describes the main purpose of this concept?',
            'type': 'MCQ',
            'options': [
                'To simplify complex processes',
                'To optimize system performance',
                'To improve code readability',
                'To reduce memory usage'
            ],
            'correct_answer': 0,
            'points': 2,
            'explanation': 'It is primarily about simplifying complex processes.'
        },
        {
            'title': 'Technical Implementation',
            'content': 'What is the most appropriate approach for implementing this feature?',
            'type': 'MCQ',
            'options': [
                'Using a recursive algorithm',
                'Implementing an iterative solution',
                'Applying dynamic programming',
                'Using a greedy approach'
            ],
            'correct_answer': 2,
            'points': 3,
            'explanation': 'Dynamic programming is a typical optimization approach.'
        },
        {
            'title': 'Best Practices',
            'content': 'Which of the following are best practices? (Select all that apply)',
            'type': 'MSQ',
            'options': [
                'Writing comprehensive documentation',
                'Using meaningful variable names',
                'Avoiding code duplication',
                'Ignoring edge cases'
            ],
            'correct_answer': [0, 1, 2],
            'points': 3,
            'explanation': 'Documentation, meaningful naming, and DRY principle are standard best practices.'
        },
        {
            'title': 'System Components',
            'content': 'Which components are essential for a robust system? (Select all that apply)',
            'type': 'MSQ',
            'options': [
                'Data validation module',
                'Error handling system',
                'User interface',
                'External API'
            ],
            'correct_answer': [0, 1, 2],
            'points': 2,
            'explanation': 'Data validation, error handling, and UI are essential.'
        },
        {
            'title': 'Performance Analysis',
            'content': 'If the system processes 100 requests/second, how many requests in 5 minutes?',
            'type': 'NUMERIC',
            'correct_answer': 30000,
            'points': 2,
            'explanation': '100 * 60 * 5 = 30000.'
        },
        {
            'title': 'Resource Utilization',
            'content': 'If each process uses 2.5 MB of memory, how much total memory for 10 processes?',
            'type': 'NUMERIC',
            'correct_answer': 25,
            'points': 1,
            'explanation': '2.5 * 10 = 25 MB.'
        }
    ]
    if advanced:
        # Add extra advanced questions
        base_questions.extend([
            {
                'title': 'Advanced Data Structure Complexity',
                'content': 'Which of the following statements about B-Trees is correct?',
                'type': 'MCQ',
                'options': [
                    'B-Trees only store data in leaf nodes.',
                    'B-Trees guarantee O(1) lookup in all cases.',
                    'All leaves appear at the same level in a B-Tree.',
                    'B-Trees cannot be used as a database index.'
                ],
                'correct_answer': 2,
                'points': 4,
                'explanation': 'One hallmark of B-Trees is that all leaves are at the same level.'
            },
            {
                'title': 'Algorithmic Efficiency',
                'content': 'Select all statements that describe the benefits of using a Segment Tree. (Select all)',
                'type': 'MSQ',
                'options': [
                    'Enables O(1) time updates for array elements',
                    'Allows range queries (e.g., sum, min) in O(log n)',
                    'Requires O(n) space for storing segment trees',
                    'Provides offline query processing only'
                ],
                'correct_answer': [1, 2],
                'points': 4,
                'explanation': 'Segment Trees typically have O(log n) range queries and O(n) space usage.'
            },
            {
                'title': 'ML Model Evaluation',
                'content': 'If a model processes 200 samples/minute, how many samples after 3 hours?',
                'type': 'NUMERIC',
                'correct_answer': 36000,
                'points': 2,
                'explanation': '200 * 60 * 3 = 36,000 samples.'
            }
        ])
    questions = []
    for data in base_questions:
        question = Question(
            created_by_id=teacher_id,
            title=data['title'],
            content=data['content'],
            type=data['type'],
            question_options=data.get('options', []),
            correct_answer=data['correct_answer'],
            points=data['points'],
            explanation=data['explanation'],
            course_id=course_id,
            week_id=week_id,
            lecture_id=lecture_id,
            status='active'
        )
        questions.append(question)
    return questions

def create_courses(teacher):
    """
    Create initial sample courses (CS101, CS102).
    Each has a few weeks and some lectures.
    """
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
    """
    Create course content for a given course:
    - 4 weeks, each with multiple lectures
    - Practice/graded assignments
    - Additional resources
    - Sample questions
    """
    # Updated YouTube URLs for CS101 & CS102
    # (Week1: Introduction, Practical Apps; Week2: Advanced Tech, etc.)
    weeks_content = [
        # Week 1
        [
            {
                'type': 'youtube',
                'url': 'https://www.youtube.com/watch?v=8ext9G7xspg',  # New link
                'title': 'Course Introduction',
                'description': 'Overview of course objectives',
                'transcript': 'Welcome to the course. We will explore...'
            },
            {
                'type': 'pdf',
                'file_path': 'Week1_Lecture2.pdf',
                'title': 'Fundamental Concepts',
                'description': 'Core concepts and terminology',
                'transcript': 'Key aspects are variables, functions, etc.'
            },
            {
                'type': 'youtube',
                'url': 'https://www.youtube.com/watch?v=ea8BRGxGmlA',  # New link
                'title': 'Practical Applications',
                'description': 'Real-world examples',
                'transcript': 'How these concepts apply in practice...'
            }
        ],
        # Week 2
        [
            {
                'type': 'youtube',
                'url': 'https://www.youtube.com/watch?v=sugvnHA7ElY',  # New link
                'title': 'Advanced Techniques',
                'description': 'Deeper dive into advanced methodologies',
                'transcript': 'Exploring deeper topics...'
            },
            {
                'type': 'pdf',
                'file_path': 'Week2_Lecture2.pdf',
                'title': 'Case Studies',
                'description': 'Real-world analysis',
                'transcript': 'Examining real-world usage...'
            }
        ],
        # Week 3
        [
            {
                'type': 'youtube',
                'url': 'https://www.youtube.com/watch?v=bXJx1bFoHDU',  # New link
                'title': 'Implementation Strategies',
                'description': 'Hands-on guide',
                'transcript': 'Implementation steps for the concept...'
            },
            {
                'type': 'pdf',
                'file_path': 'Week3_Lecture2.pdf',
                'title': 'Best Practices',
                'description': 'Industry standards and best practices',
                'transcript': 'Typical best practices in the field...'
            },
            {
                'type': 'youtube',
                'url': 'https://www.youtube.com/watch?v=5qQQ3yzbKp8',  # New link
                'title': 'Common Pitfalls',
                'description': 'Common mistakes to avoid',
                'transcript': 'Mistakes and how to address them...'
            }
        ],
        # Week 4
        [
            {
                'type': 'youtube',
                'url': 'https://www.youtube.com/watch?v=1Lfv5tUGsn8',  # New link
                'title': 'Advanced Applications',
                'description': 'Complex real-world applications',
                'transcript': 'In this final week, we will tackle advanced scenarios...'
            },
            {
                'type': 'pdf',
                'file_path': 'Week4_Lecture2.pdf',
                'title': 'Future Trends',
                'description': 'Emerging trends',
                'transcript': 'An overview of future directions...'
            }
        ]
    ]
    
    for week_num, lectures_data in enumerate(weeks_content, 1):
        week = Week(
            course_id=course.id,
            number=week_num,
            title=f'Week {week_num}',
            description=f'Content for Week {week_num}',
            is_published=True
        )
        db.session.add(week)
        db.session.flush()
        
        # Create lectures for the week
        for lecture_num, lecture_data in enumerate(lectures_data, 1):
            lecture = Lecture(
                week_id=week.id,
                lecture_number=lecture_num,
                title=lecture_data['title'],
                description=lecture_data['description'],
                content_type=lecture_data['type'],
                file_path=lecture_data.get('file_path', ''),
                youtube_url=lecture_data.get('url', ''),
                transcript=lecture_data['transcript'],
                order=lecture_num,
                is_published=True
            )
            db.session.add(lecture)
            
            # Sample questions for each lecture
            # Use advanced questions only in later weeks
            advanced = (week_num > 2)
            questions = create_sample_questions(teacher_id, course.id, week.id, lecture.id, advanced=advanced)
            for question in questions:
                db.session.add(question)

            # Create assignments (last lecture of each week triggers assignment)
            if lecture_num == len(lectures_data): 
                due_date = datetime.now() + timedelta(days=7 * week_num)
                assignment_type = 'practice' if week_num % 2 == 0 else 'graded'
                
                assignment = Assignment(
                    week_id=week.id,
                    title=f"{'Practice' if assignment_type == 'practice' else 'Graded'} Assignment - Week {week_num}",
                    description=f"Complete this {assignment_type} assignment to test your understanding of Week {week_num} concepts.",
                    type=assignment_type,
                    start_date=datetime.now(),
                    due_date=due_date,
                    late_submission_penalty=10.0 if assignment_type == 'graded' else 0.0,
                    is_published=True
                )
                db.session.add(assignment)
                db.session.flush()

                # Link questions to assignment
                for i, q in enumerate(questions, 1):
                    assignment_question = AssignmentQuestion(
                        assignment_id=assignment.id,
                        question_id=q.id,
                        order=i
                    )
                    db.session.add(assignment_question)

            # Create a resource for each lecture
            resource = Resource(
                course_id=course.id,
                week_id=week.id,
                title=f"{lecture_data['title']} - Materials",
                description=f"Supplementary materials for {lecture_data['title']}",
                type='file',
                content=None,
                file_path=f"/static/resources/week{week_num}/lecture{lecture_num}/materials.pdf",
                file_type='application/pdf',
                file_size=1024 * 1024,
                created_by_id=teacher_id,
                is_active=True,
                is_public=True
            )
            db.session.add(resource)
    
    db.session.commit()

def create_sample_submissions(student_id, assignment_id):
    """
    Create realistic assignment submissions, with multiple attempts for practice,
    single attempt for graded, varying scores, etc.
    """
    assignment = Assignment.query.get(assignment_id)
    if not assignment:
        return

    # Only create submissions if assignment due date is in the past
    if assignment.due_date > datetime.now():
        return

    if assignment.type == 'practice':
        scores = [65.0, 75.0, 85.0]
        for attempt, score in enumerate(scores, 1):
            create_single_submission(student_id, assignment_id, score, attempt)
    else:
        import random
        score = random.uniform(60.0, 95.0)
        create_single_submission(student_id, assignment_id, score, 1)

def create_single_submission(student_id, assignment_id, score, attempt=1):
    """
    Create a single assignment submission with question-wise answers and partial scoring.
    """
    assignment = Assignment.query.get(assignment_id)
    
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

    num_questions = len(answers)
    base_question_score = score / num_questions
    question_scores = {
        str(i): round(base_question_score, 1) for i in range(1, num_questions + 1)
    }

    submission_date = datetime.now() - timedelta(days=3, hours=attempt)
    
    submission = AssignmentSubmission(
        assignment_id=assignment_id,
        user_id=student_id,
        answers=answers,
        score=round(score, 1),
        question_scores=question_scores,
        submitted_at=submission_date,
        status='graded'
    )
    
    db.session.add(submission)
    db.session.commit()
    log(f"Created submission for assignment {assignment_id}, student {student_id}, score {score}")

def create_enrollments(users, courses):
    """
    Enroll all students in each of the given courses and create some sample submissions.
    """
    student1 = next(u for u in users.values() if u.username == 'student1')
    
    for course in courses:
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
        
        # For each assignment in each course, create submissions for student1
        weeks = Week.query.filter_by(course_id=course.id).all()
        assignments = []
        for week in weeks:
            assignments += Assignment.query.filter_by(week_id=week.id).all()
        
        # Make submissions for the first few assignments
        for idx, assignment in enumerate(assignments):
            if idx < 3:  # only submit a few
                create_sample_submissions(student1.id, assignment.id)

    db.session.commit()

def create_ml_course(admin, users):
    """
    Create a Machine Learning course with some advanced content.
    """
    course_code = "ML101"
    course_name = "Introduction to Machine Learning"
    description = "A foundational course covering supervised, unsupervised learning, and neural networks."

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
            end_date=(datetime.now() + timedelta(days=120)).date(),
            is_active=True
        )
        db.session.add(course)
        db.session.commit()
        log(f"Created course: {course_code}")

    # Create 4 weeks for ML
    weeks_titles = [
        "Week 1: Introduction to ML",
        "Week 2: Supervised Learning",
        "Week 3: Unsupervised Learning",
        "Week 4: Neural Networks & Deep Learning"
    ]
    weeks = []
    for i, title in enumerate(weeks_titles, 1):
        w = Week(
            course_id=course.id,
            number=i,
            title=title,
            description=f"Topics covered: {title}",
            is_published=True
        )
        db.session.add(w)
        db.session.flush()
        weeks.append(w)

    # Updated sample lectures with new YouTube links
    lecture_data = [
        {
            "week": weeks[0],
            "title": "What is Machine Learning?",
            "youtube_url": "https://www.youtube.com/watch?v=GwIo3gDZCVQ",
            "transcript": "Machine learning is the field of study that gives computers the ability to learn...",
            "content_type": "youtube",
            "lecture_number": 1
        },
        {
            "week": weeks[0],
            "title": "Types of Machine Learning",
            "youtube_url": "https://www.youtube.com/watch?v=UKdQjQX1Pko",
            "transcript": "Supervised, Unsupervised, and Reinforcement Learning...",
            "content_type": "youtube",
            "lecture_number": 2
        },
        {
            "week": weeks[1],
            "title": "Linear Regression Fundamentals",
            "youtube_url": "https://www.youtube.com/watch?v=nk2CQITm_eo",
            "transcript": "Linear Regression basics...",
            "content_type": "youtube",
            "lecture_number": 1
        },
        {
            "week": weeks[1],
            "title": "Classification Overview",
            "youtube_url": "https://www.youtube.com/watch?v=pN6jk0uUrD8",
            "transcript": "Classification fundamentals with logistic regression, SVM...",
            "content_type": "youtube",
            "lecture_number": 2
        },
        {
            "week": weeks[2],
            "title": "Clustering in ML",
            "youtube_url": "https://www.youtube.com/watch?v=_aWzGGNrcic",
            "transcript": "Clustering helps in finding patterns in data...",
            "content_type": "youtube",
            "lecture_number": 1
        },
        {
            "week": weeks[3],
            "title": "Intro to Neural Networks",
            "youtube_url": "https://www.youtube.com/watch?v=aircAruvnKk",
            "transcript": "Neural networks are computational models...",
            "content_type": "youtube",
            "lecture_number": 1
        }
    ]
    for ld in lecture_data:
        lecture = Lecture(
            week_id=ld["week"].id,
            lecture_number=ld["lecture_number"],
            title=ld["title"],
            description=f"Lecture: {ld['title']}",
            content_type=ld["content_type"],
            youtube_url=ld["youtube_url"],
            transcript=ld["transcript"],
            order=ld["lecture_number"],
            is_published=True
        )
        db.session.add(lecture)
        db.session.flush()

        # Add questions to each lecture (some advanced)
        adv = (ld["week"].number > 1)
        questions = create_sample_questions(admin.id, course.id, ld["week"].id, lecture.id, advanced=adv)
        for q in questions:
            db.session.add(q)

    db.session.commit()
    log("Created ML lectures and questions.")

    # Assignments
    assignments = [
        {
            "week": weeks[0],
            "title": "Intro to ML Assignment",
            "description": "Basic ML concepts check",
            "type": "graded",
            "due_date": datetime.now() + timedelta(days=14)
        },
        {
            "week": weeks[1],
            "title": "Supervised Learning Quiz",
            "description": "Key topics in regression and classification",
            "type": "practice",
            "due_date": datetime.now() + timedelta(days=21)
        },
        {
            "week": weeks[2],
            "title": "Unsupervised Methods Assignment",
            "description": "Clustering and dimensionality reduction tasks",
            "type": "graded",
            "due_date": datetime.now() + timedelta(days=28)
        },
        {
            "week": weeks[3],
            "title": "Neural Nets Quiz",
            "description": "Basics of MLP, activation functions, forward/backprop",
            "type": "practice",
            "due_date": datetime.now() + timedelta(days=35)
        }
    ]
    for a_data in assignments:
        assignment = Assignment(
            week_id=a_data["week"].id,
            title=a_data["title"],
            description=a_data["description"],
            type=a_data["type"],
            start_date=datetime.now(),
            due_date=a_data["due_date"],
            late_submission_penalty=10.0 if a_data["type"] == 'graded' else 0.0,
            is_published=True
        )
        db.session.add(assignment)
        db.session.flush()

        # Link the week’s questions to this assignment
        week_questions = Question.query.filter_by(
            week_id=a_data["week"].id,
            course_id=course.id
        ).all()
        for idx, q in enumerate(week_questions):
            aq = AssignmentQuestion(
                assignment_id=assignment.id,
                question_id=q.id,
                order=idx+1
            )
            db.session.add(aq)

    db.session.commit()
    log("Created ML assignments.")

    # Enroll students
    for student_key, student in users.items():
        if student.role == 'student':
            enrollment = CourseEnrollment(
                course_id=course.id,
                user_id=student.id,
                role='student',
                status='active'
            )
            db.session.add(enrollment)
            log(f"Enrolled {student.username} in {course_code}")

    db.session.commit()
    log("ML101 course setup completed.")

def create_data_science_course(admin, users):
    """
    Create a Data Science course with multiple weeks,
    advanced questions, and more robust content.
    """
    course_code = "DS201"
    course_name = "Data Science Essentials"
    desc = "Covers data preprocessing, exploratory data analysis, visualization, and basic modeling."

    course = Course.query.filter_by(code=course_code).first()
    if not course:
        course = Course(
            code=course_code,
            name=course_name,
            description=desc,
            created_by_id=admin.id,
            max_students=40,
            enrollment_type='open',
            start_date=datetime.now().date(),
            end_date=(datetime.now() + timedelta(days=120)).date(),
            is_active=True
        )
        db.session.add(course)
        db.session.commit()
        log(f"Created course: {course_code}")

    # Create 5 weeks
    weeks_titles = [
        "Week 1: Data Preprocessing",
        "Week 2: Exploratory Data Analysis",
        "Week 3: Visualization Techniques",
        "Week 4: Intro to Statistical Modeling",
        "Week 5: Project & Case Studies"
    ]
    weeks = []
    for i, title in enumerate(weeks_titles, 1):
        w = Week(
            course_id=course.id,
            number=i,
            title=title,
            description=f"Topics covered: {title}",
            is_published=True
        )
        db.session.add(w)
        db.session.flush()
        weeks.append(w)

    # Updated sample lectures for DS with new YouTube links
    ds_lecture_data = [
        {
            "week_idx": 0,
            "title": "Data Cleaning Basics",
            "description": "Identifying and handling missing values",
            "content_type": "youtube",
            "url": "https://www.youtube.com/watch?v=zo4EesmKquw",
            "transcript": "How to identify and correct missing data..."
        },
        {
            "week_idx": 1,
            "title": "EDA - Descriptive Stats",
            "description": "Descriptive statistics overview",
            "content_type": "pdf",
            "file_path": "DS_Week2_Lecture2.pdf",
            "transcript": "Understanding measures of central tendency, spread..."
        },
        {
            "week_idx": 2,
            "title": "Visualization Tools",
            "description": "Using matplotlib, seaborn for data visualization",
            "content_type": "youtube",
            "url": "https://www.youtube.com/watch?v=RLmOOw_5GmI",
            "transcript": "Plotting and charting fundamentals..."
        },
        {
            "week_idx": 3,
            "title": "Intro to Regression",
            "description": "Basic statistical modeling using linear regression",
            "content_type": "youtube",
            "url": "https://www.youtube.com/watch?v=kHwlB_j7Hkc",
            "transcript": "Regression approach for data analysis..."
        },
        {
            "week_idx": 4,
            "title": "Final Case Study",
            "description": "End-to-end data science project",
            "content_type": "pdf",
            "file_path": "DS_Week5_FinalProject.pdf",
            "transcript": "Bringing everything together with a real dataset..."
        }
    ]
    for idx, ld in enumerate(ds_lecture_data):
        w_idx = ld['week_idx']
        if w_idx >= len(weeks):
            continue
        lecture = Lecture(
            week_id=weeks[w_idx].id,
            lecture_number=idx+1,
            title=ld["title"],
            description=ld["description"],
            content_type=ld["content_type"],
            file_path=ld.get('file_path', ''),
            youtube_url=ld.get('url', ''),
            transcript=ld["transcript"],
            order=idx+1,
            is_published=True
        )
        db.session.add(lecture)
        db.session.flush()

        # Questions - advanced from week 3 onwards
        advanced = (w_idx >= 2)
        qs = create_sample_questions(admin.id, course.id, weeks[w_idx].id, lecture.id, advanced=advanced)
        for q in qs:
            db.session.add(q)

        # Create an assignment if it's the last lecture in that week
        # We'll assume each week has at most 1 lecture here for simplicity
        assignment_type = 'practice' if (w_idx % 2 == 0) else 'graded'
        due_date = datetime.now() + timedelta(days=7 + w_idx*7)
        assignment = Assignment(
            week_id=weeks[w_idx].id,
            title=f"{'Practice' if assignment_type == 'practice' else 'Graded'} DS Assignment - Week {w_idx+1}",
            description=f"Data Science tasks for Week {w_idx+1}.",
            type=assignment_type,
            start_date=datetime.now(),
            due_date=due_date,
            late_submission_penalty=10.0 if assignment_type == 'graded' else 0.0,
            is_published=True
        )
        db.session.add(assignment)
        db.session.flush()

        # Link week questions to assignment
        all_week_questions = Question.query.filter_by(
            week_id=weeks[w_idx].id,
            course_id=course.id
        ).all()
        for i, question in enumerate(all_week_questions, 1):
            db.session.add(
                AssignmentQuestion(
                    assignment_id=assignment.id,
                    question_id=question.id,
                    order=i
                )
            )

    db.session.commit()
    log("Created Data Science lectures and assignments.")

    # Enroll all students
    for sk, student in users.items():
        if student.role == 'student':
            enrollment = CourseEnrollment(
                course_id=course.id,
                user_id=student.id,
                role='student',
                status='active'
            )
            db.session.add(enrollment)
            log(f"Enrolled {student.username} in {course_code}")

    db.session.commit()
    log(f"{course_code} course setup completed.")

def create_algorithms_course(admin, users):
    """
    Another advanced course focusing on algorithms.
    """
    course_code = "CS103"
    course_name = "Introduction to Algorithms"
    desc = "An in-depth course on algorithmic paradigms, complexity, and analysis."

    course = Course.query.filter_by(code=course_code).first()
    if not course:
        course = Course(
            code=course_code,
            name=course_name,
            description=desc,
            created_by_id=admin.id,
            max_students=35,
            enrollment_type='open',
            start_date=datetime.now().date(),
            end_date=(datetime.now() + timedelta(days=100)).date(),
            is_active=True
        )
        db.session.add(course)
        db.session.commit()
        log(f"Created course: {course_code}")

    # Create 4 weeks
    week_titles = [
        "Week 1: Algorithmic Complexity & Big-O",
        "Week 2: Divide & Conquer",
        "Week 3: Greedy Algorithms",
        "Week 4: Dynamic Programming"
    ]
    weeks = []
    for i, title in enumerate(week_titles, 1):
        w = Week(
            course_id=course.id,
            number=i,
            title=title,
            description=f"Topics covered: {title}",
            is_published=True
        )
        db.session.add(w)
        db.session.flush()
        weeks.append(w)

    # For each week, add 2 lectures
    # Updated single YouTube link for intro to algorithms
    for i, week in enumerate(weeks):
        lectures_data = [
            {
                'title': f'Lecture {i+1}.1 - {week.title}',
                'description': 'Intro lecture',
                'content_type': 'youtube',
                'youtube_url': 'https://www.youtube.com/watch?v=CBYHwZcbD-s',
                'transcript': 'Discussing fundamental concepts...'
            },
            {
                'title': f'Lecture {i+1}.2 - {week.title}',
                'description': 'Detailed lecture',
                'content_type': 'pdf',
                'file_path': f'CS103_Week{i+1}_Lecture2.pdf',
                'transcript': f'Exploring deeper topics for {week.title}...'
            }
        ]
        for idx2, ld in enumerate(lectures_data, 1):
            lecture = Lecture(
                week_id=week.id,
                lecture_number=idx2,
                title=ld["title"],
                description=ld["description"],
                content_type=ld["content_type"],
                file_path=ld.get('file_path', ''),
                youtube_url=ld.get('youtube_url', ''),
                transcript=ld["transcript"],
                order=idx2,
                is_published=True
            )
            db.session.add(lecture)
            db.session.flush()

            # Advanced questions for every lecture
            qs = create_sample_questions(admin.id, course.id, week.id, lecture.id, advanced=True)
            for q in qs:
                db.session.add(q)

        # Create an assignment for each week (graded or practice)
        assignment_type = 'graded' if (i % 2 == 0) else 'practice'
        assignment = Assignment(
            week_id=week.id,
            title=f"{assignment_type.capitalize()} Assignment - {week.title}",
            description=f"Test your knowledge of {week.title}.",
            type=assignment_type,
            start_date=datetime.now(),
            due_date=datetime.now() + timedelta(days=10*(i+1)),
            late_submission_penalty=5.0 if assignment_type == 'graded' else 0.0,
            is_published=True
        )
        db.session.add(assignment)
        db.session.flush()

        # Link the week's questions
        w_questions = Question.query.filter_by(week_id=week.id, course_id=course.id).all()
        for idx3, q in enumerate(w_questions, 1):
            db.session.add(
                AssignmentQuestion(
                    assignment_id=assignment.id,
                    question_id=q.id,
                    order=idx3
                )
            )

    db.session.commit()
    log("Created lectures and assignments for Algorithms course.")

    # Enroll students
    for sk, student in users.items():
        if student.role == 'student':
            enrollment = CourseEnrollment(
                course_id=course.id,
                user_id=student.id,
                role='student',
                status='active'
            )
            db.session.add(enrollment)
            log(f"Enrolled {student.username} in {course_code}")

    db.session.commit()
    log(f"{course_code} course setup completed.")

def create_personal_resources(db):
    """
    Create more extensive personal learning resources for students.
    Each student in each course gets multiple notes, links, and summaries.
    """
    resource_templates = {
        'notes': [
            {
                'name': 'Lecture Notes',
                'description': 'Detailed notes with key concepts and examples',
                'content': '''
# Week {week} Lecture Notes

## Key Concepts
- Concept A: explanation
- Concept B: use cases

## Practice Problems
1. Problem statement
2. Proposed solution approach

## Additional Hints
- Remember to do X before Y
                '''
            },
            {
                'name': 'Study Guide',
                'description': 'Summary and practice questions for quick revision',
                'content': '''
# Study Guide - Week {week}

## Summary
- Main topics covered
- Important formulas or definitions

## Practice Questions
1. Question 1
2. Question 2

## References
- Link to official docs
                '''
            }
        ],
        'links': [
            {
                'name': 'External Resources',
                'description': 'Curated list of helpful external resources',
                'content': '''
# Helpful Links for {course}

- https://docs.python.org/3/tutorial/ - Python docs
- https://stackoverflow.com - Community Q&A
- https://realpython.com - Python tutorials
                '''
            },
            {
                'name': 'Video Tutorials',
                'description': 'List of video resources or playlists',
                'content': '''
# Video Tutorials for {course}

- https://youtube.com/playlist?list=XXXX - Official Course Channel
- https://coursera.org/specialization - Data Structures specialization
                '''
            }
        ],
        'summaries': [
            {
                'name': 'Weekly Summary',
                'description': 'Highlights of your weekly progress',
                'content': '''
# Week {week} Summary

## Completed
- Lectures watched
- Assignments submitted

## To-Do
- Pending exercises
- Revision tasks
                '''
            }
        ]
    }

    students = User.query.filter_by(role='student').all()
    courses = Course.query.all()
    
    for student in students:
        for course in courses:
            enrollment = CourseEnrollment.query.filter_by(
                user_id=student.id,
                course_id=course.id,
                status='active'
            ).first()
            if not enrollment:
                continue

            resource = PersonalResource(
                user_id=student.id,
                course_id=course.id,
                name=f"Personal Materials - {course.code}",
                description=f"My personal notes and materials for {course.name}",
                is_active=True,
                settings={'visibility': 'private'}
            )
            db.session.add(resource)
            db.session.flush()

            # Create resources for 4 weeks (expand as needed)
            for week_num in range(1, 5):
                for note_template in resource_templates['notes']:
                    note = ResourceFile(
                        resource_id=resource.id,
                        name=f"Week {week_num} - {note_template['name']}.txt",
                        type='note',
                        content=note_template['content'].format(
                            week=week_num, course=course.name
                        ),
                        file_type='text/plain',
                        file_size=len(note_template['content']) * 2
                    )
                    db.session.add(note)

                for link_template in resource_templates['links']:
                    link = ResourceFile(
                        resource_id=resource.id,
                        name=f"Week {week_num} - {link_template['name']}.txt",
                        type='link',
                        content=link_template['content'].format(course=course.name),
                        file_type='text/plain',
                        file_size=len(link_template['content']) * 2
                    )
                    db.session.add(link)

                for summary_template in resource_templates['summaries']:
                    summary = ResourceFile(
                        resource_id=resource.id,
                        name=f"Week {week_num} - {summary_template['name']}.txt",
                        type='note',
                        content=summary_template['content'].format(week=week_num),
                        file_type='text/plain',
                        file_size=len(summary_template['content']) * 2
                    )
                    db.session.add(summary)

    db.session.commit()
    log("Created personal resources for all enrolled students.")

def init_db():
    """
    Main function to initialize the database.
    """
    app = create_app()
    with app.app_context():
        if check_existing_data() and not RECREATE_DB:
            log("Database already contains data. Use RECREATE_DB=True to force recreation.")
            return

        log("Dropping all tables...")
        db.drop_all()
        
        log("Creating all tables...")
        db.create_all()
        
        log("Creating users...")
        users = create_users()
        
        log("Creating initial courses (CS101, CS102)...")
        courses = create_courses(users['teacher'])
        
        log("Creating course content for CS101, CS102...")
        for c in courses:
            create_course_content(c, users['teacher'].id)
        
        log("Enrolling students in initial courses...")
        create_enrollments(users, courses)
        
        log("Creating ML101 course...")
        create_ml_course(users['admin'], users)
        
        log("Creating Data Science course (DS201)...")
        create_data_science_course(users['admin'], users)
        
        log("Creating Algorithms course (CS103)...")
        create_algorithms_course(users['admin'], users)

        log("Creating personal resources for all students...")
        create_personal_resources(db)
        
        db.session.commit()
        log("Database initialization complete!")
        log("\nTest Credentials:")
        log("Admin     - username: admin    password: admin123")
        log("Teacher   - username: teacher  password: teacher123")
        log("Students  - username: student1 password: student123")
        log("           username: student2  password: student123")
        log("           ... up to student5")

def init_personal_resources():
    """
    Optional function to ONLY initialize personal resources.
    """
    app = create_app()
    with app.app_context():
        log("Creating personal resources only...")
        students = User.query.filter_by(role='student').all()
        courses = Course.query.all()
        
        for student in students:
            for course in courses:
                enrollment = CourseEnrollment.query.filter_by(
                    user_id=student.id,
                    course_id=course.id,
                    status='active'
                ).first()
                
                if not enrollment:
                    continue

                resource = PersonalResource(
                    user_id=student.id,
                    course_id=course.id,
                    name=f"Course Notes - {course.code}",
                    description=f"Personal notes for {course.name}",
                    is_active=True,
                    settings={'visibility': 'private'}
                )
                db.session.add(resource)
                db.session.flush()

                note = ResourceFile(
                    resource_id=resource.id,
                    name="Week 1 Notes.txt",
                    type="note",
                    content="Important points from Week 1...\n- Concepts\n- Problems\n- Solutions",
                    file_type="text/plain",
                    file_size=150
                )
                db.session.add(note)

                link = ResourceFile(
                    resource_id=resource.id,
                    name="Useful Links.txt",
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
