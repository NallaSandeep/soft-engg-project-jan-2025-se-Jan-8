"""
import_courses_to_studyhub.py

This script imports course data from JSON files into StudyHub database.
It ensures consistency between StudyHub and StudyIndexer by maintaining
the same course codes, week structures, and content IDs.

Usage:
    python import_courses.py file.json        # Process a single file
    python import_courses.py path/to/json_dir # Process all JSON in a directory
"""

import os
import sys
import json
import uuid
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

# Add the parent directory to the path so we can import app
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

try:
    # Import Flask app and database
    from app import db, create_app
    from app.models import (
    User, Course, Week, Lecture, Assignment, AssignmentQuestion, 
        CourseEnrollment, PersonalResource, Question
    )
    
    # Create the Flask app with the default config
    app = create_app()
    print("[INFO] Successfully imported StudyHub models and database")
except ImportError as e:
    print(f"[ERROR] Failed to import StudyHub models: {str(e)}")
    print("[INFO] Make sure you're running this script from the StudyHub backend directory")
    sys.exit(1)

# Constants - match with init_db.py
ADMIN_EMAIL = "admin@studyhub.com"  # Admin from init_db.py

def log(message, level="INFO"):
    """Log messages with timestamp and level"""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{level}] {message}")

def check_existing_data(db_session):
    """Check if courses already exist to avoid duplication"""
    try:
        log("Checking for existing courses in the database...")
        existing_courses = db_session.query(Course).all()
        if existing_courses:
            log(f"Found {len(existing_courses)} existing courses")
            for course in existing_courses:
                log(f"  - {course.code}: {course.name}", "DEBUG")
            return {course.code: course for course in existing_courses}
        else:
            log("No existing courses found in the database")
            return {}
    except Exception as e:
        log(f"Error checking existing data: {str(e)}", "ERROR")
        return {}

def get_admin_user(db_session):
    """Get admin user for course creation"""
    log(f"Looking for admin user with email {ADMIN_EMAIL}...")
    admin = db_session.query(User).filter(User.email == ADMIN_EMAIL).first()
    if not admin:
        log(f"Admin user ({ADMIN_EMAIL}) not found. Trying to find any teacher...", "WARNING")
        admin = db_session.query(User).filter(User.role == 'teacher').first()
        if not admin:
            log("No admin or teacher users found in database.", "ERROR")
            log("Please create a teacher user first by running init_db.py", "ERROR")
            raise Exception("No admin or teacher users found in database.")
        log(f"Using teacher: {admin.email} (ID: {admin.id})")
    else:
        log(f"Found admin user: {admin.email} (ID: {admin.id})")
    return admin

def parse_json_file(file_path):
    """Parse JSON file and return course data"""
    log(f"Parsing JSON file: {file_path}")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Basic validation
        if "course" not in data:
            log(f"JSON file missing 'course' element", "ERROR")
            return None
            
        log(f"Successfully parsed JSON with {len(data.keys())} top-level keys")
        if "course" in data:
            course_info = data["course"]
            log(f"Course info found: {course_info.get('title', 'Unknown')} ({course_info.get('code', 'Unknown')})")
        if "weeks" in data:
            log(f"Found {len(data['weeks'])} weeks")
        if "lectures" in data:
            log(f"Found {len(data['lectures'])} lectures")
        if "assignments" in data:
            log(f"Found {len(data['assignments'])} assignments")
            
        return data
    except json.JSONDecodeError as e:
        log(f"JSON parsing error in {file_path}: {str(e)}", "ERROR")
        log(f"Error at line {e.lineno}, column {e.colno}: {e.msg}", "ERROR")
        return None
    except Exception as e:
        log(f"Error parsing {file_path}: {str(e)}", "ERROR")
        return None

