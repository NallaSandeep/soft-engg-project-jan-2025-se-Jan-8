"""
Enhanced personal resources script for StudyHub and StudyIndexer integration.
This script adds rich personal resources to StudyHub and syncs them to StudyIndexer.
"""
import os
import sys
import json
import logging
import requests
import random
from datetime import datetime, timedelta
from pathlib import Path

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import necessary modules from the StudyHub application
from app import create_app, db
from app.models.user import User
from app.models.course import Course, CourseEnrollment
from app.models.personal_resource import PersonalResource, ResourceFile

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def log(message):
    """Log a message with timestamp."""
    logger.info(message)
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")

def get_students_with_courses():
    """
    Get all students with their subscribed courses.
    
    Returns:
        List of dictionaries with student information and subscribed courses
    """
    students_with_courses = []
    students = User.query.filter_by(role='student').all()
    
    for student in students:
        enrollments = CourseEnrollment.query.filter_by(
            user_id=student.id,
            status='active'
        ).all()
        
        courses = []
        for enrollment in enrollments:
            course = Course.query.get(enrollment.course_id)
            if course:
                courses.append({
                    'id': course.id,
                    'code': course.code,
                    'name': course.name,
                    'description': course.description
                })
        
        # Use first_name and last_name from User model
        display_name = f"{student.first_name} {student.last_name}" if student.first_name and student.last_name else student.username
        
        students_with_courses.append({
            'student': {
                'id': student.id,
                'username': student.username,
                'display_name': display_name,
                'first_name': student.first_name,
                'last_name': student.last_name,
                'email': student.email
            },
            'courses': courses
        })
    
    return students_with_courses

def generate_course_content(course):
    """
    Generate course-specific content for personal resources.
    
    Args:
        course: Course dictionary
        
    Returns:
        Dictionary with various generated content
    """
    # Key topics for different course types
    topics_by_subject = {
        'CS': [
            'Object-Oriented Programming', 'Algorithms', 'Data Structures', 
            'Software Engineering', 'Database Systems', 'Web Development'
        ],
        'MATH': [
            'Linear Algebra', 'Calculus', 'Discrete Mathematics', 
            'Statistics', 'Numerical Methods', 'Probability Theory'
        ],
        'PHYS': [
            'Classical Mechanics', 'Electromagnetism', 'Thermodynamics', 
            'Quantum Mechanics', 'Optics', 'Relativity'
        ],
        'BIO': [
            'Cell Biology', 'Genetics', 'Ecology', 
            'Physiology', 'Molecular Biology', 'Evolutionary Biology'
        ]
    }
    
    # Determine subject area from course code
    subject = 'CS'  # Default
    for key in topics_by_subject.keys():
        if key in course['code']:
            subject = key
            break
    
    # Select random topics for this course
    course_topics = random.sample(topics_by_subject[subject], min(4, len(topics_by_subject[subject])))
    
    # Generate weekly themes
    weekly_themes = [
        'Fundamentals and Introduction',
        'Core Concepts and Principles',
        'Advanced Topics and Applications',
        'Implementation and Problem Solving'
    ]
    
    return {
        'topics': course_topics,
        'weekly_themes': weekly_themes,
        'textbook': f"Comprehensive Guide to {course['name']}",
        'external_resources': [
            f"https://example.com/{subject.lower()}/tutorials",
            f"https://example.com/{subject.lower()}/practice"
        ]
    }

