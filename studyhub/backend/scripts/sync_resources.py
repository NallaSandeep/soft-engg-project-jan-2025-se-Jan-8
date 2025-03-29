#!/usr/bin/env python3
"""
Personal Resources Sync Script
-----------------------------
This script synchronizes personal resources from StudyHub to StudyIndexer.
It can be run independently from the database initialization process.

Usage:
    python sync_resources.py [--limit N] [--student_id ID] [--course_id ID] [--export PATH]

Options:
    --limit N            Limit the number of resources to sync (default: all)
    --student_id ID      Sync resources only for a specific student
    --course_id ID       Sync resources only for a specific course
    --export PATH        Export resources to a JSON file instead of syncing
    --batch_size N       Number of resources to sync in each batch (default: 50)
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
    from app.models import PersonalResource
    from app.utils.sync_personal_resources import (
        sync_personal_resources, 
        export_personal_resources,
        export_resources_to_file
    )
    
    app = create_app()
    print("[INFO] Successfully imported StudyHub models and database")
except ImportError as e:
    print(f"[ERROR] Failed to import StudyHub models: {str(e)}")
    sys.exit(1)

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Sync personal resources from StudyHub to StudyIndexer")
    parser.add_argument("--limit", type=int, help="Limit the number of resources to sync")
    parser.add_argument("--student_id", type=int, help="Sync resources only for a specific student")
    parser.add_argument("--course_id", type=int, help="Sync resources only for a specific course")
    parser.add_argument("--export", type=str, help="Export resources to a JSON file instead of syncing")
    parser.add_argument("--batch_size", type=int, default=50, help="Number of resources to send in each batch")
    
    return parser.parse_args()

def main():
    """Main function to run the sync process"""
    args = parse_args()
    
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting personal resources sync...")
    
    # Create application context
    with app.app_context():
        # Count resources to sync
        query = db.session.query(PersonalResource)
        if args.student_id:
            query = query.filter(PersonalResource.user_id == args.student_id)
        if args.course_id:
            query = query.filter(PersonalResource.course_id == args.course_id)
            
        resource_count = query.count()
        print(f"[INFO] Found {resource_count} personal resources to sync")
        
        if resource_count == 0:
            print("[WARNING] No personal resources found to sync")
            return
        
        # Export to file if requested
        if args.export:
            print(f"[INFO] Exporting resources to {args.export}...")
            export_resources_to_file(
                output_file=args.export,
                limit=args.limit
            )
            print(f"[INFO] Export completed to {args.export}")
            return
            
        # Sync with StudyIndexer
        print("[INFO] Starting sync with StudyIndexer...")
        results = sync_personal_resources(
            limit=args.limit,
            student_id=args.student_id,
            course_id=args.course_id,
            batch_size=args.batch_size
        )
        
        # Print summary
        print("\nSync Summary:")
        print(f"Resources added: {results.get('added', 0)}")
        print(f"Resources failed: {results.get('failed', 0)}")
        print(f"Total processed: {results.get('total', 0)}")
        
        if results.get('failed', 0) > 0:
            print("[WARNING] Some resources failed to sync")
        else:
            print("[INFO] All resources synced successfully")

if __name__ == "__main__":
    main() 