def create_course_from_json(db, data, admin_id):
    """Create a course from JSON data"""
    try:
        # Extract course info
        course_info = data.get("course", {})
        if not course_info:
            log("Course information not found in JSON.", "ERROR")
            return None

        # Extract basic course data
        code = course_info.get("code")
        name = course_info.get("title")  # StudyHub uses 'name' instead of 'title'
        description = course_info.get("description", "")
        # StudyHub Course model doesn't have department or credits fields

        if not code or not name:
            log(f"Course code or name missing. Code: {code}, Name: {name}", "ERROR")
            return None

        log(f"Creating course: {code} - {name}")
        log(f"  Description: {description[:50]}..." if len(description) > 50 else f"  Description: {description}")

        # Create course with fields that match the StudyHub Course model
        course = Course(
            code=code,
            name=name,
            description=description,
            created_by_id=admin_id,
            start_date=datetime.now().date(),
            end_date=(datetime.now() + timedelta(days=90)).date(),
            is_active=True,
            max_students=50,
            enrollment_type='open'
        )
        db.add(course)
        db.flush()  # Get the course ID without committing

        log(f"Created course with ID: {course.id}")
        return course
    except IntegrityError:
        db.rollback()
        log(f"Course {code} already exists. Trying to retrieve existing course.", "WARNING")
        return db.query(Course).filter(Course.code == code).first()
    except Exception as e:
        db.rollback()
        log(f"Error creating course: {str(e)}", "ERROR")
        return None

def create_weeks_from_json(db, course, data):
    """Create weeks for a course from JSON data"""
    weeks_data = data.get("weeks", [])
    if not weeks_data:
        log(f"No weeks found for course {course.code}", "WARNING")
        return

    log(f"Creating {len(weeks_data)} weeks for course {course.code}")
    for week_data in weeks_data:
        try:
            # Extract week data
            week_number = week_data.get("week_number")
            if week_number is None:
                week_number = week_data.get("week_id")
            if week_number is None:
                week_number = week_data.get("order")
                
            if week_number is None:
                log(f"Week number missing from week data: {week_data}", "ERROR")
                continue
                
            title = week_data.get("title", f"Week {week_number}")
            description = week_data.get("description", "")

            log(f"  Creating week {week_number}: {title}")
            
            # Create week with fields that match the StudyHub Week model
            week = Week(
                course_id=course.id,
                number=week_number,  # StudyHub uses 'number' instead of 'week_number'
                title=title,
                description=description,
                is_published=True
            )
            db.add(week)
            db.flush()  # Get the week ID
            
            log(f"  Created week with ID: {week.id}")

            # Create lectures for this week
            create_lectures_from_json(db, course, week, week_data, data)

        except Exception as e:
            db.rollback()
            log(f"Error creating week {week_number} for course {course.code}: {str(e)}", "ERROR")

def create_lectures_from_json(db, course, week, week_data, parent_data):
    """Create lectures for a week from JSON data"""
    lectures_data = week_data.get("lectures", [])
    
    # Also check if lectures are in the parent data
    if not lectures_data and "lectures" in parent_data:
        # Filter lectures for this week
        all_lectures = parent_data.get("lectures", [])
        lectures_data = [l for l in all_lectures if l.get("week_id") == week.number or l.get("week") == week.number]
        log(f"  Found {len(lectures_data)} lectures in parent data for week {week.number}")

    if not lectures_data:
        log(f"  No lectures found for week {week.number} in course {course.code}", "WARNING")
        return

    log(f"  Creating {len(lectures_data)} lectures for week {week.number}")
    for idx, lecture_data in enumerate(lectures_data):
        try:
            # Extract lecture data
            title = lecture_data.get("title", f"Lecture {idx+1}")
            description = lecture_data.get("description", f"Description for {title}")
            
            # Determine content type and related fields
            content_type = 'youtube'  # Default to youtube
            
            # Handle different URL field names
            youtube_url = lecture_data.get("youtube_url", "")
            if not youtube_url and lecture_data.get("video_url"):
                youtube_url = lecture_data.get("video_url", "")
            
            # Handle file paths
            file_path = lecture_data.get("file_path", "")
            if not file_path and lecture_data.get("resource_url"):
                file_path = lecture_data.get("resource_url", "")
                
            if lecture_data.get("resource_type") == "pdf" or (not youtube_url and file_path):
                content_type = 'pdf'
                youtube_url = ""
            
            # Get transcript - handle different field names for transcript content
            transcript = ""
            if lecture_data.get("content_transcript"):
                transcript = lecture_data.get("content_transcript", "")
            elif lecture_data.get("content"):
                transcript = lecture_data.get("content", "")
            elif lecture_data.get("transcript"):
                transcript = lecture_data.get("transcript", "")
            elif lecture_data.get("content_extract"):
                transcript = lecture_data.get("content_extract", "")
                
            lecture_number = lecture_data.get("lecture_number", idx + 1)
            if not lecture_number and lecture_data.get("lecture_id"):
                lecture_number = lecture_data.get("lecture_id")
                
            order = lecture_data.get("order", idx + 1)
            
            log(f"    Creating lecture {lecture_number}: {title} (Type: {content_type})")
            
            # Create lecture with fields that match the StudyHub Lecture model
            lecture = Lecture(
                week_id=week.id,
                lecture_number=lecture_number,
                title=title,
                description=description,
                content_type=content_type,
                youtube_url=youtube_url,
                file_path=file_path,
                transcript=transcript,
                order=order,
                is_published=True
            )
            db.add(lecture)
            db.flush()  # Get the lecture ID

            log(f"    Created lecture with ID: {lecture.id} with {len(transcript) > 0 and 'transcript' or 'no transcript'}")

        except Exception as e:
            log(f"Error creating lecture for week {week.number} in course {course.code}: {str(e)}", "ERROR")

