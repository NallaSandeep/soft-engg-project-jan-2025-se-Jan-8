"""
Database Initialization Script
----------------------------
This script initializes the StudyHub database with sample data for development and testing.
The script creates a rich set of interconnected data including:
- Users (admin, teachers, students)
- Courses with detailed content structure
- Weeks with multiple lectures and resources
- Assignments (both practice and graded) with questions
- Student submissions and progress tracking
- Personal learning resources

Key Features:
- Creates realistic academic environment
- Supports multiple course types and content formats
- Generates meaningful test data for all features
- Maintains referential integrity across models
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
    - 1 admin user for system management
    - 1 teacher for course creation and management
    - 5 students for testing different scenarios
    Each user has:
    - Unique username and email
    - Role-specific permissions
    - Verified email status
    - Active account status
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
    """
    Create sample questions for lectures and assignments.
    Generates:
    - Multiple Choice Questions (MCQ)
    - Multiple Select Questions (MSQ)
    - Numeric Questions
    Each question includes:
    - Title and content
    - Options (for MCQ/MSQ)
    - Correct answers
    - Points and explanation
    - Course/Week/Lecture association
    """
    questions_data = [
        # MCQ Questions
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
            'explanation': 'The primary purpose is to simplify complex processes, making them more manageable and understandable.'
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
            'explanation': 'Dynamic programming is most appropriate as it optimizes the solution by storing intermediate results.'
        },
        # MSQ Questions
        {
            'title': 'Best Practices',
            'content': 'Which of the following are considered best practices in this context? (Select all that apply)',
            'type': 'MSQ',
            'options': [
                'Writing comprehensive documentation',
                'Using meaningful variable names',
                'Avoiding code duplication',
                'Ignoring edge cases'
            ],
            'correct_answer': [0, 1, 2],
            'points': 3,
            'explanation': 'Good coding practices include documentation, meaningful names, and DRY principle.'
        },
        {
            'title': 'System Components',
            'content': 'Which components are essential for this system? (Select all that apply)',
            'type': 'MSQ',
            'options': [
                'Data validation module',
                'Error handling system',
                'User interface',
                'External API'
            ],
            'correct_answer': [0, 1, 2],
            'points': 2,
            'explanation': 'A robust system requires data validation, error handling, and a user interface.'
        },
        # Numeric Questions
        {
            'title': 'Performance Analysis',
            'content': 'If the system processes 100 requests per second, how many requests will it handle in 5 minutes?',
            'type': 'NUMERIC',
            'correct_answer': 30000,
            'points': 2,
            'explanation': 'Calculation: 100 requests/second * 60 seconds * 5 minutes = 30,000 requests'
        },
        {
            'title': 'Resource Utilization',
            'content': 'If each process uses 2.5 MB of memory, how much total memory (in MB) is needed for 10 processes?',
            'type': 'NUMERIC',
            'correct_answer': 25,
            'points': 1,
            'explanation': 'Calculation: 2.5 MB * 10 processes = 25 MB total memory'
        }
    ]

    questions = []
    for data in questions_data:
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
    Create sample courses with detailed structure.
    Each course includes:
    - Unique code and name
    - Description and enrollment settings
    - Start and end dates
    - Maximum student capacity
    - Active status
    Courses are designed to showcase different teaching scenarios.
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
    """
    Create comprehensive course content structure.
    For each course:
    - Multiple weeks of content
    - Lectures with various content types (YouTube, PDF)
    - Practice and graded assignments
    - Resource materials
    - Questions and assessments
    Content is organized to simulate a real course progression.
    """
    # Sample content data for each week (4 weeks, 2-3 lectures per week)
    weeks_content = [
        # Week 1: Introduction and Basics
        [
            {
                'type': 'youtube',
                'url': 'https://www.youtube.com/watch?v=zOjov-2OZ0E',
                'title': 'Course Introduction',
                'description': 'Overview of the course objectives and learning outcomes',
                'transcript': 'Welcome to this course! In this lecture, we will explore...'
            },
            {
                'type': 'pdf',
                'file_path': 'Week1_Lecture2.pdf',
                'title': 'Fundamental Concepts',
                'description': 'Core concepts and terminology',
                'transcript': 'This lecture covers the essential concepts you need to know...'
            },
            {
                'type': 'youtube',
                'url': 'https://www.youtube.com/watch?v=example3',
                'title': 'Practical Applications',
                'description': 'Real-world applications and examples',
                'transcript': 'Let\'s look at how these concepts apply in practice...'
            }
        ],
        # Week 2: Advanced Topics
        [
            {
                'type': 'youtube',
                'url': 'https://www.youtube.com/watch?v=rfscVS0vtbw',
                'title': 'Advanced Techniques',
                'description': 'Deep dive into advanced methodologies',
                'transcript': 'In this advanced lecture, we will explore complex topics...'
            },
            {
                'type': 'pdf',
                'file_path': 'Week2_Lecture2.pdf',
                'title': 'Case Studies',
                'description': 'Analysis of real-world examples',
                'transcript': 'These case studies demonstrate the practical application...'
            }
        ],
        # Week 3: Practical Implementation
        [
            {
                'type': 'youtube',
                'url': 'https://www.youtube.com/watch?v=example5',
                'title': 'Implementation Strategies',
                'description': 'Hands-on implementation guide',
                'transcript': 'Today we will implement what we\'ve learned...'
            },
            {
                'type': 'pdf',
                'file_path': 'Week3_Lecture2.pdf',
                'title': 'Best Practices',
                'description': 'Industry standards and best practices',
                'transcript': 'Following these best practices will ensure...'
            },
            {
                'type': 'youtube',
                'url': 'https://www.youtube.com/watch?v=example6',
                'title': 'Common Pitfalls',
                'description': 'Common mistakes and how to avoid them',
                'transcript': 'Let\'s discuss common mistakes and their solutions...'
            }
        ],
        # Week 4: Advanced Applications
        [
            {
                'type': 'youtube',
                'url': 'https://www.youtube.com/watch?v=example7',
                'title': 'Advanced Applications',
                'description': 'Complex real-world applications',
                'transcript': 'In this final week, we\'ll tackle advanced applications...'
            },
            {
                'type': 'pdf',
                'file_path': 'Week4_Lecture2.pdf',
                'title': 'Future Trends',
                'description': 'Emerging trends and future directions',
                'transcript': 'The field is rapidly evolving, and these trends...'
            }
        ]
    ]
    
    weeks = []
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
        weeks.append(week)
        
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
            
            # Create sample questions for each lecture
            questions = create_sample_questions(teacher_id, course.id, week.id, lecture.id)
            for question in questions:
                db.session.add(question)

            # Create assignments (alternating between practice and graded)
            if lecture_num == len(lectures_data):  # Create assignment at end of week
                due_date = datetime.now() + timedelta(days=7 * week_num)
                assignment_type = 'practice' if week_num % 2 == 0 else 'graded'
                
                assignment = Assignment(
                    week_id=week.id,
                    title=f"{'Practice' if assignment_type == 'practice' else 'Graded'} Assignment - Week {week_num}",
                    description=f"Complete this {'practice' if assignment_type == 'practice' else 'graded'} assignment to test your understanding of Week {week_num} concepts.",
                    type=assignment_type,
                    start_date=datetime.now(),
                    due_date=due_date,
                    late_submission_penalty=10.0 if assignment_type == 'graded' else 0.0,
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

            # Create resources for each lecture
            resource = Resource(
                course_id=course.id,
                week_id=week.id,
                title=f"{lecture_data['title']} - Materials",
                description=f"Supplementary materials for {lecture_data['title']}",
                type='file',
                content=None,
                file_path=f"/static/resources/week{week_num}/lecture{lecture_num}/materials.pdf",
                file_type='application/pdf',
                file_size=1024 * 1024,  # 1MB dummy size
                created_by_id=teacher_id,
                is_active=True,
                is_public=True
            )
            db.session.add(resource)
    
    db.session.commit()
    return weeks

def create_sample_submissions(student_id, assignment_id):
    """
    Create realistic assignment submissions.
    Features:
    - Different submission patterns for practice/graded assignments
    - Multiple attempts for practice assignments
    - Score improvements over attempts
    - Submission timing relative to due dates
    - Detailed feedback and grading
    """
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
    """
    Create a single detailed assignment submission.
    Includes:
    - Question-wise answers and explanations
    - Individual question scores
    - Overall submission score
    - Submission timing and status
    - Attempt tracking for multiple submissions
    """
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
    Create course enrollments and student progress.
    Handles:
    - Student enrollment in courses
    - Assignment submission history
    - Course progress tracking
    - Active enrollment status
    Creates realistic enrollment patterns across courses.
    """
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
    """
    Create a specialized Machine Learning course.
    Features:
    - Structured learning path
    - Mix of theoretical and practical content
    - Progressive difficulty levels
    - Various assessment types
    - Rich resource materials
    Demonstrates advanced course structuring capabilities.
    """
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
            "transcript": "Machine learning is the field of study that gives computers the ability to learn without being explicitly programmed.",
            "content_type": "youtube",
            "lecture_number": 1
        },
        {
            "week": weeks[0],
            "title": "Types of Machine Learning",
            "youtube_url": "https://www.youtube.com/watch?v=wnZbxye9xP4",
            "transcript": "In this video, we explore Supervised, Unsupervised, and Reinforcement Learning.",
            "content_type": "youtube",
            "lecture_number": 2
        },
        {
            "week": weeks[1],
            "title": "Supervised Learning: Linear Regression",
            "youtube_url": "https://www.youtube.com/watch?v=ZkjP5RJLQF4",
            "transcript": "Linear Regression is one of the simplest models for Supervised Learning.",
            "content_type": "youtube",
            "lecture_number": 1
        },
        {
            "week": weeks[2],
            "title": "Clustering in Machine Learning",
            "youtube_url": "https://www.youtube.com/watch?v=2uqWgtrL2M0",
            "transcript": "Clustering helps in finding patterns in data, often used in customer segmentation.",
            "content_type": "youtube",
            "lecture_number": 1
        }
    ]

    for lecture_info in lecture_data:
        lecture = Lecture(
            week_id=lecture_info["week"].id,
            lecture_number=lecture_info["lecture_number"],  # Use the specified lecture number
            title=lecture_info["title"],
            description=f"Lecture: {lecture_info['title']}",
            content_type=lecture_info["content_type"],
            youtube_url=lecture_info["youtube_url"],
            transcript=lecture_info["transcript"],
            order=lecture_info["lecture_number"],  # Use lecture_number as initial order
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
    """
    Create personalized learning resources for students.
    Includes:
    - Course-specific notes
    - Study materials
    - External resource links
    - Personal progress tracking
    Supports individual learning paths.
    """
    # Sample resource types and templates
    resource_templates = {
        'notes': [
            {
                'name': 'Lecture Notes',
                'description': 'Detailed notes from lectures with key concepts and examples',
                'content': '''
# Week {week} Lecture Notes

## Key Concepts
- Important concept 1: Definition and explanation
- Important concept 2: Examples and use cases
- Important concept 3: Implementation details

## Practice Problems
1. Problem description and approach
2. Solution strategy
3. Common pitfalls to avoid

## Study Tips
- Review these concepts before next lecture
- Practice exercises recommended
- Additional resources to explore
                '''
            },
            {
                'name': 'Study Guide',
                'description': 'Comprehensive study guide with summaries and practice questions',
                'content': '''
# Study Guide - Week {week}

## Summary
- Main topics covered
- Key takeaways
- Important formulas/concepts

## Practice Questions
1. Question 1 with solution
2. Question 2 with solution
3. Self-assessment exercises

## Additional Resources
- Recommended readings
- Online tutorials
- Reference materials
                '''
            }
        ],
        'links': [
            {
                'name': 'External Resources',
                'description': 'Curated list of helpful external resources and references',
                'content': '''
# Useful Resources for {course}

## Online Tutorials
- https://example.com/tutorial1 - Basic concepts
- https://example.com/tutorial2 - Advanced topics
- https://example.com/tutorial3 - Practice exercises

## Reference Documentation
- https://example.com/docs1 - Official documentation
- https://example.com/docs2 - Community guides
- https://example.com/docs3 - Best practices

## Video Lectures
- https://example.com/video1 - Introduction
- https://example.com/video2 - Deep dive
- https://example.com/video3 - Case studies
                '''
            }
        ],
        'summaries': [
            {
                'name': 'Weekly Summary',
                'description': 'Condensed summary of weekly learning objectives and achievements',
                'content': '''
# Week {week} Summary

## Learning Objectives
- Objective 1: Status and notes
- Objective 2: Status and notes
- Objective 3: Status and notes

## Key Achievements
- Completed assignments
- Practice exercises
- Additional learning

## Next Steps
- Topics to review
- Upcoming assignments
- Preparation for next week
                '''
            }
        ]
    }

    # Get all students and courses
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
            
            # Create a personal resource collection for this course
            resource = PersonalResource(
                user_id=student.id,
                course_id=course.id,
                name=f"Course Materials - {course.code}",
                description=f"Personal study materials and notes for {course.name}",
                is_active=True,
                settings={'visibility': 'private'}
            )
            db.session.add(resource)
            db.session.flush()

            # Add various types of resource files
            for week_num in range(1, 5):  # 4 weeks of content
                # Add lecture notes
                for note_template in resource_templates['notes']:
                    note = ResourceFile(
                        resource_id=resource.id,
                        name=f"Week {week_num} - {note_template['name']}.txt",
                        type='note',
                        content=note_template['content'].format(week=week_num, course=course.name),
                        file_type='text/plain',
                        file_size=len(note_template['content']) * 2  # Approximate size
                    )
                    db.session.add(note)

                # Add external resources/links
                for link_template in resource_templates['links']:
                    link = ResourceFile(
                        resource_id=resource.id,
                        name=f"Week {week_num} - {link_template['name']}.txt",
                        type='link',
                        content=link_template['content'].format(course=course.name),
                        file_type='text/plain',
                        file_size=len(link_template['content'])
                    )
                    db.session.add(link)

                # Add weekly summaries
                for summary_template in resource_templates['summaries']:
                    summary = ResourceFile(
                        resource_id=resource.id,
                        name=f"Week {week_num} - {summary_template['name']}.txt",
                        type='note',
                        content=summary_template['content'].format(week=week_num),
                        file_type='text/plain',
                        file_size=len(summary_template['content'])
                    )
                    db.session.add(summary)

    db.session.commit()
    log("Created personal resources for all enrolled students")

def init_db():
    """
    Main function to initialize the database.
    Process:
    1. Checks for existing data
    2. Creates fresh database schema
    3. Generates all sample data
    4. Establishes relationships
    5. Ensures data consistency
    Creates a complete testing environment.
    """
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
        create_personal_resources(db)
        
        db.session.commit()
        log("Database initialization complete!")
        log("\nTest Credentials:")
        log("Admin     - username: admin    password: admin123")
        log("Teacher   - username: teacher  password: teacher123")
        log("Students  - username: student1 password: student123")
        log("           username: student2 password: student123")
        log("           ... up to student5")

def init_personal_resources():
    """
    Initialize only personal learning resources.
    Used for:
    - Adding study materials
    - Creating resource collections
    - Setting up learning paths
    Can be run independently of main initialization.
    """
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
