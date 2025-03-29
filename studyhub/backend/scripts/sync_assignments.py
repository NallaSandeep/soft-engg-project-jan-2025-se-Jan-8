#!/usr/bin/env python3
"""
Graded Assignments Sync Script
-----------------------------
This script synchronizes graded assignments from StudyHub to StudyIndexer.
It can be run independently from the database initialization process.

Usage:
    python sync_assignments.py [--limit N] [--course_id ID] [--export PATH]

Options:
    --limit N            Limit the number of assignments to sync (default: all)
    --course_id ID       Sync assignments only for a specific course
    --export PATH        Export assignments to a JSON file instead of syncing
    --batch_size N       Number of assignments to sync in each batch (default: 50)
"""
import os
import sys
import json
import argparse
from datetime import datetime

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

# Import the app and database
try:
    from app import db, create_app
    from app.models import Assignment
    from app.utils.sync_graded_assignments import (
        sync_graded_assignments, 
        export_graded_assignments,
        export_assignments_to_file
    )
    
    app = create_app()
    print("[INFO] Successfully imported StudyHub models and database")
except ImportError as e:
    print(f"[ERROR] Failed to import StudyHub models: {str(e)}")
    sys.exit(1)

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Sync graded assignments from StudyHub to StudyIndexer")
    parser.add_argument("--limit", type=int, help="Limit the number of assignments to sync")
    parser.add_argument("--course_id", type=int, help="Sync assignments only for a specific course")
    parser.add_argument("--export", type=str, help="Export assignments to a JSON file instead of syncing")
    parser.add_argument("--batch_size", type=int, default=50, help="Number of assignments to send in each batch")
    
    return parser.parse_args()

def main():
    """Main function to run the sync process"""
    args = parse_args()
    
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting graded assignments sync...")
    
    # Create application context
    with app.app_context():
        # Count assignments to sync
        query = db.session.query(Assignment).filter_by(type="graded", is_published=True)
        if args.course_id:
            from app.models import Week
            query = query.join(Week).filter(Week.course_id == args.course_id)
            
        assignment_count = query.count()
        print(f"[INFO] Found {assignment_count} graded assignments to sync")
        
        if assignment_count == 0:
            print("[WARNING] No graded assignments found to sync")
            return
        
        # Export to file if requested
        if args.export:
            print(f"[INFO] Exporting assignments to {args.export}...")
            export_assignments_to_file(
                output_file=args.export,
                limit=args.limit,
                course_id=args.course_id
            )
            print(f"[INFO] Export completed to {args.export}")
            return
            
        # Sync with StudyIndexer
        print("[INFO] Starting sync with StudyIndexer...")
        results = sync_graded_assignments(
            limit=args.limit,
            course_id=args.course_id,
            batch_size=args.batch_size
        )
        
        # Print summary
        print("\nSync Summary:")
        print(f"Assignments added: {results.get('added', 0)}")
        print(f"Assignments failed: {results.get('failed', 0)}")
        print(f"Total processed: {results.get('total', 0)}")
        
        if results.get('failed', 0) > 0:
            print("[WARNING] Some assignments failed to sync")
        else:
            print("[INFO] All assignments synced successfully")

if __name__ == "__main__":
    main() 