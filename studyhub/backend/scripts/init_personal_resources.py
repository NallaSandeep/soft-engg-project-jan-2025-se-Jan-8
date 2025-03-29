#!/usr/bin/env python3
"""
Initialize personal resources in StudyHub and sync them to StudyIndexer.
This script can be run independently of the main initialization process.
"""
import os
import sys
import logging
import argparse
from datetime import datetime

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the enhanced_personal_resources module
from scripts.enhanced_personal_resources import (
    init_personal_resources_and_sync,
    create_enhanced_personal_resources,
    sync_resources_to_studyindexer
)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Initialize personal resources and sync with StudyIndexer")
    parser.add_argument("--no-sync", action="store_true", help="Skip syncing to StudyIndexer")
    parser.add_argument("--sync-only", action="store_true", help="Only sync existing resources (don't create new ones)")
    parser.add_argument("--api-url", default="http://localhost:8081", help="StudyIndexer API URL")
    args = parser.parse_args()
    
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Personal resources initialization started")
    
    if args.sync_only:
        # Only sync existing resources
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Syncing existing resources to StudyIndexer")
        
        from app import create_app
        app = create_app()
        with app.app_context():
            results = sync_resources_to_studyindexer(args.api_url)
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Sync completed: {results}")
    else:
        # Create new resources and optionally sync
        api_url = None if args.no_sync else args.api_url
        init_personal_resources_and_sync(api_url)
    
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Personal resources initialization completed") 