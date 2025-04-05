"""
Database Initialization Script (Modular Version)
------------------------------------------------
This script initializes the StudyHub database using a modular approach:

Phase 1: Create users (admin, teachers, students)
Phase 2: Import course content from JSON files
Phase 3: Create enrollments and personal resources
Phase 4: Sync personal resources with StudyIndexer
Phase 5: Sync graded assignments with StudyIndexer for integrity checking

This approach ensures:
- Better separation of concerns
- Consistent data between StudyHub and StudyIndexer
- Maintainable and extensible initialization process
"""

import os
import sys
import json
import glob
from datetime import datetime, timedelta

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

# Import the app and database
try:
    from app import db, create_app
    from app.models import User, Course, Week, Lecture, Assignment, AssignmentQuestion, Question, \
        CourseEnrollment, PersonalResource, AssignmentSubmission, ResourceFile
    
    app = create_app()
    print("[INFO] Successfully imported StudyHub models and database")
except ImportError as e:
    print(f"[ERROR] Failed to import StudyHub models: {str(e)}")
    sys.exit(1)

# Import specific modules for phases
from scripts.import_courses import main as import_courses
#from scripts.create_assignments import main as create_assignments
from app.utils.sync_personal_resources import sync_personal_resources
from app.utils.sync_graded_assignments import sync_graded_assignments

# Constants - Database credentials 
ADMIN_EMAIL = "admin@studyhub.com"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

TEACHER_EMAIL = "teacher@studyhub.com"
TEACHER_USERNAME = "teacher"
TEACHER_PASSWORD = "teacher123"

# Student credentials
STUDENT_COUNT = 5
STUDENT_PASSWORD = "student123"

# Database reset flag - Set to True to completely recreate the database
RESET_DATABASE = True

# StudyIndexer sync flags
SYNC_PERSONAL_RESOURCES = True
SYNC_GRADED_ASSIGNMENTS = True
SYNC_BATCH_SIZE = 50

def log(message, level="INFO"):
    """Log messages with timestamp and level"""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{level}] {message}")

def reset_database(db_session):
    """Reset the database by dropping and recreating all tables"""
    if not RESET_DATABASE:
        log("Database reset skipped (RESET_DATABASE=False)")
        return
        
    log("RESETTING DATABASE - THIS WILL DELETE ALL DATA")
    
    try:
        log("Dropping all tables...")
        db.drop_all()
        
        log("Creating tables...")
        db.create_all()
        
        log("Database reset completed successfully")
    except Exception as e:
        log(f"Error resetting database: {str(e)}", "ERROR")
        import traceback
        log(traceback.format_exc(), "ERROR")

def run_phase1_create_users(db_session):
    """
    Phase 1: Create users (admin, teachers, students)
    """
    log("PHASE 1: CREATING USERS")
    
    # Check if users already exist
    existing_users = db_session.query(User).all()
    if existing_users:
        log(f"Found {len(existing_users)} existing users")
        admin = db_session.query(User).filter_by(email=ADMIN_EMAIL).first()
        if admin:
            log(f"Admin user already exists: {admin.username} ({admin.email})")
            return admin.id, [u.id for u in existing_users if u.role == 'student']
    
    # Create admin user
    log("Creating admin user...")
    admin = User(
        username=ADMIN_USERNAME,
        email=ADMIN_EMAIL,
        password=ADMIN_PASSWORD,
        role="admin",
        first_name="Admin",
        last_name="User",
        is_active=True
    )
    db_session.add(admin)
    db_session.flush()
    log(f"Created admin user: {admin.username} (ID: {admin.id})")
    
    # # Create teacher
    # log("Creating teacher user...")
    # teacher = User(
    #     username=TEACHER_USERNAME,
    #     email=TEACHER_EMAIL,
    #     password=TEACHER_PASSWORD,
    #     role="teacher",
    #             is_active=True
    # )
    # db_session.add(teacher)
    # db_session.flush()
    # log(f"Created teacher user: {teacher.username} (ID: {teacher.id})")
    
    # Create students
    student_ids = []
    log(f"Creating {STUDENT_COUNT} student users...")
    for i in range(1, STUDENT_COUNT + 1):
        username = f"student{i}"
        email = f"student{i}@studyhub.com"
        
        student = User(
            username=username,
            email=email,
            password=STUDENT_PASSWORD,
            role="student",
            first_name=f"Student{i}",
            last_name="User",
            is_active=True
        )
        db_session.add(student)
        db_session.flush()
        student_ids.append(student.id)
        log(f"Created student: {username} (ID: {student.id})", level="DEBUG")
    
    # Store admin_id before committing
    admin_id = admin.id
    
    db_session.commit()
    log("PHASE 1 COMPLETED - USERS CREATED")
    
    return admin_id, student_ids

