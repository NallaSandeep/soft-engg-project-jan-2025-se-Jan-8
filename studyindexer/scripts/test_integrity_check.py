#!/usr/bin/env python
"""
Test script for the IntegrityCheck feature of StudyIndexer

This script:
1. Creates sample graded assignments
2. Indexes them in the IntegrityCheck service
3. Performs integrity checks with different test submissions
4. Displays the results with match details

Usage:
    python scripts/test_integrity_check.py

Requirements:
    - StudyIndexer service must be running
    - Sample data is included in this script
"""
import os
import sys
import json
import random
import requests
import argparse
from typing import Dict, List, Any
from pprint import pprint

# Add base directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Base URL for the StudyIndexer API
BASE_URL = "http://localhost:8000/api/v1/integrity-check"

def create_sample_assignments() -> List[Dict[str, Any]]:
    """Create sample graded assignments for testing"""
    
    # Assignment 1: Database Systems Midterm
    assignment1 = {
        "assignment_id": "DBMS201_MIDTERM",
        "course_id": "DBMS201",
        "title": "Database Systems Midterm Exam",
        "description": "Midterm examination covering SQL, database design, and normalization",
        "questions": [
            {
                "question_id": "q1",
                "title": "SQL Joins",
                "content": "Write a SQL query to retrieve the name and email of all customers who have placed an order in the last 30 days. Use the Customers and Orders tables.",
                "type": "open_ended"
            },
            {
                "question_id": "q2",
                "title": "Database Normalization",
                "content": "Explain the concept of Third Normal Form (3NF) and provide an example of how to normalize a table that is not in 3NF.",
                "type": "open_ended"
            },
            {
                "question_id": "q3",
                "title": "Entity-Relationship Diagrams",
                "content": "Draw an Entity-Relationship diagram for a university database with entities for Students, Courses, and Professors. Include appropriate relationships and attributes for each entity.",
                "type": "open_ended"
            },
            {
                "question_id": "q4",
                "title": "ACID Properties",
                "content": "What are the ACID properties in database transactions? Explain each property and why it is important for database integrity.",
                "type": "open_ended"
            },
            {
                "question_id": "q5",
                "title": "Database Indexing",
                "content": "What is indexing in databases? Explain the difference between clustered and non-clustered indexes.",
                "type": "multiple_choice",
                "options": [
                    {"id": "a", "text": "Indexing is a way to optimize database performance by creating data structures that improve the speed of data retrieval operations."},
                    {"id": "b", "text": "Indexing is the process of normalizing a database to reduce redundancy."},
                    {"id": "c", "text": "Indexing is a technique to secure database access through encryption."},
                    {"id": "d", "text": "Indexing is a method to compress database files to reduce storage requirements."}
                ]
            }
        ]
    }
    
    # Assignment 2: Algorithms Final Exam
    assignment2 = {
        "assignment_id": "ALGO301_FINAL",
        "course_id": "ALGO301",
        "title": "Algorithms and Data Structures Final Exam",
        "description": "Comprehensive examination covering algorithm complexity, sorting, searching, and advanced data structures",
        "questions": [
            {
                "question_id": "q1",
                "title": "Time Complexity Analysis",
                "content": "Analyze the time complexity of the following algorithm and explain your reasoning:\n\nfunction mystery(n):\n    result = 0\n    for i from 1 to n:\n        for j from 1 to i*i:\n            result = result + 1\n    return result",
                "type": "open_ended"
            },
            {
                "question_id": "q2",
                "title": "Binary Search Trees",
                "content": "Explain the properties of a balanced binary search tree. Implement a function to check if a given binary tree is a valid binary search tree.",
                "type": "open_ended"
            },
            {
                "question_id": "q3",
                "title": "Dynamic Programming",
                "content": "Solve the 0/1 Knapsack problem using dynamic programming. Explain your approach and provide pseudocode for your solution.",
                "type": "open_ended"
            },
            {
                "question_id": "q4",
                "title": "Graph Algorithms",
                "content": "Compare and contrast Dijkstra's algorithm and Bellman-Ford algorithm for finding shortest paths in a graph. When would you use one over the other?",
                "type": "open_ended"
            },
            {
                "question_id": "q5",
                "title": "Sorting Algorithms",
                "content": "What is the worst-case time complexity of Quicksort? How can the pivot selection affect the performance of Quicksort?",
                "type": "multiple_choice",
                "options": [
                    {"id": "a", "text": "O(n log n) - Choosing a good pivot like the median element can help maintain this complexity"},
                    {"id": "b", "text": "O(n²) - This occurs when the pivot selection consistently results in unbalanced partitions"},
                    {"id": "c", "text": "O(n) - Using random pivot selection guarantees linear time"},
                    {"id": "d", "text": "O(log n) - This is achieved with perfect pivot selection"}
                ]
            }
        ]
    }
    
    # Assignment 3: Software Engineering Project
    assignment3 = {
        "assignment_id": "SE401_PROJECT",
        "course_id": "SE401",
        "title": "Software Engineering Design Project",
        "description": "Final project requiring implementation of a web application following software engineering principles",
        "questions": [
            {
                "question_id": "q1",
                "title": "Project Requirements",
                "content": "Write a comprehensive Software Requirements Specification (SRS) document for a student management system. Include functional and non-functional requirements, system constraints, and user stories.",
                "type": "open_ended"
            },
            {
                "question_id": "q2",
                "title": "System Architecture",
                "content": "Design a three-tier architecture for the student management system. Include component diagrams and describe the responsibilities of each layer.",
                "type": "open_ended"
            },
            {
                "question_id": "q3",
                "title": "Testing Strategy",
                "content": "Develop a comprehensive testing strategy for the student management system. Include unit testing, integration testing, system testing, and acceptance testing approaches.",
                "type": "open_ended"
            },
            {
                "question_id": "q4",
                "title": "Design Patterns",
                "content": "Identify and explain at least three design patterns that would be appropriate to use in the implementation of the student management system. Provide code examples for each pattern.",
                "type": "open_ended"
            }
        ]
    }
    
    return [assignment1, assignment2, assignment3]