def create_question_bank(db, course, data):
    """Create questions for the course and store them in the question bank
    
    This function creates questions from:
    1. Questions directly in the JSON
    2. Concepts extracted from lecture content
    
    Returns a dictionary mapping week_id to a list of questions for that week
    """
    log(f"Creating question bank for course {course.code}...")
    
    # Dictionary to store questions by week
    question_bank = {}
    
    # Process standalone questions if they exist
    standalone_questions = data.get("questions", [])
    if standalone_questions:
        log(f"  Found {len(standalone_questions)} standalone questions")
        # For now, assign these to week 1 if we can't determine their week
        default_week = db.query(Week).filter_by(course_id=course.id, number=1).first()
        
        if default_week:
            for idx, q_data in enumerate(standalone_questions):
                try:
                    # Create question similar to before
                    title = q_data.get("title", f"Question {idx+1}")
                    content = q_data.get("text", f"Question content {idx+1}")
                    if not content and q_data.get("content"):
                        content = q_data.get("content")
                        
                    q_type = q_data.get("type", "MCQ")
                    options = q_data.get("options", [])
                    correct_answer = q_data.get("correct_answer", 0)
                    points = q_data.get("points", 1)
                    explanation = q_data.get("explanation", f"Explanation for question {idx+1}")
                    
                    question = Question(
                        created_by_id=course.created_by_id,
                        title=title,
                        content=content,
                        type=q_type,
                        question_options=options,
                        correct_answer=correct_answer,
                        points=points,
                        explanation=explanation,
                        course_id=course.id,
                        week_id=default_week.id,
                        status='active'
                    )
                    db.add(question)
                    db.flush()
                    
                    # Add to question bank
                    if default_week.id not in question_bank:
                        question_bank[default_week.id] = []
                    question_bank[default_week.id].append(question)
                    
                    log(f"    Created standalone question: {title}")
                except Exception as e:
                    log(f"    Error creating standalone question: {str(e)}", "ERROR")
    
    # Process questions from lectures
    weeks_data = data.get("weeks", [])
    for week_data in weeks_data:
        week_id = week_data.get("week_id")
        if not week_id:
            continue
            
        # Find the week in the database
        week = db.query(Week).filter_by(course_id=course.id, number=week_id).first()
        if not week:
            continue
            
        # Initialize the question list for this week
        if week.id not in question_bank:
            question_bank[week.id] = []
            
        # Get lectures for this week
        lectures_data = week_data.get("lectures", [])
        
        # Also check lectures in parent data
        if not lectures_data and "lectures" in data:
            lectures_data = [l for l in data.get("lectures", []) 
                            if l.get("week_id") == week_id or l.get("week") == week_id]
        
        # Process each lecture to extract questions
        for lecture_idx, lecture_data in enumerate(lectures_data):
            try:
                # Find the lecture in the database
                lecture_number = lecture_data.get("lecture_number") or lecture_data.get("lecture_id") or (lecture_idx + 1)
                lecture = db.query(Lecture).filter_by(
                    week_id=week.id, 
                    lecture_number=lecture_number
                ).first()
                
                if not lecture:
                    continue
                
                # Try to create questions from the lecture content
                if lecture.transcript:
                    # Create a basic understanding question
                    base_question = Question(
                        created_by_id=course.created_by_id,
                        title=f"Core concepts in {lecture.title}",
                        content=f"What are the key points discussed in the lecture on {lecture.title}?",
                        type="text",
                        question_options=[],
                        correct_answer="",
                        points=5,
                        explanation=f"This question tests understanding of the main concepts in {lecture.title}",
                        course_id=course.id,
                        week_id=week.id,
                        status='active'
                    )
                    db.add(base_question)
                    db.flush()
                    question_bank[week.id].append(base_question)
                    
                    # If lecture has LLM_Summary, extract concepts for more specific questions
                    if lecture_data.get("LLM_Summary") and lecture_data["LLM_Summary"].get("concepts_covered"):
                        concepts = lecture_data["LLM_Summary"].get("concepts_covered", [])
                        
                        # Create a multiple choice question about these concepts
                        if len(concepts) >= 4:  # Need at least 4 for options
                            import random
                            
                            # Select a random concept as the subject
                            target_concept = random.choice(concepts)
                            options = random.sample(concepts, min(4, len(concepts)))
                            if target_concept not in options:
                                options[0] = target_concept
                                random.shuffle(options)
                                
                            correct_idx = options.index(target_concept)
                            
                            concept_q = Question(
                                created_by_id=course.created_by_id,
                                title=f"Concept identification in {lecture.title}",
                                content=f"Which of the following best describes {target_concept}?",
                                type="MCQ",
                                question_options=options,
                                correct_answer=correct_idx,
                                points=3,
                                explanation=f"This concept was covered in the lecture on {lecture.title}",
                                course_id=course.id,
                                week_id=week.id,
                                status='active'
                            )
                            db.add(concept_q)
                            db.flush()
                            question_bank[week.id].append(concept_q)
                    
                    log(f"    Created {len(question_bank[week.id])} questions from lecture: {lecture.title}")
            except Exception as e:
                log(f"    Error processing lecture for questions: {str(e)}", "ERROR")
    
    # Summary
    total_questions = sum(len(questions) for questions in question_bank.values())
    log(f"Created question bank with {total_questions} questions across {len(question_bank)} weeks")
    
    return question_bank