def run_phase2_import_courses(db_session, admin_id):
    """
    Phase 2: Import course content from JSON files
    Uses the import_courses.py script to load courses from JSON
    """
    log("PHASE 2: IMPORTING COURSE CONTENT")
    
    try:
        log("Calling import_courses.py with verbose logging...")
        
        # Set verbose logging global in the import_courses module
        import scripts.import_courses
        
        # Manually run the import_courses functionality with the course directory
        course_data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "course")
        
        if os.path.exists(course_data_dir):
            log(f"Found course data directory: {course_data_dir}")
            json_files = glob.glob(os.path.join(course_data_dir, "*.json"))
            
            if json_files:
                log(f"Found {len(json_files)} JSON files in {course_data_dir}")
                
                # Get admin user
                admin = db_session.query(User).filter_by(email=ADMIN_EMAIL).first()
                
                for json_file in json_files:
                    log(f"Processing {os.path.basename(json_file)}...")
                    scripts.import_courses.process_single_file(db_session, json_file, admin)
            else:
                log(f"No JSON files found in {course_data_dir}", "ERROR")
        else:
            log(f"Course data directory not found: {course_data_dir}", "ERROR")
        
        courses = db_session.query(Course).all()
    except Exception as e:
        log(f"Error during course import: {str(e)}", "ERROR")
        import traceback
        log(traceback.format_exc(), "ERROR")
        courses = []
    
    return courses

def run_phase3_create_enrollments(db_session, student_ids, courses):
    """
    Phase 3: Create enrollments and personal resources
    - Creates enrollments for all students in all courses
    - Creates personal resources for each student in their enrolled courses
    """
    log("PHASE 3: CREATING ENROLLMENTS AND PERSONAL RESOURCES")
    
    # Create enrollments for all students in all courses
    for student_id in student_ids:
        for course in courses:
            # Skip student1 as it was enrolled during course import
            if student_id == 3:  # student1 has ID 3
                continue
                
            # Check if enrollment already exists
            existing = db_session.query(CourseEnrollment).filter_by(
                user_id=student_id,
                course_id=course.id,
                status='active'
            ).first()
            
            if existing:
                log(f"Student {student_id} already enrolled in course {course.code}", "INFO")
                continue
                
            # Create enrollment
            enrollment = CourseEnrollment(
                user_id=student_id,
                course_id=course.id,
                role="student",
                status="active",
                enrolled_at=datetime.now()
            )
            db_session.add(enrollment)
            log(f"Enrolled student {student_id} in course {course.code}", level="DEBUG")
    
    # Create personal resources for all students in their enrolled courses
    for course in courses:
        # Get lectures for the course
        lectures = db_session.query(Lecture).join(Week).filter(Week.course_id == course.id).all()
        
        if not lectures:
            log(f"No lectures found for course {course.code}", "WARNING")
            continue
        
        log(f"Found {len(lectures)} lectures for course {course.code}")
        
        # Create personal resources for all lectures for student1, first 5 for others
        for lecture in lectures:
            for student_id in student_ids:
                # For student1, create resources for all lectures
                # For others, only create for first 5 lectures
                if student_id != 3 and lecture.lecture_number > 5:
                    continue
                
                # Create the personal resource
                resource = PersonalResource(
                    user_id=student_id,
                    course_id=course.id,
                    name=f"Notes on {lecture.title}",  # Use name instead of title
                    description=f"My personal notes for {lecture.title}",
                    is_active=True,
                    settings={"visibility": "private"}  # Use settings instead of is_public
                )
                db_session.add(resource)
                db_session.flush()  # Need to flush to get the resource.id
                
                # Create the resource file to hold the content
                resource_file = ResourceFile(
                    resource_id=resource.id,
                    name=f"Lecture {lecture.lecture_number} Notes.txt",
                    type="text",  # Use text type for notes
                    content=f"My personal notes for {lecture.title}.\n\nKey points:\n- Important concept 1\n- Important concept 2\n- Remember to review this before the exam",
                    file_type="text/plain",
                    file_size=250  # Approximate size
                )
                db_session.add(resource_file)
                log(f"Created personal resource for student {student_id} in course {course.code} for lecture {lecture.lecture_number}", level="DEBUG")
    
    db_session.commit()