def create_test_submissions() -> List[Dict[str, Any]]:
    """Create test submissions with varying degrees of similarity to the assignments"""
    
    submissions = [
        {
            "name": "Original SQL Answer",
            "submission_text": "To retrieve the name and email of all customers who have placed an order in the last 30 days, I would use the following SQL query:\n\nSELECT c.customer_name, c.email\nFROM Customers c\nJOIN Orders o ON c.customer_id = o.customer_id\nWHERE o.order_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)\nGROUP BY c.customer_id;\n\nThis query joins the Customers and Orders tables on the customer_id field, filters for orders placed in the last 30 days, and returns unique customers with their names and email addresses.",
            "course_id": "DBMS201",
            "expected_match": "DBMS201_MIDTERM"
        },
        {
            "name": "Paraphrased SQL Answer",
            "submission_text": "For finding customers with recent orders, we can execute this query:\n\nSELECT customer_name, email\nFROM Customers\nINNER JOIN Orders ON Customers.id = Orders.customer_id\nWHERE Orders.date > (CURRENT_DATE - INTERVAL '30 days')\nGROUP BY Customers.id;\n\nThis will give us all customers who ordered something within the last month, showing their names and contact emails without duplicates.",
            "course_id": "DBMS201",
            "expected_match": "DBMS201_MIDTERM"
        },
        {
            "name": "Algorithm Complexity Answer",
            "submission_text": "When analyzing the time complexity of the given mystery function, I need to count the number of operations.\n\nfunction mystery(n):\n    result = 0\n    for i from 1 to n:\n        for j from 1 to i*i:\n            result = result + 1\n    return result\n\nThe outer loop runs n times. For each i, the inner loop runs i² times. So the total number of operations is:\n∑(i=1 to n) i² = n(n+1)(2n+1)/6 which is O(n³)\n\nTherefore, the time complexity of this algorithm is O(n³).",
            "course_id": "ALGO301",
            "expected_match": "ALGO301_FINAL"
        },
        {
            "name": "Software Engineering Requirements",
            "submission_text": "Here's my Software Requirements Specification for a Student Portal:\n\n1. Functional Requirements:\n   - The system shall allow students to register and login\n   - Students shall be able to view their course schedule\n   - The system shall display grades for completed courses\n   - Students shall be able to register for new courses\n\n2. Non-functional Requirements:\n   - The system shall be available 99.9% of the time\n   - Page load times shall not exceed 2 seconds\n   - The system shall support at least 10,000 concurrent users\n   - All personal data shall be encrypted\n\n3. User Stories:\n   - As a student, I want to register for courses so that I can plan my academic schedule\n   - As a student, I want to view my grades so that I can track my academic progress\n   - As a student, I want to update my personal information so that the university has my current contact details",
            "course_id": "SE401",
            "expected_match": "SE401_PROJECT"
        },
        {
            "name": "Unrelated Biology Text",
            "submission_text": "Photosynthesis is the process by which green plants and some other organisms convert light energy into chemical energy. During photosynthesis, plants capture light energy and use it to convert water, carbon dioxide, and minerals into oxygen and energy-rich organic compounds. The process primarily takes place in plant leaves through specialized cell structures called chloroplasts.\n\nThe basic equation for photosynthesis is:\n6CO₂ + 6H₂O + light energy → C₆H₁₂O₆ + 6O₂\n\nThis process is fundamental to life on Earth as it produces oxygen and serves as the primary source of energy for most ecosystems.",
            "course_id": None,
            "expected_match": None
        }
    ]
    
    return submissions

