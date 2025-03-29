"""
Test script for CourseContent functionality
This script tests the CourseContent service by adding sample courses and searching for them.
"""
import asyncio
import json
import os
import time
import glob
from app.services.course_content import CourseContentService
from app.models.course_selector import CourseContent, CourseInfo, CourseTopic

async def main():
    print("Testing CourseContent functionality...")
    
    # Initialize the CourseContent service
    service = CourseContentService()
    await service.initialize()
    
    # Find and import sample courses
    sample_dir = os.path.join(os.getcwd(), "samples")
    sample_files = glob.glob(os.path.join(sample_dir, "sample_course*.json"))
    
    if not sample_files:
        print("No sample course files found in samples directory")
        return
    
    print(f"Found {len(sample_files)} sample course files")
    
    # Import each sample course
    course_ids = []
    for file_path in sample_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                course_data = json.load(f)
            
            print(f"Importing {os.path.basename(file_path)}...")
            course_id = await service.add_course_content(course_data)
            course_ids.append(course_id)
            print(f"Successfully imported course: {course_id}")
        except Exception as e:
            print(f"Error importing {os.path.basename(file_path)}: {str(e)}")
    
    print(f"\nImported {len(course_ids)} courses successfully")
    
    # List all courses
    print("\nListing all courses:")
    courses = await service.list_courses()
    for course in courses:
        print(f"- {course['title']} ({course['code']})")
    
    # Test search with various queries
    search_queries = [
        "database",
        "python programming",
        "data structures",
        "algorithms",
        "SQL"
    ]
    
    for query in search_queries:
        print(f"\nSearching for '{query}':")
        search_results = await service.search_courses(query)
        if not search_results:
            print(f"No results found for '{query}'")
        else:
            for result in search_results:
                print(f"- {result['title']} (Score: {result['score']:.2f})")
    
    # Get and display full content for a specific course
    if course_ids:
        print(f"\nFetching full content for course {course_ids[0]}:")
        course = await service.get_course_content(course_ids[0])
        if course:
            print(f"Course: {course.course_info.title}")
            print(f"Topics: {len(course.topics)}")
            print(f"Weeks: {len(course.weeks)}")
            print(f"Lectures: {len(course.lectures)}")
            
            print("\nWeeks:")
            for week in course.weeks:
                print(f"- Week {week.order}: {week.title}")
            
            print("\nSample lectures:")
            for lecture in course.lectures[:3]:  # Show first 3 lectures only
                print(f"- {lecture.title} (Week {lecture.week}, Order {lecture.order})")
    
    print("\nTesting completed successfully!")

if __name__ == "__main__":
    asyncio.run(main()) 