def sync_with_studyindexer(courses):
    """
    Sync courses with StudyIndexer to ensure consistency
    This calls the StudyIndexer API to index the courses
    
    StudyIndexer has several vector databases that need to be updated:
    1. CourseContent - For within-course search (for RAG)
    2. CourseSelector - For course selection based on query (for recommending courses)
    """
    log("SYNCING COURSES WITH STUDYINDEXER...")
    
    try:
        import requests
        import json
        from requests.exceptions import RequestException
        
        # URLs for the StudyIndexer APIs
        STUDYINDEXER_BASE_URL = "http://127.0.0.1:8081"
        COURSE_CONTENT_URL = f"{STUDYINDEXER_BASE_URL}/api/v1/course-content"
        COURSE_SELECTOR_URL = f"{STUDYINDEXER_BASE_URL}/api/v1/course-selector/index"
        
        courses_synced = 0
        course_content_success = 0
        course_selector_success = 0
        
        for course in courses:
            log(f"Syncing course {course.code} with StudyIndexer...", level="DEBUG")
            
            # Get course weeks
            weeks = db.session.query(Week).filter_by(course_id=course.id).all()
            
            # Format weeks into properly structured array
            week_data = []
            for week in weeks:
                week_data.append({
                    "week_id": week.id,
                    "course_id": course.id,
                    "order": week.number,
                    "title": week.title,
                    "estimated_hours": getattr(week, 'estimated_hours', 25)  # Default to 25 if not present
                })
            
            # Collect all lectures as a separate top-level array
            lectures_data = []
            for week in weeks:
                lectures = db.session.query(Lecture).filter_by(week_id=week.id).all()
                
                for lecture in lectures:
                    lecture_entry = {
                        "lecture_id": lecture.id,
                        "week_id": week.id,
                        "order": getattr(lecture, 'lecture_number', 1),  # Get lecture_number if exists
                        "title": lecture.title,
                        "resource_type": lecture.content_type
                    }
                    
                    # Add URL based on content type
                    if lecture.content_type == "youtube" and hasattr(lecture, 'youtube_url'):
                        lecture_entry["video_url"] = lecture.youtube_url
                    elif hasattr(lecture, 'file_path') and lecture.file_path:
                        lecture_entry["resource_url"] = lecture.file_path
                        
                    # Add transcript/content if available
                    if hasattr(lecture, 'transcript') and lecture.transcript:
                        lecture_entry["content_transcript"] = lecture.transcript
                    
                    # Add duration if available or default
                    lecture_entry["duration_minutes"] = getattr(lecture, 'duration', 45)
                    
                    # Add keywords if available
                    if hasattr(lecture, 'keywords') and lecture.keywords:
                        lecture_entry["keywords"] = lecture.keywords
                    else:
                        lecture_entry["keywords"] = [course.code, "lecture", week.title.split(':')[0] if ':' in week.title else week.title]
                    
                    # Ensure each lecture has access to course and week summaries
                    if hasattr(week, 'LLM_Summary') and week.LLM_Summary:
                        lecture_entry["week_LLM_Summary"] = week.LLM_Summary
                    
                    lectures_data.append(lecture_entry)
            
            # Create LLM_Summary if not present (using course description)
            llm_summary = None
            if hasattr(course, 'LLM_Summary') and course.LLM_Summary:
                llm_summary = course.LLM_Summary
            else:
                llm_summary = {
                    "summary": course.description,
                    "concepts_covered": [],
                    "concepts_not_covered": []
                }
            
            # Structure the final course data according to expected format
            course_data = {
                "course": {
                    "course_id": course.id,
                    "code": course.code,
                    "title": course.name,  # StudyHub uses 'name', StudyIndexer expects 'title'
                    "description": course.description,
                    "instructor_id": course.created_by_id,
                    "credits": getattr(course, 'credits', 3),  # Default to 3 if not present
                    "department": getattr(course, 'department', "Computer Science"),
                    "LLM_Summary": llm_summary,
                    "acronyms": course.acronyms or {}, # Add acronyms
                    "synonyms": course.synonyms or {}  # Add synonyms
                },
                "weeks": week_data,
                "lectures": lectures_data
            }
            
            # --- Log Payload --- BEGIN
            log(f"DEBUG: Payload for {course.code} - Acronyms: {json.dumps(course_data['course']['acronyms'])}, Synonyms: {json.dumps(course_data['course']['synonyms'])}", "DEBUG")
            # --- Log Payload --- END

            # Add assignments if they exist
            assignment_data = []
            for week in weeks:
                assignments = db.session.query(Assignment).filter_by(week_id=week.id).all()
                for assignment in assignments:
                    assignment_entry = {
                        "assignment_id": assignment.id,
                        "week_id": week.id,
                        "title": assignment.title,
                        "description": assignment.description,
                        "type": assignment.type,
                        "due_date": str(assignment.due_date) if hasattr(assignment, 'due_date') else None,
                        "start_date": str(assignment.start_date) if hasattr(assignment, 'start_date') else None,
                        "is_published": getattr(assignment, 'is_published', True)
                    }
                    
                    # Get question IDs if needed
                    question_ids = []
                    assignment_questions = db.session.query(AssignmentQuestion).filter_by(assignment_id=assignment.id).all()
                    for aq in assignment_questions:
                        question_ids.append(aq.question_id)
                    
                    if question_ids:
                        assignment_entry["question_ids"] = question_ids
                        
                    assignment_data.append(assignment_entry)
            
            if assignment_data:
                course_data["assignments"] = assignment_data
                
            # 1. Sync with StudyIndexer CourseContent API
            try:
                log(f"Calling StudyIndexer CourseContent API for {course.code}...", "DEBUG")
                content_response = requests.post(
                    COURSE_CONTENT_URL, 
                    json=course_data,
                    headers={"Content-Type": "application/json"},
                    timeout=10  # Add 10 second timeout
                )
                
                if content_response.status_code == 200:
                    log(f"Successfully synced course {course.code} with CourseContent API", level="DEBUG")
                    course_content_success += 1
                else:
                    log(f"Failed to sync course {course.code} with CourseContent API. Status: {content_response.status_code}", "ERROR")
                    log(f"Response: {content_response.text}", "ERROR")
                    
            except requests.exceptions.Timeout:
                log(f"Timeout connecting to StudyIndexer CourseContent API for course {course.code}", "ERROR")
                log("Please ensure StudyIndexer is running before running init_db.py", "ERROR")
            except RequestException as e:
                log(f"Error connecting to StudyIndexer CourseContent API for course {course.code}: {str(e)}", "ERROR")
                
            # 2. Sync with StudyIndexer CourseSelector API
            try:
                log(f"Calling StudyIndexer CourseSelector API for {course.code}...", "DEBUG")
                selector_response = requests.post(
                    COURSE_SELECTOR_URL, 
                    json=course_data,
                    headers={"Content-Type": "application/json"},
                    timeout=10  # Add 10 second timeout
                )
                
                if selector_response.status_code == 200:
                    log(f"Successfully synced course {course.code} with CourseSelector API", level="DEBUG")
                    course_selector_success += 1
                else:
                    log(f"Failed to sync course {course.code} with CourseSelector API. Status: {selector_response.status_code}", "ERROR")
                    log(f"Response: {selector_response.text}", "ERROR")
                    
            except requests.exceptions.Timeout:
                log(f"Timeout connecting to StudyIndexer CourseSelector API for course {course.code}", "ERROR")
                log("Please ensure StudyIndexer is running before running init_db.py", "ERROR")
            except RequestException as e:
                log(f"Error connecting to StudyIndexer CourseSelector API for course {course.code}: {str(e)}", "ERROR")
                
            # If either API call succeeded, count the course as synced
            if course_content_success > 0 or course_selector_success > 0:
                courses_synced += 1
                
        # Log summary of sync operations
        log(f"Sync summary: {courses_synced} courses processed")
        log(f"CourseContent API: {course_content_success} successes")
        log(f"CourseSelector API: {course_selector_success} successes")
        
        if courses_synced == 0:
            log("No courses were synced with StudyIndexer", "WARNING")
            log("StudyIndexer service may not be running.", "WARNING")
            
    except ImportError:
        log("Could not import 'requests' module. Please install it with 'pip install requests'", "ERROR")
        log("StudyIndexer synchronization skipped.", "WARNING")
    except Exception as e:
        log(f"Error during StudyIndexer synchronization: {str(e)}", "ERROR")
        import traceback
        log(traceback.format_exc(), "ERROR")