def create_enhanced_personal_resources():
    """
    Create enhanced personal resources with rich content and structure.
    """
    log("Creating enhanced personal resources...")
    students_with_courses = get_students_with_courses()
    
    # Track all resources created
    created_resources = []
    
    for student_data in students_with_courses:
        student = student_data['student']
        log(f"Processing resources for student: {student['display_name']} ({student['id']})")
        
        for course_data in student_data['courses']:
            log(f"  Creating resources for course: {course_data['code']} ({course_data['id']})")
            
            course = Course.query.get(course_data['id'])
            content_data = generate_course_content(course_data)
            
            # Create the main resource container
            resource = PersonalResource(
                user_id=student['id'],
                course_id=course.id,
                name=f"Study Materials - {course.code}",
                description=f"Comprehensive study materials and notes for {course.name}",
                is_active=True,
                settings={
                    'visibility': 'private',
                    'tags': [course.code, 'notes', 'study materials']
                }
            )
            db.session.add(resource)
            db.session.flush()  # Get resource ID
            
            # Create course overview note
            overview_note = ResourceFile(
                resource_id=resource.id,
                name="Course Overview.md",
                type="note",
                content=f"""# {course.name} ({course.code}) - Course Overview

## Course Description
{course.description}

## Key Topics
{chr(10).join([f"- {topic}" for topic in content_data['topics']])}

## Learning Objectives
- Understand the fundamental concepts of {course.name}
- Apply theoretical knowledge to practical problems
- Develop analytical skills related to the subject matter
- Master key techniques and methodologies

## Resources
- Textbook: "{content_data['textbook']}"
- Course slides and lecture recordings
- Practice exercises and solutions
{chr(10).join([f"- {url}" for url in content_data['external_resources']])}
                """,
                file_type="text/markdown",
                file_size=500  # Approximate size
            )
            db.session.add(overview_note)
            
            # Create weekly notes (for weeks 1-4)
            for week_num in range(1, 5):
                week_theme = content_data['weekly_themes'][week_num-1]
                week_topics = random.sample(content_data['topics'], min(2, len(content_data['topics'])))
                
                week_note = ResourceFile(
                    resource_id=resource.id,
                    name=f"Week {week_num} Notes.md",
                    type="note",
                    content=f"""# Week {week_num}: {week_theme}

## Lecture Summary
Key points from Week {week_num} lectures:

- {week_topics[0]}: core principles and fundamentals
- {week_topics[-1]}: application and examples
- Integration with previous topics
- Practical implementation considerations

## Study Notes
My personal notes on this week's material:

1. The relationship between {week_topics[0]} and {week_topics[-1]} is crucial for understanding the overall subject
2. When implementing {week_topics[0]}, always consider the constraints of {week_topics[-1]}
3. Practice examples from Chapter {week_num+1} are especially helpful for exam preparation
4. Additional research needed on {random.choice(content_data['topics'])}

## Questions for Office Hours
- How does {week_topics[0]} relate to the real-world scenario of {course.name.split()[-1]}?
- Can we apply methodology from {week_topics[-1]} to problem types in {week_topics[0]}?
                    """,
                    file_type="text/markdown",
                    file_size=350  # Approximate size
                )
                db.session.add(week_note)
            
            # Create an assignment guide file
            assignment_guide = ResourceFile(
                resource_id=resource.id,
                name="Assignment Tips.md",
                type="note",
                content=f"""# Assignment Guidelines for {course.code}

## Assignment Structure
Most assignments in this course follow this structure:
- Problem statement (10%)
- Methodology (30%)
- Implementation (40%)
- Analysis and conclusions (20%)

## Tips for Success
1. Start early and plan your approach
2. Reference lecture materials for methodology
3. Be thorough in your implementation
4. Provide detailed analysis in your conclusions

## Common Pitfalls
- Misinterpreting the problem statement
- Insufficient methodology explanation
- Incomplete implementation
- Superficial analysis

## Example Problems
Here are some example problems similar to what you might encounter:

1. Apply {content_data['topics'][0]} to solve a practical problem in {content_data['topics'][-1]}
2. Compare and contrast different approaches to {content_data['topics'][1]}
3. Implement a solution using concepts from {content_data['topics'][2]}
                """,
                file_type="text/markdown",
                file_size=300  # Approximate size
            )
            db.session.add(assignment_guide)
            
            # Create a PDF reference file link
            reference_link = ResourceFile(
                resource_id=resource.id,
                name=f"{course.code} Textbook Reference.pdf",
                type="file",  # This is a file, not just a note
                content="",  # No content for file type
                file_path=f"/resources/{course.code.lower()}_reference.pdf",  # Path to file
                file_type="application/pdf",
                file_size=2048  # 2MB approx
            )
            db.session.add(reference_link)
            
            # Track this resource
            created_resources.append({
                'resource_id': resource.id,
                'student_id': student['id'],
                'course_id': course.id
            })
    
    db.session.commit()
    log(f"Enhanced personal resources created successfully! Created {len(created_resources)} resources")
    return created_resources