def create_assignments_with_questions(db, course, data, question_bank):
    """Create assignments and associate questions from the question bank
    
    Args:
        db: Database session
        course: Course object
        data: Course data from JSON
        question_bank: Dictionary mapping week_id to list of questions for that week
    """
    log(f"Creating assignments for course {course.code}...")
    
    # Process assignments from the data
    assignments_data = data.get("assignments", [])
    
    if not assignments_data:
        log(f"No explicit assignments found, creating default assignments for each week...", "WARNING")
        
        # Create default assignments for each week if none specified
        weeks = db.query(Week).filter_by(course_id=course.id).order_by(Week.number).all()
        
        for i, week in enumerate(weeks):
            # Skip weeks with no questions
            if week.id not in question_bank or not question_bank[week.id]:
                continue
                
            # Create both a practice and graded assignment for each week
            assignment_types = ["practice", "graded"]
            for idx, a_type in enumerate(assignment_types):
                try:
                    # Create assignment
                    title = f"{a_type.capitalize()} Assignment - Week {week.number}"
                    description = f"Complete this {a_type} assignment to assess your understanding of Week {week.number}"
                    
                    assignment = Assignment(
                        week_id=week.id,
                        title=title,
                        description=description,
                        type=a_type,
                        start_date=datetime.now(),
                        due_date=datetime.now() + timedelta(days=7 + (i * 7)),
                        late_submission_penalty=5.0 if a_type == "graded" else 0.0,
                        is_published=True
                    )
                    db.add(assignment)
                    db.flush()
                    
                    # Determine how many questions to include
                    questions = question_bank[week.id]
                    num_questions = min(5, len(questions))  # Max 5 questions per assignment
                    
                    # Link questions to assignment
                    for q_idx, question in enumerate(questions[:num_questions]):
                        aq = AssignmentQuestion(
                            assignment_id=assignment.id,
                            question_id=question.id,
                            order=q_idx + 1
                        )
                        db.add(aq)
                    
                    log(f"  Created default {a_type} assignment for Week {week.number} with {num_questions} questions")
                except Exception as e:
                    log(f"  Error creating default assignment for Week {week.number}: {str(e)}", "ERROR")
    else:
        # Process assignments from the data
        log(f"Processing {len(assignments_data)} assignments from data...")
        
        for a_idx, a_data in enumerate(assignments_data):
        try:
            # Extract assignment data
                title = a_data.get("title", f"Assignment {a_idx+1}")
                description = a_data.get("description", "")
                a_type = a_data.get("type", "practice")
                
                # Get week
                week_id_val = a_data.get("week_id") or a_data.get("week")
                if not week_id_val:
                    log(f"  No week specified for assignment {title}, skipping", "WARNING")
                    continue
                
                week = db.query(Week).filter_by(course_id=course.id, number=week_id_val).first()
            if not week:
                    log(f"  Week {week_id_val} not found for assignment {title}, skipping", "WARNING")
                continue

            # Create assignment
                due_days = 14 if a_type == "graded" else 7
            assignment = Assignment(
                week_id=week.id,
                title=title,
                description=description,
                    type=a_type,
                    start_date=datetime.now(),
                    due_date=datetime.now() + timedelta(days=due_days),
                    late_submission_penalty=10.0 if a_type == "graded" else 0.0,
                    is_published=True
            )
            db.add(assignment)
                db.flush()
                
                # Get questions for this assignment
                assignment_questions = a_data.get("questions", [])
                
                if assignment_questions:
                    # Use explicitly defined questions for this assignment
                    for q_idx, q_data in enumerate(assignment_questions):
                        try:
                            # Create a new question
                            title = q_data.get("title", f"Question {q_idx+1}")
                            content = q_data.get("text", "") or q_data.get("content", "")
                            q_type = q_data.get("type", "MCQ")
                            options = q_data.get("options", [])
                            correct_answer = q_data.get("correct_answer", 0)
                            
                            question = Question(
                                created_by_id=course.created_by_id,
                                title=title,
                                content=content,
                                type=q_type,
                                question_options=options,
                                correct_answer=correct_answer,
                                points=q_data.get("points", 1),
                                explanation=q_data.get("explanation", ""),
                                course_id=course.id,
                                week_id=week.id,
                                status='active'
            )
            db.add(question)
                            db.flush()
                            
                            # Link to assignment
                            aq = AssignmentQuestion(
                                assignment_id=assignment.id,
                                question_id=question.id,
                                order=q_idx + 1
                            )
                            db.add(aq)
                            
                            log(f"    Added question '{title}' to assignment")
        except Exception as e:
                            log(f"    Error creating question for assignment: {str(e)}", "ERROR")
                else:
                    # Use questions from the question bank
                    if week.id in question_bank and question_bank[week.id]:
                        # Determine number of questions (5 for practice, 10 for graded)
                        num_questions = 10 if a_type == "graded" else 5
                        questions = question_bank[week.id][:num_questions]
                        
                        for q_idx, question in enumerate(questions):
                            aq = AssignmentQuestion(
                                assignment_id=assignment.id,
                                question_id=question.id,
                                order=q_idx + 1
                            )
                            db.add(aq)
                        
                        log(f"    Added {len(questions)} questions from question bank to assignment")
                    else:
                        log(f"    No questions available for this assignment", "WARNING")
                
                log(f"  Created assignment: {title} ({a_type})")
            except Exception as e:
                log(f"  Error creating assignment: {str(e)}", "ERROR")
    
    db.flush()
    log(f"Assignments creation completed")

