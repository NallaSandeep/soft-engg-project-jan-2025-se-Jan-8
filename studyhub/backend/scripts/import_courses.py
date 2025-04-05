"""
import_courses.py

This script imports course data from JSON files into StudyHub database.
It ensures consistency between StudyHub and StudyIndexer by maintaining
the same course codes, week structures, and content organization.

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
        CourseEnrollment, PersonalResource, Question, ResourceFile
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
        if "questions" in data:
            log(f"Found {len(data['questions'])} questions")
            
        return data
    except json.JSONDecodeError as e:
        log(f"JSON parsing error in {file_path}: {str(e)}", "ERROR")
        log(f"Error at line {e.lineno}, column {e.colno}: {e.msg}", "ERROR")
        return None
    except Exception as e:
        log(f"Error parsing {file_path}: {str(e)}", "ERROR")
        return None

def parse_date(date_str):
    """Parse date string to datetime object
    
    Handles ISO format dates like 2025-05-10
    """
    if not date_str:
        return None
        
    try:
        # Handle ISO format (YYYY-MM-DD)
        if isinstance(date_str, str) and len(date_str) == 10 and date_str[4] == '-' and date_str[7] == '-':
            year = int(date_str[:4])
            month = int(date_str[5:7])
            day = int(date_str[8:10])
            return datetime(year, month, day)
        
        # Handle existing datetime objects
        if isinstance(date_str, datetime):
            return date_str
            
        # Default: return current date + 7 days
        return datetime.now() + timedelta(days=7)
    except:
        # Default: return current date + 7 days
        return datetime.now() + timedelta(days=7)

def process_weeks(db_session, course, data):
    """Process weeks and lectures for a course
    
    This function creates weeks and lectures from the data.
    It does NOT use explicit IDs from JSON but creates unique DB IDs.
    """
    weeks_data = data.get("weeks", [])
    if not weeks_data:
        log(f"No weeks found for course {course.code}", "WARNING")
        return []
        
    log(f"Processing {len(weeks_data)} weeks for course {course.code}")
    
    # Map to keep track of JSON week_id -> DB week object
    week_map = {}
    
    weeks = []
    for w_data in weeks_data:
        # Extract required fields - we use number for display labels (Week 1, Week 2)
        json_week_id = w_data.get("week_id")  # We'll map this but NOT use it as the DB ID
        week_number = w_data.get("order") or w_data.get("number")
        if not week_number and json_week_id:
            week_number = json_week_id  # Fall back to week_id as the number if order/number missing
            
        title = w_data.get("title", f"Week {week_number}")
        
        # Check if week already exists for this course+number combination
        existing_week = db_session.query(Week).filter_by(course_id=course.id, number=week_number).first()
        if existing_week:
            log(f"Week {week_number} already exists for course {course.code}, updating...")
            # Update fields
            existing_week.title = title
            existing_week.description = w_data.get("description", "")
            weeks.append(existing_week)
            
            # Add to map even if it's existing
            if json_week_id:
                week_map[json_week_id] = existing_week
                
            continue
            
        # Create new week - DON'T use the JSON week_id for the DB ID
        week = Week(
            course_id=course.id,
            number=week_number,
            title=title,
            description=w_data.get("description", ""),
            is_published=True
        )

        # If LLM_Summary exists in the JSON data, add it to the week object
        if "LLM_Summary" in w_data:
            week.LLM_Summary = w_data["LLM_Summary"]
            log(f"Added LLM_Summary to week {week.number}", level="DEBUG")

        db_session.add(week)
        db_session.flush()  # This assigns a unique DB ID
        
        log(f"Created week {week.number}: {week.title} (DB ID: {week.id})", level="DEBUG")
        weeks.append(week)
        
        # Add to map for later reference
        if json_week_id:
            week_map[json_week_id] = week
        
    db_session.flush()
    
    # Now process lectures for each week
    lectures_data = data.get("lectures", [])
    if lectures_data:
        log(f"Processing {len(lectures_data)} lectures")
        
        for l_data in lectures_data:
            # Get week for this lecture using the JSON week_id and our map
            json_week_id = l_data.get("week_id")
            if not json_week_id:
                log(f"No week_id for lecture {l_data.get('title')}, skipping", "WARNING")
                continue
                
            # Find the week using our mapping
            week = week_map.get(json_week_id)
            if not week:
                # Try by number as fallback
                week_num = int(json_week_id) if str(json_week_id).isdigit() else None
                if week_num:
                    week = next((w for w in weeks if w.number == week_num), None)
                
            if not week:
                log(f"Week {json_week_id} not found for lecture {l_data.get('title')}, skipping", "WARNING")
                continue
                
            # Extract lecture data
            lecture_id = l_data.get("lecture_id")  # Only for logging/reference
            title = l_data.get("title", "Lecture")
            order = l_data.get("order", 1)
            lecture_number = l_data.get("lecture_number", order)
            
            # Check if lecture exists
            existing_lecture = db_session.query(Lecture).filter_by(week_id=week.id, lecture_number=lecture_number).first()
            if existing_lecture:
                log(f"Lecture {lecture_number} already exists for week {week.number}, updating...")
                # Update fields
                existing_lecture.title = title
                existing_lecture.description = l_data.get("description", "")
                
                # Update keywords if present
                if "keywords" in l_data:
                    existing_lecture.keywords = l_data["keywords"]
                    log(f"Updated keywords for lecture {existing_lecture.lecture_number}")
                
                continue
                
            # Create lecture - DON'T use the JSON lecture_id for the DB ID
            resource_type = l_data.get("resource_type", "youtube")
            youtube_url = l_data.get("video_url") or l_data.get("youtube_url")
            transcript = l_data.get("content_transcript", "")
            content_extract = l_data.get("content_extract", "")
            
            # For PDF resources, use content_extract as transcript
            if resource_type == "pdf" and content_extract and not transcript:
                transcript = content_extract
                
            lecture = Lecture(
                week_id=week.id,
                lecture_number=lecture_number,
                title=title,
                description=l_data.get("description", ""),
                content_type=resource_type,
                youtube_url=youtube_url,
                file_path=l_data.get("resource_url", ""),
                transcript=transcript,
                order=order,
                is_published=True
            )

            # Add keywords if present in the lecture data
            if "keywords" in l_data:
                lecture.keywords = l_data["keywords"]
                log(f"Added keywords to lecture {lecture.lecture_number}", level="DEBUG")
            else:
                # Default keywords if none provided
                lecture.keywords = [course.code, "lecture", week.title.split(':')[0] if ':' in week.title else week.title]
                log(f"Added default keywords to lecture {lecture.lecture_number}", level="DEBUG")

            db_session.add(lecture)
            log(f"Created lecture {lecture.lecture_number}: {lecture.title} for week {week.number}", level="DEBUG")
            
    db_session.commit()
    log(f"Processed {len(weeks)} weeks and {len(lectures_data)} lectures for course {course.code}")
    return weeks, week_map

def create_question_bank(db, course, data, week_map, created_by_id=None):
    """Create question bank for the course
    
    This function processes all questions from the JSON and creates them in the database.
    Questions in the JSON should have:
    - content (question text)
    - type (MCQ, MSQ, NUMERIC, etc.)
    - question_options (array of options for MCQ and MSQ)
    - correct_answer (correct option index or value)
    - points (point value for question)
    - explanation (explanation of answer)
    """
    questions_data = data.get("questions", [])
    if not questions_data:
        log(f"No questions found in JSON for course {course.code}", "WARNING")
        return {}
    
    log(f"Creating {len(questions_data)} questions for course {course.code}")
    
    # Dictionary to store question_id -> Question object mapping
    question_map = {}
    
    # Get admin user if created_by_id is not provided
    if not created_by_id:
        admin = db.query(User).filter_by(role="admin").first()
        created_by_id = admin.id if admin else None
    
    for q_data in questions_data:
        # Skip if question already exists
        question_id = q_data.get("question_id")
        if question_id:
            existing = db.query(Question).filter_by(id=question_id).first()
            if existing:
                question_map[question_id] = existing
                log(f"  Question {question_id} already exists, skipping")
                continue
        
        # Get required fields
        content = q_data.get("content")
        q_type = q_data.get("type")
        if not content or not q_type:
            log(f"  Missing required fields for question: {q_data}", "ERROR")
            continue
        
        # Get other fields
        title = q_data.get("title", content[:50] + "...")  # Use truncated content as title if not provided
        options = q_data.get("question_options", [])
        correct_answer = q_data.get("correct_answer")
        points = q_data.get("points", 10)
        explanation = q_data.get("explanation", "")
        
        # Get week and lecture IDs if provided
        json_week_id = q_data.get("week_id")
        week_id = None
        
        # Map the JSON week ID to the actual database week ID
        if json_week_id and json_week_id in week_map:
            week_id = week_map[json_week_id].id
        
        lecture_id = q_data.get("lecture_id")
        
        # Create the question - don't use explicit question_id
        question = Question(
            title=title,
            content=content,
            type=q_type,
            question_options=options,
            correct_answer=correct_answer,
            points=points,
            explanation=explanation,
            course_id=course.id,
            week_id=week_id,
            lecture_id=lecture_id,
            created_by_id=created_by_id,
            status="active"
        )
        
        db.add(question)
        db.flush()  # Get the ID
        
        log(f"  Created question {question.id}: {title[:30]}...", level="DEBUG")
        
        # Store with the question_id from JSON as the key for lookup
        if question_id:
            question_map[question_id] = question
        
        # Also store with the actual DB ID
        question_map[question.id] = question
    
    db.commit()
    log(f"Created {len(question_map)} questions for course {course.code}")
    return question_map

def create_assignments_from_json(db, course, data, question_map, week_map):
    """Create assignments for a course from JSON data
    
    This function creates assignments and links them to questions.
    It uses the question_map to link questions to assignments.
    """
    assignments_data = data.get("assignments", [])
    if not assignments_data:
        log(f"No assignments found in JSON for course {course.code}", "WARNING")
        return []
    
    log(f"Creating {len(assignments_data)} assignments for course {course.code}")
    
    # Organize questions by week for fallback
    week_questions = {}
    for question in question_map.values():
        if question.week_id not in week_questions:
            week_questions[question.week_id] = []
        week_questions[question.week_id].append(question)
    
    assignments = []
    for a_data in assignments_data:
        # Skip if assignment already exists
        assignment_id = a_data.get("assignment_id")
        if assignment_id:
            existing = db.query(Assignment).filter_by(id=assignment_id).first()
            if existing:
                log(f"  Assignment {assignment_id} already exists, skipping")
                assignments.append(existing)
                continue

        # Get required fields
        title = a_data.get("title")
        json_week_id = a_data.get("week_id")
        
        if not title or not json_week_id:
            log(f"  Missing required fields for assignment: {a_data}", "ERROR")
            continue

        # Get week using our week map
        week = None
        if json_week_id in week_map:
            week = week_map[json_week_id]
        
        # If not found through mapping, try direct lookup
        if not week:
            week = db.query(Week).filter_by(number=json_week_id, course_id=course.id).first()
        
        if not week:
            log(f"  Week {json_week_id} not found for assignment {title}", "ERROR")
            continue

        # Get other fields
        description = a_data.get("description", "")
        assignment_type = a_data.get("type", "practice")  # Default to practice
        start_date = parse_date(a_data.get("start_date"))
        due_date = parse_date(a_data.get("due_date"))
        is_published = a_data.get("is_published", True)

        log(f"  Creating assignment: {title} (Week {week.number}, Type: {assignment_type})", level="DEBUG")

        # Create assignment - DON'T use the assignment_id from JSON
        assignment = Assignment(
            title=title,
            description=description,
            type=assignment_type,
            week_id=week.id,
            start_date=start_date,
            due_date=due_date,
            is_published=is_published
        )

        db.add(assignment)
        db.flush()  # Get the ID

        # Link questions to assignment
        question_ids = a_data.get("question_ids", [])

        # If no question_ids specified, use questions from this week
        if not question_ids and week.id in week_questions:
            available_questions = week_questions[week.id]
            
            # Determine num_questions based on assignment type
            num_questions = min(10 if assignment_type == "graded" else 5, len(available_questions))
            
            # Use the first num_questions questions from the week
            question_objects = available_questions[:num_questions]
            log(f"  No question_ids specified, using {num_questions} questions from week {week.number}")
            
            for order, question in enumerate(question_objects, 1):
                # Check if this question is already linked to this assignment
                existing_link = db.query(AssignmentQuestion).filter_by(
                    assignment_id=assignment.id,
                    question_id=question.id
                ).first()
                
                if existing_link:
                    log(f"    Question {question.id} is already linked to assignment {assignment.title}, skipping duplicate.", level="WARNING")
                    continue
                    
                assignment_question = AssignmentQuestion(
                    assignment_id=assignment.id,
                    question_id=question.id,
                    order=order
                )
                db.add(assignment_question)
                log(f"    Added question {question.id} to assignment {assignment.title}", level="DEBUG")
        elif question_ids:
            log(f"  Adding {len(question_ids)} questions to assignment {assignment.title}")
            
            for order, q_id in enumerate(question_ids, 1):
                # Check if question exists in our map or database
                question = question_map.get(q_id)
                if not question:
                    question = db.query(Question).filter_by(id=q_id).first()
                
                if not question:
                    log(f"  Question {q_id} not found for assignment {assignment.title}", "WARNING")
                    continue
                
                # Create assignment question link
                # Check if this question is already linked to this assignment
                existing_link = db.query(AssignmentQuestion).filter_by(
                    assignment_id=assignment.id,
                    question_id=question.id
                ).first()
                
                if existing_link:
                    log(f"    Question {question.id} is already linked to assignment {assignment.title}, skipping duplicate.", level="WARNING")
                    continue
                    
                assignment_question = AssignmentQuestion(
                    assignment_id=assignment.id,
                    question_id=question.id,
                    order=order
                )
                
                db.add(assignment_question)
                log(f"    Added question {question.id} to assignment {assignment.title}", level="DEBUG")
        else:
            log(f"  WARNING: No questions added to assignment {assignment.title} - no question_ids and no questions for week {week.number}")
        
        assignments.append(assignment)
        log(f"  Created assignment {assignment.id}: {assignment.title}", level="DEBUG")
    
    db.commit()
    log(f"Created {len(assignments)} assignments for course {course.code}")
    return assignments

def create_sample_enrollment(db_session, course):
    """Create a sample enrollment for student1 (ID 3)
    
    This creates a sample enrollment for the course to demonstrate enrollment functionality.
    """
    try:
        # Find student1 (ID 3)
        student = db_session.query(User).filter_by(id=3).first()
        if not student:
            student = db_session.query(User).filter_by(username="student1").first()
            
        if not student:
            log(f"Sample student (student1) not found, skipping enrollment", "WARNING")
            return False
            
        # Check if enrollment already exists
        existing = db_session.query(CourseEnrollment).filter_by(
            user_id=student.id,
            course_id=course.id
        ).first()
        
        if existing:
            log(f"Student {student.username} already enrolled in course {course.code}", "INFO")
            return True
            
        # Create enrollment
        enrollment = CourseEnrollment(
            user_id=student.id,
            course_id=course.id,
            role="student",
            status="active",
            enrolled_at=datetime.now()
        )
        db_session.add(enrollment)
        db_session.commit()
        log(f"Enrolled student {student.username} in course {course.code}", level="DEBUG")
        return True
    except Exception as e:
        log(f"Error creating sample enrollment: {str(e)}", "ERROR")
        return False

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
            course = existing_courses[code]
            log(f"Course {code} already exists", "INFO")
            log(f"Updating content for existing course {code}")
            # Update relevant fields from JSON, including acronyms/synonyms
            course.name = course_info.get("title", course.name)
            course.description = course_info.get("description", course.description)
            course.acronyms = course_info.get("acronyms", course.acronyms or {})
            course.synonyms = course_info.get("synonyms", course.synonyms or {})
            log(f"  Updating existing course {code} - Acronyms: {len(course.acronyms)}, Synonyms: {len(course.synonyms)}", "DEBUG")
            # Update other potential fields like instructor_id, credits, etc. if needed
            # course.instructor_id = course_info.get("instructor_id", course.instructor_id)
            # course.credits = course_info.get("credits", course.credits)
            log(f"  Course model {code} (before commit) - Acronyms: {json.dumps(course.acronyms)}, Synonyms: {json.dumps(course.synonyms)}", "DEBUG") # Log before commit
            db_session.commit() # Commit updates for existing course
        else:
            # Create new course
            title = course_info.get("title", "")
            description = course_info.get("description", "")
            # Get LLM_Summary and extract acronyms/synonyms from there
            llm_summary = course_info.get("LLM_Summary", {})
            acronyms = llm_summary.get("acronyms", {})
            synonyms = llm_summary.get("synonyms", {})
            
            # Log what we extracted for debugging
            log(f"  Extracting from LLM_Summary - Found acronyms: {len(acronyms) if isinstance(acronyms, dict) else 0}, synonyms: {len(synonyms) if isinstance(synonyms, dict) else 0}", "DEBUG")
            
            course = Course(
                code=code,
                name=title,
                description=description,
                acronyms=acronyms,  # Add acronyms
                synonyms=synonyms, # Add synonyms
                created_by_id=admin.id,
                is_active=True,
                enrollment_type='open',
                max_students=100,
                start_date=datetime.now().date(),
                end_date=(datetime.now() + timedelta(days=90)).date()
            )
            log(f"  Creating new course {code} - Acronyms: {len(acronyms)}, Synonyms: {len(synonyms)}", "DEBUG")
            log(f"  Course model {code} (before adding) - Acronyms: {json.dumps(acronyms)}, Synonyms: {json.dumps(synonyms)}", "DEBUG") # Log before add
            
            db_session.add(course)
            db_session.commit() 
            log(f"Created course: {code} - {title}")
        
        # Process weeks and lectures
        weeks, week_map = process_weeks(db_session, course, data)
        
        # Process question bank first
        log("Creating question bank...")
        question_map = create_question_bank(db_session, course, data, week_map, admin.id)
        
        # Process assignments (link to questions)
        log("Creating assignments...")
        assignments = create_assignments_from_json(db_session, course, data, question_map, week_map)
        
        # Create an enrollment for student1 (as a sample student)
        create_sample_enrollment(db_session, course)
        
        log(f"Successfully processed course {code} from {json_file}")
        return True
    except Exception as e:
        log(f"Error processing file {json_file}: {str(e)}", "ERROR")
        import traceback
        log(traceback.format_exc(), "ERROR")
        db_session.rollback()
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
                import traceback
                log(traceback.format_exc(), "ERROR")
            finally:
                # No need to close the session, Flask will handle it
                log("Import process completed")
    except Exception as e:
        log(f"Failed to connect to database: {str(e)}", "ERROR")
        return

if __name__ == "__main__":
    main()