def sync_resources_to_studyindexer(api_url="http://localhost:8081"):
    """
    Sync personal resources from StudyHub to StudyIndexer.
    
    Args:
        api_url: StudyIndexer API URL
    """
    log(f"Syncing personal resources to StudyIndexer at {api_url}...")
    
    # Get all personal resources with their files
    personal_resources = PersonalResource.query.all()
    log(f"Found {len(personal_resources)} personal resources to sync")
    
    success_count = 0
    failure_count = 0
    
    for resource in personal_resources:
        log(f"Processing resource {resource.id} for student {resource.user_id} in course {resource.course_id}")
        
        # Get resource files
        files = ResourceFile.query.filter_by(resource_id=resource.id).all()
        
        # Extract content from note files
        note_content = []
        for file in files:
            if file.type == "note" and file.content:
                note_content.append(f"## {file.name}\n\n{file.content}")
        
        combined_content = "\n\n---\n\n".join(note_content)
        
        # Format for StudyIndexer
        studyindexer_resource = {
            "resource_info": {
                "resource_id": str(resource.id),
                "title": resource.name,
                "description": resource.description,
                "content": combined_content,
                "type": "collection",
                "course_id": str(resource.course_id),
                "student_id": str(resource.user_id),
                "tags": resource.settings.get("tags", []),
                "metadata": {
                    "resource_type": "collection",
                    "is_private": resource.settings.get("visibility") == "private",
                    "created_at": resource.created_at.isoformat() if resource.created_at else None,
                    "updated_at": resource.updated_at.isoformat() if resource.updated_at else None,
                    "file_count": len(files)
                }
            }
        }
        
        # Attempt to import to StudyIndexer
        try:
            log(f"Sending resource {resource.id} to StudyIndexer")
            response = requests.post(
                f"{api_url}/api/v1/personal-resource/",
                json=studyindexer_resource,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code < 400:
                log(f"Successfully synced resource {resource.id} to StudyIndexer")
                success_count += 1
                
                # Upload files if any files exist
                file_success = 0
                for file in files:
                    if file.type == "file" and file.file_path:
                        # For any file types, upload the actual file
                        file_path = Path(file.file_path.lstrip("/"))
                        
                        # Create dummy file for testing if needed
                        if not os.path.exists(file_path):
                            os.makedirs(os.path.dirname(file_path), exist_ok=True)
                            with open(file_path, "w") as f:
                                f.write(f"Dummy content for {file.name}")
                        
                        try:
                            with open(file_path, "rb") as f:
                                file_response = requests.post(
                                    f"{api_url}/api/v1/personal-resource/{resource.id}/files",
                                    files={
                                        "file": (file.name, f, file.file_type)
                                    },
                                    data={
                                        "student_id": resource.user_id,
                                        "name": file.name,
                                        "file_type": file.type
                                    }
                                )
                                
                                if file_response.status_code < 400:
                                    log(f"Successfully uploaded file {file.name} for resource {resource.id}")
                                    file_success += 1
                                else:
                                    log(f"Failed to upload file {file.name}: {file_response.text}")
                        except Exception as e:
                            log(f"Error uploading file {file.name}: {str(e)}")
                
                log(f"Uploaded {file_success} files for resource {resource.id}")
            else:
                log(f"Failed to sync resource {resource.id}: {response.text}")
                failure_count += 1
                
        except Exception as e:
            log(f"Error syncing resource {resource.id}: {str(e)}")
            failure_count += 1
    
    log(f"Resource sync to StudyIndexer completed. Success: {success_count}, Failed: {failure_count}")
    return {
        'total': len(personal_resources),
        'success': success_count,
        'failed': failure_count
    }

def init_personal_resources_and_sync(studyindexer_url=None):
    """
    Initialize personal resources and optionally sync them to StudyIndexer.
    
    Args:
        studyindexer_url: URL of StudyIndexer API (if None, syncing is skipped)
    """
    app = create_app()
    with app.app_context():
        log("Starting enhanced personal resources initialization...")
        
        # Create enhanced personal resources
        created_resources = create_enhanced_personal_resources()
        
        # Sync to StudyIndexer if URL is provided
        if studyindexer_url:
            sync_results = sync_resources_to_studyindexer(studyindexer_url)
            log(f"Sync results: {sync_results}")
            
        log("Enhanced personal resources initialization and sync completed!")

if __name__ == "__main__":
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Create enhanced personal resources and sync to StudyIndexer")
    parser.add_argument("--sync", action="store_true", help="Sync resources to StudyIndexer")
    parser.add_argument("--api-url", default="http://localhost:8081", help="StudyIndexer API URL")
    args = parser.parse_args()
    
    # Run the initialization
    if args.sync:
        init_personal_resources_and_sync(args.api_url)
    else:
        init_personal_resources_and_sync(None) 