def process_single_file(db_session, json_file, admin):
    """Process a single JSON file"""
    log(f"=== Processing file: {json_file} ===")
    
    try:
        # Parse file
            data = parse_json_file(json_file)
            if not data:
            log(f"Failed to parse {json_file}. Skipping.", "ERROR")
            return False

            # Extract course info
            course_info = data.get("course", {})
            if not course_info:
            log(f"No course information found in {json_file}", "ERROR")
            return False

        # Extract course code
            code = course_info.get("code")
        if not code:
            log(f"No course code found in {json_file}", "ERROR")
            return False
            
        # Check if course exists
        existing_courses = check_existing_data(db_session)
            if code in existing_courses:
            log(f"Course {code} already exists. Using existing course.", "WARNING")
            course = existing_courses[code]
        else:    
            # Create course
            course = create_course_from_json(db_session, data, admin.id)
            if not course:
                log(f"Failed to create course from {json_file}", "ERROR")
                return False

            # Create weeks, lectures
            create_weeks_from_json(db_session, course, data)
            
            # Create question bank and assignments in sequence
            question_bank = create_question_bank(db_session, course, data)
            create_assignments_with_questions(db_session, course, data, question_bank)
        
        # Enroll student with ID 3 (student1) in the course
        enroll_student(db_session, course, student_id=3)

        # Commit the transaction
        db_session.commit()
        log(f"Successfully imported and processed course {code} from {json_file}", "SUCCESS")
        return True
    except Exception as e:
        db_session.rollback()
        log(f"Error processing course from {json_file}: {str(e)}", "ERROR")
        return False

