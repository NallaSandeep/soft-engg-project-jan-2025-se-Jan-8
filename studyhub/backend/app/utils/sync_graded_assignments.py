"""
Sync Graded Assignments to StudyIndexer
---------------------------------------
This utility module synchronizes graded assignments from StudyHub to StudyIndexer's
integrity check service to enable academic integrity checks for student submissions.

It extracts graded assignments, their questions, and necessary metadata from StudyHub 
and formats them for the IntegrityCheck API in StudyIndexer.
"""

import os
import json
import logging
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime

from flask import current_app
from .. import db
from ..models import Assignment, AssignmentQuestion, Question, Course, Week, User

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
STUDYINDEXER_BASE_URL = os.environ.get('STUDYINDEXER_BASE_URL', 'http://localhost:8081')
INTEGRITY_CHECK_API = f"{STUDYINDEXER_BASE_URL}/api/v1/integrity-check"

def log(message: str) -> None:
    """Log a message with a timestamp"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    logger.info(f"[{timestamp}] {message}")
    print(f"[{timestamp}] {message}")

def export_graded_assignments(
    limit: Optional[int] = None,
    course_id: Optional[int] = None,
    batch_size: int = 50
) -> List[Dict[str, Any]]:
    """
    Export graded assignments from StudyHub database
    
    Args:
        limit: Optional limit on number of assignments to export
        course_id: Optional filter by course ID
        batch_size: Size of each batch of assignments to process
        
    Returns:
        List of assignment data formatted for StudyIndexer
    """
    log(f"Exporting graded assignments (limit={limit}, course_id={course_id}, batch_size={batch_size})")
    
    # Start with base query for graded assignments
    query = db.session.query(Assignment).filter_by(type="graded", is_published=True)
    
    # Apply filters
    if course_id:
        query = query.join(Week).filter(Week.course_id == course_id)
    
    # Apply limit
    if limit:
        query = query.limit(limit)
    
    # Execute query
    assignments = query.all()
    log(f"Found {len(assignments)} graded assignments to export")
    
    # Format assignments for StudyIndexer
    formatted_assignments = []
    
    for assignment in assignments:
        try:
            # Get week and course information
            week = db.session.query(Week).filter_by(id=assignment.week_id).first()
            if not week:
                log(f"Week not found for assignment {assignment.id}, skipping")
                continue
                
            course = db.session.query(Course).filter_by(id=week.course_id).first()
            if not course:
                log(f"Course not found for assignment {assignment.id}, skipping")
                continue
                
            # Get assignment questions
            assignment_questions = db.session.query(AssignmentQuestion).filter_by(
                assignment_id=assignment.id
            ).order_by(AssignmentQuestion.order).all()
            
            if not assignment_questions:
                log(f"No questions found for assignment {assignment.id}, skipping")
                continue
                
            # Format questions
            formatted_questions = []
            for aq in assignment_questions:
                # Get question details
                question = db.session.query(Question).filter_by(id=aq.question_id).first()
                if not question:
                    log(f"Question {aq.question_id} not found, skipping")
                    continue
                    
                # Format options for display
                options = []
                if question.question_options and question.type in ["MCQ", "MSQ", "mcq", "msq"]:
                    for i, option in enumerate(question.question_options):
                        # Format depends on whether option is a dict or string
                        if isinstance(option, dict) and "text" in option:
                            options.append(option["text"])
                        elif isinstance(option, str):
                            options.append(option)
                
                # Format the question
                formatted_question = {
                    "question_id": str(question.id),
                    "title": question.title,
                    "content": question.content,
                    "type": question.type.lower(),
                    "options": options,
                    "points": question.points
                }
                
                formatted_questions.append(formatted_question)
            
            # Format the assignment
            formatted_assignment = {
                "assignment_id": str(assignment.id),
                "course_id": str(course.id),
                "course_code": course.code,
                "course_title": course.name,
                "title": assignment.title,
                "description": assignment.description,
                "week_id": str(week.id),
                "week_number": week.number,
                "week_title": week.title,
                "due_date": assignment.due_date.isoformat() if assignment.due_date else None,
                "questions": formatted_questions
            }
            
            formatted_assignments.append(formatted_assignment)
            log(f"Exported assignment {assignment.id}: {assignment.title} with {len(formatted_questions)} questions")
            
        except Exception as e:
            log(f"Error exporting assignment {assignment.id}: {str(e)}")
    
    log(f"Exported {len(formatted_assignments)} assignments with questions")
    return formatted_assignments

def send_assignments_to_studyindexer(
    assignments: List[Dict[str, Any]],
    batch_size: int = 50
) -> Dict[str, int]:
    """
    Send formatted assignments to StudyIndexer for indexing
    
    Args:
        assignments: List of formatted assignment data
        batch_size: Size of each batch to send
        
    Returns:
        Summary of results (added, failed, total)
    """
    log(f"Sending {len(assignments)} assignments to StudyIndexer in batches of {batch_size}")
    
    results = {
        "added": 0,
        "failed": 0,
        "total": len(assignments)
    }
    
    # Process in batches
    for i in range(0, len(assignments), batch_size):
        batch = assignments[i:i+batch_size]
        log(f"Processing batch {i//batch_size + 1} with {len(batch)} assignments")
        
        # First try bulk endpoint if available
        bulk_success = False
        try:
            bulk_response = requests.post(
                f"{INTEGRITY_CHECK_API}/bulk-index",
                json=batch,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if bulk_response.status_code < 400:
                response_data = bulk_response.json()
                added = response_data.get("data", {}).get("total_indexed", 0)
                failed = len(batch) - added
                
                results["added"] += added
                results["failed"] += failed
                
                log(f"Bulk index completed: {added} added, {failed} failed")
                bulk_success = True
            else:
                log(f"Bulk index failed with status {bulk_response.status_code}: {bulk_response.text}")
        except Exception as e:
            log(f"Error during bulk index: {str(e)}")
        
        # If bulk failed, try individual assignments
        if not bulk_success:
            for assignment in batch:
                try:
                    response = requests.post(
                        f"{INTEGRITY_CHECK_API}/index",
                        json=assignment,
                        headers={"Content-Type": "application/json"},
                        timeout=10
                    )
                    
                    if response.status_code < 400:
                        results["added"] += 1
                        log(f"Successfully indexed assignment {assignment['assignment_id']}")
                    else:
                        results["failed"] += 1
                        log(f"Failed to index assignment {assignment['assignment_id']}: {response.text}")
                except Exception as e:
                    results["failed"] += 1
                    log(f"Error indexing assignment {assignment['assignment_id']}: {str(e)}")
    
    log(f"Assignment indexing completed: {results['added']} added, {results['failed']} failed")
    return results

def export_assignments_to_file(
    output_file: str,
    limit: Optional[int] = None,
    course_id: Optional[int] = None
) -> None:
    """
    Export graded assignments to a JSON file
    
    Args:
        output_file: Path to output file
        limit: Optional limit on number of assignments to export
        course_id: Optional filter by course ID
    """
    log(f"Exporting graded assignments to file: {output_file}")
    
    # Export assignments
    assignments = export_graded_assignments(limit=limit, course_id=course_id)
    
    # Write to file
    try:
        with open(output_file, 'w') as f:
            json.dump(assignments, f, indent=2)
        log(f"Successfully exported {len(assignments)} assignments to {output_file}")
    except Exception as e:
        log(f"Error writing to file {output_file}: {str(e)}")

def sync_graded_assignments(
    limit: Optional[int] = None,
    course_id: Optional[int] = None,
    batch_size: int = 50
) -> Dict[str, int]:
    """
    Sync graded assignments from StudyHub to StudyIndexer
    
    Args:
        limit: Optional limit on number of assignments to sync
        course_id: Optional filter by course ID
        batch_size: Size of each batch to send
        
    Returns:
        Summary of results (added, failed, total)
    """
    log(f"Starting graded assignments sync with StudyIndexer")
    
    # Export assignments
    assignments = export_graded_assignments(
        limit=limit,
        course_id=course_id,
        batch_size=batch_size
    )
    
    if not assignments:
        log("No assignments to sync")
        return {"added": 0, "failed": 0, "total": 0}
    
    # Send to StudyIndexer
    results = send_assignments_to_studyindexer(
        assignments=assignments,
        batch_size=batch_size
    )
    
    return results

if __name__ == "__main__":
    # For testing as standalone script
    from flask import Flask
    app = Flask(__name__)
    app.config.from_object('config.Config')
    
    with app.app_context():
        results = sync_graded_assignments()
        print(f"Sync results: {results}") 