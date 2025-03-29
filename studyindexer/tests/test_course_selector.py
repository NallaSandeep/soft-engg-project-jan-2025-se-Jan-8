"""
Test script for CourseSelector functionality
"""
import json
import os
from datetime import datetime

from app.services.course_selector import CourseSelectorService
from app.models.course_selector import CourseSelectorQuery

def test_course_selector():
    """Test CourseSelector functionality"""
    # Sample course data matching se-compact.json structure
    sample_courses = [
        {
            "course": {
                "course_id": 1001,
                "code": "CS101",
                "title": "Introduction to Programming",
                "description": "Learn basics of programming with Python",
                "department": "Computer Science",
                "credits": 3,
                "LLM_Summary": {
                    "summary": "A comprehensive introduction to programming using Python. Students will learn fundamental concepts and practical coding skills.",
                    "concepts_covered": [
                        "Python Programming",
                        "Basic Data Types",
                        "Control Flow",
                        "Functions"
                    ],
                    "concepts_not_covered": [
                        "Advanced Python Features",
                        "Web Development",
                        "Database Integration"
                    ]
                }
            },
            "weeks": [
                {
                    "week_id": 1,
                    "course_id": 1001,
                    "order": 1,
                    "title": "Python Basics",
                    "estimated_hours": 25
                }
            ],
            "lectures": [
                {
                    "lecture_id": 1,
                    "week_id": 1,
                    "order": 1,
                    "title": "Python Introduction",
                    "resource_type": "youtube",
                    "content_transcript": "Python is a high-level programming language designed to be easy to read and simple to implement.",
                    "keywords": ["python", "programming", "basics"],
                    "LLM_Summary": {
                        "summary": "Introduction to Python programming basics",
                        "concepts_covered": [
                            "Python syntax",
                            "Variables",
                            "Data Types"
                        ]
                    }
                }
            ]
        },
        {
            "course": {
                "course_id": 1002,
                "code": "MATH101",
                "title": "Linear Algebra",
                "description": "Fundamentals of linear algebra including matrices and vectors",
                "department": "Mathematics",
                "credits": 3,
                "LLM_Summary": {
                    "summary": "Essential concepts of linear algebra with focus on practical applications.",
                    "concepts_covered": [
                        "Vectors",
                        "Matrices",
                        "Linear Transformations",
                        "Eigenvalues"
                    ],
                    "concepts_not_covered": [
                        "Advanced Matrix Theory",
                        "Abstract Algebra",
                        "Tensor Analysis"
                    ]
                }
            },
            "weeks": [
                {
                    "week_id": 2,
                    "course_id": 1002,
                    "order": 1,
                    "title": "Vectors and Matrices",
                    "estimated_hours": 25
                }
            ],
            "lectures": [
                {
                    "lecture_id": 2,
                    "week_id": 2,
                    "order": 1,
                    "title": "Vector Basics",
                    "resource_type": "youtube",
                    "content_transcript": "Vectors are quantities having both magnitude and direction.",
                    "keywords": ["vectors", "matrices", "linear algebra"],
                    "LLM_Summary": {
                        "summary": "Introduction to vector operations and properties",
                        "concepts_covered": [
                            "Vector operations",
                            "Vector properties",
                            "Vector applications"
                        ]
                    }
                }
            ]
        }
    ]

    # Initialize service
    service = CourseSelectorService()
    print("✅ Service initialized")

    # Index sample courses
    course_ids = []
    for course_data in sample_courses:
        course_id = service.index_course(course_data)
        course_ids.append(int(course_id))
        print(f"✅ Indexed course: {course_data['course']['title']}")

    # Test queries
    test_cases = [
        {
            "query": "python programming",
            "expected_matches": [1001],  # CS101 should match
            "expected_concepts": ["Python Programming", "Basic Data Types"]
        },
        {
            "query": "vectors and matrices",
            "expected_matches": [1002],  # MATH101 should match
            "expected_concepts": ["Vectors", "Matrices"]
        }
    ]

    for test_case in test_cases:
        query = test_case["query"]
        expected = test_case["expected_matches"]
        expected_concepts = test_case["expected_concepts"]
        
        # Create search query
        search_query = CourseSelectorQuery(
            query=query,
            subscribed_courses=course_ids,
            min_score=0.3,
            limit=10
        )
        
        # Execute search
        total, results, query_time = service.select_courses(search_query)
        
        # Verify results
        matched_ids = [r.course_id for r in results]
        success = all(eid in matched_ids for eid in expected)
        
        print(f"\nTest Query: {query}")
        print(f"Expected matches: {expected}")
        print(f"Actual matches: {matched_ids}")
        print(f"Time: {query_time:.2f}ms")
        print("✅ PASS" if success else "❌ FAIL")
        
        # Print detailed results
        for result in results:
            print(f"\nCourse: {result.title}")
            print(f"Score: {result.score:.4f}")
            print(f"Matched Concepts: {result.matched_topics}")

if __name__ == "__main__":
    test_course_selector() 