def run_phase4_sync_personal_resources(db_session):
    """
    Phase 4: Sync personal resources with StudyIndexer
    """
    if not SYNC_PERSONAL_RESOURCES:
        log("Personal resource sync skipped (SYNC_PERSONAL_RESOURCES=False)")
        return
        
    log("PHASE 4: SYNCING PERSONAL RESOURCES WITH STUDYINDEXER")
    
    try:
        # Count resources to sync
        resource_count = db_session.query(PersonalResource).count()
        log(f"Found {resource_count} personal resources to sync")
        
        if resource_count == 0:
            log("No personal resources found to sync", "WARNING")
            return
            
        # Sync personal resources with StudyIndexer
        log("Starting personal resource sync...")
        results = sync_personal_resources(batch_size=SYNC_BATCH_SIZE)
        
        # Log results
        log(f"Sync completed: {results['added']} added, {results['failed']} failed, {results['total']} total")
        
        if results['failed'] > 0:
            log(f"Failed to sync {results['failed']} personal resources", "WARNING")
        else:
            log("All personal resources synced successfully")
            
    except Exception as e:
        log(f"Error during personal resource sync: {str(e)}", "ERROR")
        import traceback
        log(traceback.format_exc(), "ERROR")

def run_phase5_sync_graded_assignments(db_session):
    """
    Phase 5: Sync graded assignments with StudyIndexer for integrity checking
    """
    if not SYNC_GRADED_ASSIGNMENTS:
        log("Graded assignment sync skipped (SYNC_GRADED_ASSIGNMENTS=False)")
        return
        
    log("PHASE 5: SYNCING GRADED ASSIGNMENTS WITH STUDYINDEXER")
    
    try:
        # Count assignments to sync
        assignments = db_session.query(Assignment).filter_by(type="graded").count()
        log(f"Found {assignments} graded assignments to sync")
        
        if assignments == 0:
            log("No graded assignments found to sync", "WARNING")
            return
            
        # Sync graded assignments with StudyIndexer
        log("Starting graded assignment sync...")
        results = sync_graded_assignments(batch_size=SYNC_BATCH_SIZE)
        
        # Log results
        log(f"Sync completed: {results['added']} added, {results['failed']} failed, {results['total']} total")
        
        if results['failed'] > 0:
            log(f"Failed to sync {results['failed']} assignments", "WARNING")
        else:
            log("All graded assignments synced successfully")
            
    except Exception as e:
        log(f"Error during graded assignment sync: {str(e)}", "ERROR")
        import traceback
        log(traceback.format_exc(), "ERROR")

def main():
    """Main function to run the database initialization process"""
    log("Starting database initialization...")
    
    # Create application context
    with app.app_context():
        # Reset database if requested
        reset_database(db.session)
        
        # Phase 1: Create users
        admin_id, student_ids = run_phase1_create_users(db.session)
        
        # Phase 2: Import courses
        courses = run_phase2_import_courses(db.session, admin_id)
        
        # Phase 3: Create enrollments and personal resources
        run_phase3_create_enrollments(db.session, student_ids, courses)
        
        # Phase 4: Sync with StudyIndexer
        sync_with_studyindexer(courses)
        
        # Phase 5: Sync personal resources with StudyIndexer
        run_phase4_sync_personal_resources(db.session)
        
        # Phase 6: Sync graded assignments with StudyIndexer
        run_phase5_sync_graded_assignments(db.session)
    
    log("Database initialization completed")

if __name__ == "__main__":
    main()