def index_assignments(assignments: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Index the sample assignments in the IntegrityCheck service"""
    
    print(f"Indexing {len(assignments)} sample assignments...")
    results = {"indexed": [], "failed": []}
    
    for assignment in assignments:
        try:
            response = requests.post(f"{BASE_URL}/index", json=assignment)
            response.raise_for_status()
            assignment_id = response.json().get("data", {}).get("assignment_id")
            results["indexed"].append({
                "id": assignment_id,
                "title": assignment.get("title")
            })
            print(f"  ✓ Indexed: {assignment.get('title')}")
        except Exception as e:
            results["failed"].append({
                "title": assignment.get("title"),
                "error": str(e)
            })
            print(f"  ✗ Failed: {assignment.get('title')} - {str(e)}")
    
    return results

def test_submissions(submissions: List[Dict[str, Any]]) -> None:
    """Test the integrity check with various submissions"""
    
    print("\nTesting submissions against indexed assignments...")
    
    for idx, submission in enumerate(submissions):
        print(f"\nSubmission {idx+1}: {submission['name']}")
        
        query = {
            "submission_text": submission["submission_text"],
            "course_id": submission["course_id"]
        }
        
        try:
            response = requests.post(f"{BASE_URL}/check", json=query)
            response.raise_for_status()
            result = response.json()
            
            # Display results
            if result.get("potential_violation", False):
                highest_match = result.get("highest_match", {})
                print(f"  ⚠️  POTENTIAL VIOLATION DETECTED")
                print(f"  Assignment: {highest_match.get('title')}")
                print(f"  Question: {highest_match.get('question_title')}")
                print(f"  Similarity: {highest_match.get('similarity'):.2%}")
                
                # Print top matches
                matches = result.get("matches", [])
                if matches:
                    print("\n  Top matched segments:")
                    for match in matches[:1]:  # Show top match
                        segments = match.get("segments", [])
                        for i, segment in enumerate(segments[:2]):  # Show top 2 segments
                            print(f"\n    Match {i+1} (Similarity: {segment.get('similarity'):.2%}):")
                            print(f"    Submission: '{segment.get('query_segment')[:100]}...'")
                            print(f"    Assignment: '{segment.get('matched_segment')[:100]}...'")
            else:
                print(f"  ✓ No significant matches found")
                
            # Check if the result matches the expected match
            expected = submission.get("expected_match")
            if expected:
                highest_match_id = result.get("highest_match", {}).get("assignment_id")
                if highest_match_id == expected:
                    print(f"  ✓ Expected match found: {expected}")
                else:
                    print(f"  ✗ Expected match {expected} not found. Instead got: {highest_match_id}")
                    
        except Exception as e:
            print(f"  ✗ Error: {str(e)}")

def main():
    """Main entry point for the test script"""
    parser = argparse.ArgumentParser(description="Test the IntegrityCheck feature")
    parser.add_argument("--url", type=str, default="http://localhost:8000",
                        help="Base URL for the StudyIndexer API")
    args = parser.parse_args()
    
    global BASE_URL
    BASE_URL = f"{args.url}/api/v1/integrity-check"
    
    print("StudyIndexer IntegrityCheck Test\n")
    
    # Create sample data
    assignments = create_sample_assignments()
    submissions = create_test_submissions()
    
    # Index assignments
    index_results = index_assignments(assignments)
    
    # Test submissions
    test_submissions(submissions)
    
    print("\nTest completed!")

if __name__ == "__main__":
    main() 