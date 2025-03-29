#!/usr/bin/env python3
"""
Test script for the PersonalResource implementation in StudyIndexer

This script tests the PersonalResource functionality by:
1. Creating sample personal resources
2. Indexing them in the vector database
3. Testing search functionality with various queries

Usage:
    python test_personal_resource.py
"""
import asyncio
import json
import os
import time
import random
from typing import List, Dict, Any

from app.models.personal_resource import (
    PersonalResourceInfo,
    ResourceFile,
    PersonalResource,
    PersonalResourceSearchQuery
)
from app.services.personal_resource import PersonalResourceService

# Sample data for testing
STUDENT_IDS = [1001, 1002, 1003]
COURSE_IDS = [101, 102, 103]
RESOURCE_TYPES = ["text", "url", "file"]

# Sample content fragments for generating resources
RESOURCE_NAMES = [
    "Linear Algebra Notes",
    "Database Design Principles",
    "Machine Learning Algorithms",
    "Neural Network Basics",
    "Software Engineering Patterns",
    "Data Structures Overview",
    "Algorithms Complexity Analysis",
    "Calculus Problem Solutions",
    "Physics Experiment Notes",
    "Chemistry Reaction Tables"
]

CONTENT_FRAGMENTS = [
    "Linear algebra is the branch of mathematics concerning linear equations.",
    "A matrix is a rectangular array of numbers, symbols, or expressions, arranged in rows and columns.",
    "The singular value decomposition (SVD) is a factorization of a real or complex matrix.",
    "Eigenvalues and eigenvectors are important for solving systems of differential equations.",
    "Database normalization is the process of structuring a relational database.",
    "SQL is a domain-specific language used in programming for managing data in relational databases.",
    "Machine learning algorithms build a model based on sample data to make predictions.",
    "Neural networks are computing systems inspired by the biological neural networks.",
    "Software design patterns are typical solutions to common problems in software design.",
    "Data structures are a specialized format for organizing, processing, retrieving and storing data."
]

def generate_sample_resources(count: int = 5) -> List[Dict[str, Any]]:
    """Generate sample resources for testing"""
    resources = []
    
    for i in range(count):
        # Create a resource
        student_id = random.choice(STUDENT_IDS)
        course_id = random.choice(COURSE_IDS)
        
        resource_id = int(time.time() * 1000) + i  # Unique ID based on timestamp
        
        resource_info = {
            "id": resource_id,
            "user_id": student_id,
            "course_id": course_id,
            "name": random.choice(RESOURCE_NAMES),
            "description": f"Sample resource {i+1} for testing",
            "is_active": True,
            "created_at": "2023-01-01T00:00:00",
            "updated_at": "2023-01-01T00:00:00",
            "settings": {"tags": ["test", "sample"]}
        }
        
        # Create 1-3 files for this resource
        files = []
        for j in range(random.randint(1, 3)):
            file_type = random.choice(RESOURCE_TYPES)
            file_id = resource_id * 100 + j  # Unique file ID
            
            file = {
                "id": file_id,
                "resource_id": resource_id,
                "name": f"File {j+1} for resource {resource_id}",
                "type": file_type,
                "content": None,
                "file_path": None,
                "file_type": None,
                "file_size": None,
                "created_at": "2023-01-01T00:00:00",
                "updated_at": "2023-01-01T00:00:00"
            }
            
            # Add content based on file type
            if file_type == "text":
                # Create sample content from fragments
                content_parts = random.sample(CONTENT_FRAGMENTS, 3)
                file["content"] = " ".join(content_parts)
                file["file_type"] = "text/plain"
                file["file_size"] = len(file["content"])
            elif file_type == "url":
                file["content"] = f"https://example.com/resource{resource_id}/file{j}"
                file["file_type"] = "url"
                file["file_size"] = len(file["content"])
            else:  # file type
                file["file_path"] = f"/path/to/file{file_id}.pdf"
                file["file_type"] = "application/pdf"
                file["file_size"] = random.randint(1000, 10000000)
                # Add some content for the file (normally this would be extracted)
                file["content"] = random.choice(CONTENT_FRAGMENTS)
            
            files.append(file)
        
        # Combine into resource
        resource = {
            "resource": resource_info,
            "files": files
        }
        
        resources.append(resource)
    
    return resources

async def main():
    """Main test function"""
    print("Starting PersonalResource test...")
    
    # Initialize service
    service = PersonalResourceService()
    await service.initialize()
    
    # Generate sample resources
    print("\nGenerating sample resources...")
    resources = generate_sample_resources(10)
    print(f"Generated {len(resources)} sample resources")
    
    # Index the resources
    print("\nIndexing resources...")
    indexed_ids = []
    for i, resource in enumerate(resources):
        try:
            resource_id = await service.add_resource(resource)
            indexed_ids.append(resource_id)
            print(f"Indexed resource {i+1}/{len(resources)}: ID {resource_id}")
        except Exception as e:
            print(f"Error indexing resource {i+1}: {str(e)}")
    
    print(f"Successfully indexed {len(indexed_ids)} resources")
    
    # Test search functionality
    print("\nTesting search functionality...")
    
    # Define test queries
    test_queries = [
        "linear algebra",
        "matrix",
        "database",
        "machine learning",
        "software engineering"
    ]
    
    for query in test_queries:
        print(f"\nSearching for: '{query}'")
        
        # Create search query
        search_query = PersonalResourceSearchQuery(
            query=query,
            student_id=STUDENT_IDS[0],  # Use first student ID
            limit=5,
            min_score=0.3
        )
        
        # Execute search
        try:
            total, results, query_time = await service.search_resources(search_query)
            
            print(f"Found {total} results in {query_time:.2f}ms:")
            for i, result in enumerate(results):
                print(f"  {i+1}. {result.title} (Score: {result.score:.2f})")
                print(f"     Content: {result.content[:100]}...")
        except Exception as e:
            print(f"Error searching: {str(e)}")
    
    # Test getting a specific resource
    if indexed_ids:
        print("\nTesting get_resource...")
        try:
            resource_id = indexed_ids[0]
            resource = await service.get_resource(resource_id)
            print(f"Retrieved resource {resource_id}:")
            print(f"  Name: {resource['resource']['name']}")
            print(f"  Files: {len(resource['files'])}")
        except Exception as e:
            print(f"Error getting resource: {str(e)}")
    
    # Test listing resources
    print("\nTesting list_resources...")
    try:
        resources = await service.list_resources(STUDENT_IDS[0], limit=5)
        print(f"Listed {len(resources)} resources for student {STUDENT_IDS[0]}")
        for i, resource in enumerate(resources):
            print(f"  {i+1}. {resource['name']} (ID: {resource['id']})")
    except Exception as e:
        print(f"Error listing resources: {str(e)}")
    
    print("\nPersonalResource test completed!")
    
if __name__ == "__main__":
    asyncio.run(main()) 