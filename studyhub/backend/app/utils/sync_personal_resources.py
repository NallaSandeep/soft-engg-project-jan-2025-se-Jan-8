"""
Personal Resources Sync Utility
-------------------------------
This module provides functions to sync personal resources from StudyHub to StudyIndexer.
It exports resources from the database and sends them to the StudyIndexer API.

Core Functions:
- export_personal_resources: Export resources from the database
- sync_to_studyindexer: Send resources to StudyIndexer API
- sync_personal_resources: Main entry point function

Usage:
    from app.utils.sync_personal_resources import sync_personal_resources
    
    # In init_db.py
    sync_personal_resources()
"""
import os
import json
import requests
import logging
from typing import List, Dict, Any, Optional

from app.models.personal_resource import PersonalResource, ResourceFile
from app.models.course import Course
from app import db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("sync_resources")

# Configuration
STUDYINDEXER_API_URL = os.environ.get("STUDYINDEXER_API_URL", "http://127.0.0.1:8081")
PERSONAL_RESOURCE_ENDPOINT = f"{STUDYINDEXER_API_URL}/api/v1/personal-resource/sync"

def export_personal_resources(limit: Optional[int] = None, 
                             student_id: Optional[int] = None,
                             course_id: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Export personal resources from the database
    
    Args:
        limit: Optional limit of resources to export
        student_id: Optional filter by student ID
        course_id: Optional filter by course ID
        
    Returns:
        List of resources in a format suitable for StudyIndexer
    """
    # Build query
    query = PersonalResource.query

    # Apply filters
    if student_id:
        query = query.filter(PersonalResource.user_id == student_id)
    if course_id:
        query = query.filter(PersonalResource.course_id == course_id)

    # Apply limit if specified
    if limit and limit > 0:
        query = query.limit(limit)

    # Execute query
    resources = query.all()
    
    logger.info(f"Exporting {len(resources)} personal resources")
    
    # Transform to StudyIndexer format
    transformed_resources = []
    for resource in resources:
        try:
            # Export resource
            resource_dict = {
                "resource": {
                    "id": resource.id,
                    "user_id": resource.user_id,
                    "course_id": resource.course_id,
                    "name": resource.name,
                    "description": resource.description,
                    "is_active": resource.is_active,
                    "created_at": resource.created_at.isoformat() if resource.created_at else None,
                    "updated_at": resource.updated_at.isoformat() if resource.updated_at else None,
                    "settings": resource.settings if resource.settings else {}
                },
                "files": []
            }
            
            # Export files
            for file in resource.files:
                file_dict = {
                    "id": file.id,
                    "resource_id": file.resource_id,
                    "name": file.name,
                    "type": file.type,
                    "content": file.content if file.type in ["text", "url"] else None,
                    "file_path": file.file_path if file.type == "file" else None,
                    "file_type": file.file_type,
                    "file_size": file.file_size,
                    "created_at": file.created_at.isoformat() if file.created_at else None,
                    "updated_at": file.updated_at.isoformat() if file.updated_at else None
                }
                resource_dict["files"].append(file_dict)
                
            # Add course info if available
            if resource.course:
                resource_dict["course_info"] = {
                    "id": resource.course.id,
                    "code": resource.course.code,
                    "name": resource.course.name
                }
                
            transformed_resources.append(resource_dict)
        except Exception as e:
            logger.error(f"Error exporting resource {resource.id}: {str(e)}")
    
    return transformed_resources

def sync_to_studyindexer(resources: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Send resources to StudyIndexer API
    
    Args:
        resources: List of resources to sync
        
    Returns:
        Response from StudyIndexer API
    """
    if not resources:
        logger.info("No resources to sync")
        return {"added": 0, "failed": 0}
    
    # Prepare payload
    payload = {
        "resources": resources
    }
    
    # Send to StudyIndexer
    try:
        logger.info(f"Sending {len(resources)} resources to StudyIndexer at {PERSONAL_RESOURCE_ENDPOINT}")
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
            return {"added": 0, "failed": len(resources)}
    except Exception as e:
        logger.error(f"Error sending resources to StudyIndexer: {str(e)}")
        return {"added": 0, "failed": len(resources)}

def sync_personal_resources(limit: Optional[int] = None,
                            student_id: Optional[int] = None,
                            course_id: Optional[int] = None,
                            batch_size: int = 50) -> Dict[str, Any]:
    """
    Main function to sync personal resources from StudyHub to StudyIndexer
    
    Args:
        limit: Optional limit of resources to export
        student_id: Optional filter by student ID
        course_id: Optional filter by course ID
        batch_size: Number of resources to send in each batch
        
    Returns:
        Summary of sync operation
    """
    logger.info("Starting personal resources sync")
    
    # Export resources
    resources = export_personal_resources(limit, student_id, course_id)
    if not resources:
        logger.info("No resources to sync")
        return {"added": 0, "failed": 0, "total": 0}
    
    # Process in batches
    logger.info(f"Syncing {len(resources)} resources in batches of {batch_size}")
    batches = [resources[i:i+batch_size] for i in range(0, len(resources), batch_size)]
    
    results = {
        "added": 0,
        "failed": 0,
        "total": len(resources)
    }
    
    # Process batches with standard reporting
    for i, batch in enumerate(batches):
        logger.info(f"Processing batch {i+1}/{len(batches)}")
        batch_result = sync_to_studyindexer(batch)
        results["added"] += batch_result.get("added", 0)
        results["failed"] += batch_result.get("failed", 0)
    
    # Log summary
    logger.info(f"Sync summary: {results['added']} added, {results['failed']} failed, {results['total']} total")
    return results

# Export utility function for direct use in scripts
def export_resources_to_file(output_file: str, limit: Optional[int] = None):
    """
    Export personal resources to a JSON file
    
    Args:
        output_file: Path to output file
        limit: Optional limit of resources to export
    """
    resources = export_personal_resources(limit)
    
    with open(output_file, 'w') as f:
        json.dump(resources, f, indent=2)
    
    logger.info(f"Exported {len(resources)} resources to {output_file}") 