def enroll_student(db_session, course, student_id=3):
    """Enroll a student in the course
    
    Args:
        db_session: Database session
        course: Course object
        student_id: Student ID (default is 3, which is student1 in init_db.py)
    """
    try:
        # Check if student exists
        student = db_session.query(User).filter(User.id == student_id).first()
        if not student:
            log(f"Student with ID {student_id} not found.", "ERROR")
            return False
            
        # Check if enrollment already exists
        existing_enrollment = db_session.query(CourseEnrollment).filter(
            CourseEnrollment.course_id == course.id,
            CourseEnrollment.user_id == student_id
        ).first()
        
        if existing_enrollment:
            log(f"Student {student.username} (ID: {student_id}) is already enrolled in course {course.code}.", "WARNING")
            return True
            
        # Create enrollment
        enrollment = CourseEnrollment(
            course_id=course.id,
            user_id=student_id,
            role='student',
            status='active',
            enrolled_at=datetime.now()
        )
        db_session.add(enrollment)
        db_session.flush()
        
        log(f"Enrolled student {student.username} (ID: {student_id}) in course {course.code}.", "SUCCESS")
        return True
    except Exception as e:
        db_session.rollback()
        log(f"Error enrolling student {student_id} in course {course.code}: {str(e)}", "ERROR")
        return False

def main():
    """Main function to import courses from JSON files"""
    # Get file or directory from command line argument
    if len(sys.argv) < 2:
        log("Usage: python import_courses.py <file.json or directory>", "ERROR")
        return
        
    path = sys.argv[1]
    log(f"Starting course import process...")
    log(f"Target path: {path}")
    
    # Check if path exists
    if not os.path.exists(path):
        log(f"Path does not exist: {path}", "ERROR")
        return
        
    # Create database session using Flask-SQLAlchemy's session
    try:
        log("Connecting to database...")
        with app.app_context():
            # Use the db session from Flask-SQLAlchemy
            db_session = db.session
            log("Connected to database")
            
            try:
                # Get admin user
                admin = get_admin_user(db_session)
                
                # Process path
                if os.path.isfile(path) and path.endswith('.json'):
                    # Process single file
                    process_single_file(db_session, path, admin)
                elif os.path.isdir(path):
                    # Process directory
                    log(f"Processing directory: {path}")
                    json_files = [os.path.join(path, f) for f in os.listdir(path) 
                                 if f.endswith('.json') and os.path.isfile(os.path.join(path, f))]
                    
                    if not json_files:
                        log(f"No JSON files found in {path}", "ERROR")
                        return
                        
                    log(f"Found {len(json_files)} JSON files: {[os.path.basename(f) for f in json_files]}")
                    
                    # Process each file separately
                    for json_file in json_files:
                        process_single_file(db_session, json_file, admin)
                else:
                    log(f"Path is not a JSON file or directory: {path}", "ERROR")
            except Exception as e:
                log(f"Error during import process: {str(e)}", "ERROR")
    finally:
                # No need to close the session, Flask will handle it
                log("Import process completed")
    except Exception as e:
        log(f"Failed to connect to database: {str(e)}", "ERROR")
        return

if __name__ == "__main__":
    main()