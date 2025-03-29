#!/usr/bin/env python3
"""
Sync Personal Resources Script
------------------------------
This script synchronizes personal resources from StudyHub to StudyIndexer.
It is designed to be called from the StudyHub init_db.py script or
as a standalone utility for synchronizing resources.

Usage:
    python sync_personal_resources.py [--limit N] [--student_id STUDENT_ID]

Options:
    --limit N            Limit the number of resources to sync (default: all)
    --student_id ID      Sync resources only for a specific student

Dependencies:
    - requests: For API calls to StudyIndexer
    - tqdm: For progress bars (optional)
"""
import os
import sys
import json
import argparse
import time
import requests
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging

# Try to import tqdm for progress bars, but continue if not available
try:
    from tqdm import tqdm
    has_tqdm = True
except ImportError:
    has_tqdm = False
    print("Install tqdm for progress bars: pip install tqdm")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/sync_resources.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("sync_resources")

# Configuration
STUDYINDEXER_API_URL = os.environ.get("STUDYINDEXER_API_URL", "http://localhost:8000")
PERSONAL_RESOURCE_ENDPOINT = f"{STUDYINDEXER_API_URL}/api/v1/personal-resource/sync"

def transform_resource(resource: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform a StudyHub personal resource to StudyIndexer format
    
    Args:
        resource: StudyHub personal resource dictionary
        
    Returns:
        Transformed resource in StudyIndexer format
    """
    # Extract core resource info
    resource_info = {
        "id": resource["id"],
        "user_id": resource["user_id"],
        "course_id": resource["course_id"],
        "name": resource["name"],
        "description": resource["description"],
        "is_active": resource["is_active"],
        "created_at": resource["created_at"],
        "updated_at": resource["updated_at"],
        "settings": resource["settings"]
    }
    
    # Transform files
    transformed_files = []
    for file in resource.get("files", []):
        transformed_file = {
            "id": file["id"],
            "resource_id": file["resource_id"],
            "name": file["name"],
            "type": file["type"],
            "content": file["content"] if file["type"] in ["text", "url"] else None,
            "file_path": file["file_path"] if file["type"] == "file" else None,
            "file_type": file["file_type"],
            "file_size": file["file_size"],
            "created_at": file["created_at"],
            "updated_at": file["updated_at"]
        }
        transformed_files.append(transformed_file)
    
    # Construct final resource object
    transformed_resource = {
        "resource": resource_info,
        "files": transformed_files,
        "course_info": resource.get("course", {})
    }
    
    return transformed_resource

def sync_resources(resources: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Sync resources to StudyIndexer
    
    Args:
        resources: List of StudyHub resources
        
    Returns:
        Result dictionary with success/failure counts
    """
    if not resources:
        logger.info("No resources to sync")
        return {"added": 0, "failed": 0, "skipped": 0}
    
    # Transform resources to StudyIndexer format
    transformed_resources = []
    for resource in resources:
        try:
            transformed = transform_resource(resource)
            transformed_resources.append(transformed)
        except Exception as e:
            logger.error(f"Error transforming resource {resource.get('id')}: {str(e)}")
            continue
    
    # Prepare payload
    payload = {
        "resources": transformed_resources
    }
    
    # Send to StudyIndexer
    try:
        response = requests.post(
            PERSONAL_RESOURCE_ENDPOINT,
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"Successfully synced {result.get('data', {}).get('added', 0)} resources")
            return result.get("data", {})
        else:
            logger.error(f"Error syncing resources: {response.status_code} - {response.text}")
            return {"added": 0, "failed": len(transformed_resources), "skipped": 0}
    except Exception as e:
        logger.error(f"Error sending resources to StudyIndexer: {str(e)}")
        return {"added": 0, "failed": len(transformed_resources), "skipped": 0}

def main():
    """Main function to run the script"""
    parser = argparse.ArgumentParser(description="Sync personal resources from StudyHub to StudyIndexer")
    parser.add_argument("--limit", type=int, help="Limit the number of resources to sync")
    parser.add_argument("--student_id", type=int, help="Sync resources only for a specific student")
    parser.add_argument("--input", type=str, help="Input JSON file with resources to sync")
    args = parser.parse_args()
    
    # Check if we have an input file
    if args.input:
        try:
            with open(args.input, 'r') as f:
                resources = json.load(f)
            logger.info(f"Loaded {len(resources)} resources from {args.input}")
        except Exception as e:
            logger.error(f"Error loading resources from {args.input}: {str(e)}")
            return
    else:
        logger.error("No input file specified. Use --input to specify a JSON file with resources.")
        return
    
    # Apply limit if specified
    if args.limit and args.limit > 0:
        resources = resources[:args.limit]
        logger.info(f"Limited to {len(resources)} resources")
    
    # Filter by student_id if specified
    if args.student_id:
        resources = [r for r in resources if r.get("user_id") == args.student_id]
        logger.info(f"Filtered to {len(resources)} resources for student {args.student_id}")
    
    # Add progress bar if tqdm is available
    if has_tqdm:
        logger.info("Starting sync with progress bar...")
        result = sync_resources(resources)
    else:
        logger.info("Starting sync...")
        result = sync_resources(resources)
    
    # Print summary
    print("\nSync Summary:")
    print(f"Resources added: {result.get('added', 0)}")
    print(f"Resources failed: {result.get('failed', 0)}")
    print(f"Resources skipped: {result.get('skipped', 0)}")
    print(f"Total processed: {len(resources)}")

if __name__ == "__main__":
    main() 