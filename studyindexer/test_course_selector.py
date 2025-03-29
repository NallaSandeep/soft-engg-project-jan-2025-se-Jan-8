"""
Simple test script for the CourseSelector functionality
"""
import asyncio
import json
import sys
import glob
import os
from pathlib import Path

from app.services.course_selector import CourseSelectorService
from app.models.course_selector import CourseSelectorQuery

async def main():
    """Run test for CourseSelector"""
    print("Testing CourseSelector functionality...")
    
    # Initialize the service
    course_selector = CourseSelectorService()
    await course_selector.initialize()
    
    # Index sample courses
    sample_dir = os.path.join(os.getcwd(), "samples")
    course_files = glob.glob(os.path.join(sample_dir, "*.json"))
    
    if not course_files:
        print("No sample course files found! Please check the samples directory.")
        return
    
    print(f"Found {len(course_files)} sample course files")
    
    # Index courses
    result = await course_selector.bulk_index_courses_from_files(course_files)
    print(f"Indexed {result['total_indexed']} courses successfully")
    
    if result['failed_items']:
        print("Failed to index these items:")
        for item in result['failed_items']:
            print(f"  - {item['file']}: {item['error']}")
    
    # Test a search query
    course_ids = [int(cid) for cid in result['course_ids']]
    
    # Test queries
    test_queries = [
        "web development with JavaScript and Vue.js",
        "data structures and algorithms",
        "software engineering principles",
        "database management systems",
        "user interface design"
    ]
    
    for query in test_queries:
        print(f"\nSearching for: '{query}'")
        search_query = CourseSelectorQuery(
            query=query,
            subscribed_courses=course_ids,
            min_score=0.3,
            limit=3
        )
        
        total_results, results, query_time_ms = await course_selector.select_courses(search_query)
        
        print(f"Found {total_results} results in {query_time_ms:.2f}ms")
        
        for i, result in enumerate(results):
            print(f"{i+1}. {result.code}: {result.title} (Score: {result.score:.2f})")
            print(f"   Matched topics: {', '.join(result.matched_topics)}")
            print(f"   Relevant weeks: {result.weeks}")
    
    print("\nTest completed successfully!")

if __name__ == "__main__":
    asyncio.run(main()) 