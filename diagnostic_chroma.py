#!/usr/bin/env python3
"""
Diagnostic script for ChromaDB topic matching issues
This script directly connects to ChromaDB and queries for courses to diagnose why matched_topics are empty
"""

import os
import sys
import json
import time
import logging
from typing import List, Dict, Any, Optional, Union, Tuple
import chromadb

# Set up path to include the studyindexer app
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("diagnostic")

# ChromaDB connection settings
CHROMA_HOST = "localhost"
CHROMA_PORT = 8000

def connect_to_chroma() -> chromadb.Client:
    """Connect to ChromaDB"""
    logger.info(f"Connecting to ChromaDB at {CHROMA_HOST}:{CHROMA_PORT}")
    try:
        # Try to use the project's existing ChromaDB client setup first
        try:
            from app.services.chroma import ChromaService
            logger.info("Using existing ChromaService from the project")
            chroma_service = ChromaService()
            client = chroma_service.client
            if client:
                logger.info("Successfully got ChromaDB client from ChromaService")
                return client
        except Exception as e:
            logger.warning(f"Could not use project's ChromaService: {str(e)}")
            logger.info("Falling back to direct ChromaDB connection")
            
        # Direct connection as fallback
        from chromadb.config import Settings
        client = chromadb.HttpClient(
            host=CHROMA_HOST,
            port=CHROMA_PORT,
            settings=Settings(anonymized_telemetry=False)
        )
        # Check connection
        client.heartbeat()
        logger.info("Successfully connected to ChromaDB directly")
        return client
    except Exception as e:
        logger.error(f"Failed to connect to ChromaDB: {str(e)}")
        raise

def get_collection_names(client: chromadb.Client) -> List[str]:
    """Get all collection names"""
    try:
        collections = client.list_collections()
        collection_names = [c.name for c in collections]
        logger.info(f"Found collections: {collection_names}")
        return collection_names
    except Exception as e:
        logger.error(f"Failed to list collections: {str(e)}")
        return []

def dump_collection_raw_data(client: chromadb.Client, collection_name: str) -> None:
    """Dump complete raw data from a collection for analysis"""
    try:
        collection = client.get_collection(name=collection_name)
        
        # Get all items (limit if there are too many)
        items = collection.get(limit=10, include=["metadatas", "documents"])
        
        logger.info(f"Collection '{collection_name}' has {len(items['ids'])} items")
        logger.info("=============== RAW COLLECTION DATA ===============")
        
        # Print complete raw data in JSON format
        for i, item_id in enumerate(items['ids'][:5]):  # Show first 5 only to avoid cluttering the output
            logger.info(f"Item {i} - ID: {item_id}")
            
            # Get metadata and print as formatted JSON
            metadata = items['metadatas'][i]
            logger.info(f"METADATA (Complete Raw Data):")
            logger.info(json.dumps(metadata, indent=2, sort_keys=True))
            
            # Get document content (if available)
            if 'documents' in items and i < len(items['documents']):
                doc = items['documents'][i]
                # Truncate document if too long
                if len(doc) > 500:
                    logger.info(f"DOCUMENT (truncated): {doc[:500]}...")
                else:
                    logger.info(f"DOCUMENT: {doc}")
            
            logger.info("---------------------------------------------")
        
        # Print schema statistics - what fields exist and with what frequency
        field_stats = {}
        for metadata in items['metadatas']:
            for key in metadata.keys():
                if key not in field_stats:
                    field_stats[key] = 1
                else:
                    field_stats[key] += 1
                    
                # Check for empty fields or null values
                if metadata[key] == "" or metadata[key] is None:
                    if key + "_empty" not in field_stats:
                        field_stats[key + "_empty"] = 1
                    else:
                        field_stats[key + "_empty"] += 1
                        
        logger.info(f"FIELD STATISTICS (out of {len(items['ids'])} items):")
        for field, count in sorted(field_stats.items()):
            logger.info(f"  {field}: {count} items")
            
    except Exception as e:
        logger.error(f"Failed to dump collection data '{collection_name}': {str(e)}")

def examine_specific_courses(client: chromadb.Client, collection_name: str, course_codes: List[str]) -> None:
    """Examine specific courses by their course codes"""
    try:
        collection = client.get_collection(name=collection_name)
        
        logger.info(f"Looking up specific courses: {course_codes}")
        
        # Try to find courses by their codes
        for code in course_codes:
            logger.info(f"Searching for course with code: {code}")
            
            # First try to get by exact ID
            try:
                result = collection.get(ids=[code], include=["metadatas", "documents"])
                if result and result['ids']:
                    logger.info(f"Found course with ID {code}")
                    metadata = result['metadatas'][0]
                    logger.info(f"METADATA:")
                    logger.info(json.dumps(metadata, indent=2, sort_keys=True))
                    continue
            except Exception:
                logger.info(f"Course not found with ID {code}, trying to search...")
            
            # Try to search by code in metadata
            try:
                # Get all items and filter
                all_items = collection.get(include=["metadatas"])
                found = False
                
                for i, metadata in enumerate(all_items['metadatas']):
                    if metadata.get('code') == code:
                        logger.info(f"Found course with code {code} (ID: {all_items['ids'][i]})")
                        logger.info(f"METADATA:")
                        logger.info(json.dumps(metadata, indent=2, sort_keys=True))
                        found = True
                        break
                
                if not found:
                    logger.warning(f"Course with code {code} not found in collection")
            except Exception as e:
                logger.error(f"Error searching for course {code}: {str(e)}")
        
    except Exception as e:
        logger.error(f"Failed to examine specific courses: {str(e)}")

def main():
    logger.info("Starting ChromaDB diagnostic tool")
    
    try:
        # Connect to ChromaDB
        client = connect_to_chroma()
        
        # List all collections
        collection_names = get_collection_names(client)
        
        # Find course selector collection
        course_collection_name = None
        for name in collection_names:
            if "course" in name.lower() or "selector" in name.lower():
                course_collection_name = name
                break
        
        if not course_collection_name:
            if collection_names:
                course_collection_name = collection_names[0]
                logger.info(f"No course collection found, using first available: {course_collection_name}")
            else:
                logger.error("No collections found in ChromaDB")
                return
        
        # Dump raw collection data
        logger.info(f"Dumping raw data from collection: {course_collection_name}")
        dump_collection_raw_data(client, course_collection_name)
        
        # Examine specific courses
        examine_specific_courses(client, course_collection_name, ["BA201", "SE101"])
        
        logger.info("Diagnostic complete")
        
    except Exception as e:
        logger.error(f"Diagnostic failed: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    main() 