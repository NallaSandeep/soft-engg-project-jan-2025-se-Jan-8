from typing import AsyncGenerator, Dict, Any, List
from src.core.base import BaseAgent
from src.modules.integerity_tool import IntegrityChecker
from langgraph.graph import END
from config import Config
from collections import OrderedDict
import json
import pprint
import logging


class CourseGuideAgent(BaseAgent):
    """Agent responsible for handling course-related queries and determining relevant courses."""

    def __init__(self, max_cache_size=3, use_mock_data=True):
        super().__init__()
        self._course_cache = OrderedDict()
        self._max_cache_size = max_cache_size
        self.integrity_checker = IntegrityChecker()
        self.use_mock_data = use_mock_data

        # Mock data for testing
        self.mock_courses = {
            "programming": [
                {
                    "code": "CS101",
                    "title": "Introduction to Programming",
                    "description": "Learn fundamentals of programming using Python. Covers variables, loops, conditionals, and basic data structures.",
                },
                {
                    "code": "SE101",
                    "title": "Software Engineering Basics",
                    "description": "Introduction to software development lifecycle, requirements engineering, and project management.",
                }
            ],
            "mathematics": [
                {
                    "code": "MATH101",
                    "title": "Calculus I",
                    "description": "Introduction to differential and integral calculus of single-variable functions.",
                },
                {
                    "code": "MATH201",
                    "title": "Linear Algebra",
                    "description": "Study of vector spaces, linear transformations, matrices, and determinants.",
                },
            ],
            "ai": [
                {
                    "code": "AI101",
                    "title": "Introduction to Artificial Intelligence",
                    "description": "Overview of AI concepts, search algorithms, knowledge representation, and machine learning basics.",
                },
                {
                    "code": "ML202",
                    "title": "Machine Learning",
                    "description": "Fundamental machine learning algorithms, including supervised and unsupervised learning techniques.",
                },
            ],
            "default": [
                {
                    "code": "CS101",
                    "title": "Introduction to Programming",
                    "description": "Learn fundamentals of programming using Python. Covers variables, loops, conditionals, and basic data structures.",
                },
                {
                    "code": "SE101",
                    "title": "Software Engineering Basics",
                    "description": "Introduction to software development lifecycle, requirements engineering, and project management.",
                },
            ],
        }

        self.mock_course_content = {
            "CS101": {
                "source_course": {
                    "title": "Introduction to Programming",
                    "code": "CS101",
                    "match_score": 0.95,
                },
                "content_chunks": [
                    {
                        "type": "lecture",
                        "title": "Variables and Data Types",
                        "description": "An introduction to variables, primitive data types, and type conversion in Python.",
                        "week_number": 1,
                    },
                    {
                        "type": "lab",
                        "title": "First Python Program",
                        "description": "Write your first Python program using variables and basic operations.",
                        "week_number": 1,
                    },
                    {
                        "type": "lecture",
                        "title": "Control Flow",
                        "description": "Learn about if statements, loops, and conditional execution.",
                        "week_number": 2,
                    },
                    {
                        "type": "assignment",
                        "title": "Simple Calculator",
                        "description": "Create a command-line calculator that performs basic operations.",
                        "week_number": 2,
                    },
                ],
            },
            "SE101": {
                "source_course": {
                    "title": "Software Engineering Basics",
                    "code": "SE101",
                    "match_score": 0.82,
                },
                "content_chunks": [
                    {
                        "type": "lecture",
                        "title": "Software Development Lifecycle",
                        "description": "Overview of the stages in software development.",
                        "week_number": 1,
                    },
                    {
                        "type": "lab",
                        "title": "Requirements Gathering",
                        "description": "Techniques for effective requirements gathering.",
                        "week_number": 1,
                    },
                    {
                        "type": "lecture",
                        "title": "Agile Methodologies",
                        "description": "Introduction to Agile and Scrum frameworks.",
                        "week_number": 2,
                    },
                    {
                        "type": "assignment",
                        "title": "Project Specification",
                        "description": "Create a detailed specification for a simple software project.",
                        "week_number": 2,
                    },
                ],
            },
            "AI101": {
                "source_course": {
                    "title": "Introduction to Artificial Intelligence",
                    "code": "AI101",
                    "match_score": 0.94,
                },
                "content_chunks": [
                    {
                        "type": "lecture",
                        "title": "AI Foundations",
                        "description": "Introduction to the key concepts and history of artificial intelligence.",
                        "week_number": 1,
                    },
                    {
                        "type": "lab",
                        "title": "AI Problem Solving",
                        "description": "Implementing basic search algorithms for problem solving.",
                        "week_number": 1,
                    },
                    {
                        "type": "lecture",
                        "title": "Knowledge Representation",
                        "description": "Methods for representing knowledge in AI systems.",
                        "week_number": 2,
                    },
                    {
                        "type": "assignment",
                        "title": "Search Algorithm Implementation",
                        "description": "Implement A* and other search algorithms for a pathfinding problem.",
                        "week_number": 2,
                    },
                ],
            },
            "ML202": {
                "source_course": {
                    "title": "Machine Learning",
                    "code": "ML202",
                    "match_score": 0.92,
                },
                "content_chunks": [
                    {
                        "type": "lecture",
                        "title": "Supervised Learning",
                        "description": "Introduction to supervised learning algorithms and techniques.",
                        "week_number": 1,
                    },
                    {
                        "type": "lab",
                        "title": "Linear Regression",
                        "description": "Implementing and evaluating linear regression models.",
                        "week_number": 1,
                    },
                    {
                        "type": "lecture",
                        "title": "Neural Networks",
                        "description": "Fundamentals of neural networks and backpropagation.",
                        "week_number": 2,
                    },
                    {
                        "type": "assignment",
                        "title": "Classification Model",
                        "description": "Build and evaluate a classification model on a real-world dataset.",
                        "week_number": 2,
                    },
                ],
            },
        }

        # Mock integrity data
        self.mock_integrity = {
            "assignment help": {
                "is_potential_violation": False,
                "data": {
                    "highest_match": {
                        "assignment_info": "Week 3 Programming Assignment",
                        "course_id": "CS101",
                        "score": 0.92,
                    }
                },
            }
        }

    def _add_to_cache(self, key, value):
        if key in self._course_cache:
            del self._course_cache[key]
        elif len(self._course_cache) >= self._max_cache_size:
            self._course_cache.popitem(last=False)
        self._course_cache[key] = value

    async def get_relevant_courses(
        self,
        query: str,
        limit: int = 4,
        min_score: float = 0.3,
        subscribed_courses: List[str] = None,
    ) -> Dict[str, Any]:
        """Retrieve relevant courses based on the query using StudyIndexer API."""

        if subscribed_courses is None:
            subscribed_courses = ["CS101"]

        # Use cache key based on query and parameters
        cache_key = f"{query}_{limit}_{min_score}"
        if cache_key in self._course_cache:
            # Get and refresh position
            value = self._course_cache[cache_key]
            del self._course_cache[cache_key]
            self._course_cache[cache_key] = value
            return value

        # Use mock data if flag is set
        if self.use_mock_data:
            try:
                # Determine which course set to return based on query keywords
                mock_key = "default"
                query_lower = query.lower()

                if any(
                    term in query_lower
                    for term in ["program", "code", "python", "java"]
                ):
                    mock_key = "programming"
                elif any(
                    term in query_lower for term in ["math", "calculus", "algebra"]
                ):
                    mock_key = "mathematics"
                elif any(
                    term in query_lower
                    for term in ["ai", "machine learning", "artificial intelligence"]
                ):
                    mock_key = "ai"

                # Get courses from the selected mock dataset
                courses = self.mock_courses.get(mock_key, self.mock_courses["default"])[
                    :limit
                ]

                # Format the courses for the response
                formatted_courses = [
                    {
                        "id": course.get("code", ""),
                        "name": course.get("title", ""),
                        "description": course.get("description", ""),
                    }
                    for course in courses
                ]

                # Create a summary of what was found
                summary = (
                    f"Found {len(formatted_courses)} relevant courses for your query."
                )
                if formatted_courses:
                    summary += " Here are the most relevant ones:"

                response = {"courses": formatted_courses, "summary": summary}

                # Cache the results for future use
                self._add_to_cache(cache_key, response)
                return response

            except Exception as e:
                logging.error(f"Error using mock course data: {str(e)}")
                return {
                    "courses": [],
                    "summary": f"Error retrieving mock courses: {str(e)}",
                }

        try:
            payload = {
                "query": query,
                "limit": limit,
                "min_score": min_score,
                "subscribed_courses": ["SE101"],
            }

            result = await self.make_http_request(
                method="POST",
                url=f"http://{Config.HOST}:{Config.STUDY_INDEXER_PORT}/api/v1/course-selector/search",
                json=payload,
                headers={"accept": "application/json"},
            )

            logging.info(
                f"Response from course selector: {result.get('success', False)}"
            )

            if isinstance(result, str):
                result = json.loads(result)

            if isinstance(result, dict) and not result.get("success", False):
                return {
                    "courses": [],
                    "summary": f"Error finding courses: {result.get('error', 'Unknown error')}",
                }

            data = result.get("data", {})
            courses = data.get("results", [])
            if not courses:
                return {
                    "courses": [],
                    "summary": "No relevant courses found for your query.",
                }

            # Format the courses for the response
            formatted_courses = [
                {
                    "id": course.get("code", ""),
                    "name": course.get("title", ""),
                    "description": course.get("description", ""),
                }
                for course in courses
            ]

            # Create a summary of what was found
            summary = f"Found {len(formatted_courses)} relevant courses for your query."
            if formatted_courses:
                summary += " Here are the most relevant ones:"

            response = {"courses": formatted_courses, "summary": summary}

            # Cache the results for future use
            self._add_to_cache(cache_key, response)
            return response

        except Exception as e:
            logging.error(f"Unexpected error while searching for courses: {str(e)}")
            return {"courses": [], "summary": f"Error retrieving courses: {str(e)}"}

    async def get_course_content(self, course_id: str, query: str = "") -> str:
        """Retrieve course content based on the course ID and query using StudyIndexer API."""

        # Use mock data if flag is set
        if self.use_mock_data:
            try:
                if course_id not in self.mock_course_content:
                    return f"No relevant content found for course {course_id}{' and query ' + query if query else ''}."

                course_data = self.mock_course_content[course_id]
                source_course = course_data.get("source_course", {})
                course_title = source_course.get("title", "Unknown Course")
                course_code = source_course.get("code", "Unknown Code")
                match_score = source_course.get("match_score", 0)

                summary_parts = []
                summary_parts.append(
                    f"Course: {course_title} ({course_code}) - Relevance: {match_score:.2f}"
                )

                inner_chunks = course_data.get("content_chunks", [])
                for content in inner_chunks:
                    content_type = content.get("type", "Unknown Type")
                    title = content.get("title", content.get("name", "Untitled"))
                    description = content.get("description", "")
                    week_number = content.get("week_number", "N/A")

                    summary_parts.append(f"- {content_type.capitalize()}: {title}")
                    if week_number != "N/A":
                        summary_parts.append(f"  Week: {week_number}")
                    if description:
                        summary_parts.append(f"  Description: {description}")

                return "\n".join(summary_parts)

            except Exception as e:
                logging.error(f"Error using mock content data: {str(e)}")
                return f"Error retrieving mock content for course {course_id}: {str(e)}"

        try:
            result = await self.make_http_request(
                method="GET",
                url=f"http://{Config.HOST}:{Config.STUDY_INDEXER_PORT}/api/v1/course-content/search",
                params={"query": query, "course_ids": course_id, "limit": 10},
                headers={"accept": "application/json"},
            )

            logging.info(
                f"Response from course content search: {result.get('success', False)}"
            )
            pprint.pprint(result)

            if isinstance(result, str):
                result = json.loads(result)

            if not result.get("success", False):
                return f"Error retrieving content for course {course_id}: {result.get('message', 'Unknown error')}"

            data = result.get("data", {})
            content_chunks = data.get("content_chunks", [])

            if not content_chunks:
                return f"No relevant content found for course {course_id}{' and query ' + query if query else ''}."

            summary_parts = []
            # Process only the top 4 chunks
            for chunk in content_chunks[:4]:
                source_course = chunk.get("source_course", {})
                course_title = source_course.get("title", "Unknown Course")
                course_code = source_course.get("code", "Unknown Code")
                match_score = source_course.get("match_score", 0)

                summary_parts.append(
                    f"Course: {course_title} ({course_code}) - Relevance: {match_score:.2f}"
                )

                # Process only the first 4 content items per course
                inner_chunks = chunk.get("content_chunks", [])
                for content in inner_chunks[:4]:
                    content_type = content.get("type", "Unknown Type")
                    # Handle both title and name fields
                    title = content.get("title", content.get("name", "Untitled"))
                    description = content.get("description", "")
                    week_number = content.get("week_number", "N/A")

                    summary_parts.append(f"- {content_type.capitalize()}: {title}")
                    if week_number != "N/A":
                        summary_parts.append(f"  Week: {week_number}")
                    if description:
                        summary_parts.append(f"  Description: {description}")

            return (
                "\n".join(summary_parts)
                if summary_parts
                else f"No content available for course {course_id}{' and query ' + query if query else ''}."
            )

        except Exception as e:
            logging.error(f"Unexpected error while fetching course content: {str(e)}")
            return f"Error retrieving content for course {course_id}: {str(e)}"

    async def get_courses_with_content(self, query: str) -> Dict[str, Any]:
        """Retrieve relevant courses and their content sequentially."""
        # First get relevant courses
        course_info = await self.get_relevant_courses(query)

        print("Course Info:", course_info)

        if not course_info["courses"]:
            return {"courses": [], "content": {}, "summary": course_info["summary"]}

        # Check integrity before providing content
        if self.use_mock_data:
            # Check if the query contains keywords that might indicate integrity issues
            query_lower = query.lower()
            if any(
                term in query_lower
                for term in ["assignment", "homework", "solve", "answer", "solution"]
            ):
                # Use mock data for integrity violation
                mock_integrity_data = self.mock_integrity.get("assignment help", {})
                is_violation = mock_integrity_data.get("is_potential_violation", False)

                # if is_violation:
                #     highest_match = mock_integrity_data.get("data", {}).get(
                #         "highest_match", {}
                #     )
                #     assignment_info = highest_match.get(
                #         "assignment_info", "Unknown assignment"
                #     )
                #     course_id = highest_match.get("course_id", "Unknown course")
                #     score = highest_match.get("score", 0)

                #     # Find relevant topic information to help the student understand the concepts
                #     course_data = next(
                #         (c for c in course_info["courses"] if c["id"] == course_id),
                #         course_info["courses"][0] if course_info["courses"] else None,
                #     )

                #     # Let's get theoretical content that might help
                #     educational_content = {}
                #     related_topics = []

                #     if course_data:
                #         # Mock educational content for the topic
                #         try:
                #             theory_content = await self.get_course_content(
                #                 course_id, "theory concepts"
                #             )
                #             educational_content[course_id] = theory_content

                #             # Extract potential topics from the course description
                #             if (
                #                 "description" in course_data
                #                 and course_data["description"]
                #             ):
                #                 description_parts = course_data["description"].split()
                #                 potential_topics = [
                #                     word
                #                     for word in description_parts
                #                     if len(word) > 4
                #                     and word.lower()
                #                     not in [
                #                         "about",
                #                         "course",
                #                         "will",
                #                         "learn",
                #                         "this",
                #                         "that",
                #                     ]
                #                 ]
                #                 related_topics = potential_topics[
                #                     :5
                #                 ]  # Take up to 5 topic keywords
                #         except Exception as e:
                #             logging.error(
                #                 f"Error creating mock educational content: {str(e)}"
                #             )
                #             educational_content[course_id] = (
                #                 "Could not retrieve educational content."
                #             )

                #     warning_message = (
                #         f"⚠️ ACADEMIC INTEGRITY NOTICE: This appears to be related to a graded "
                #         f"assignment ({assignment_info}) from course {course_id}.\n\n"
                #         f"Instead of providing a direct answer, here are some learning resources "
                #         f"and concepts that might help you understand how to approach this problem:\n\n"
                #     )

                #     # Add educational resources to the warning message
                #     if educational_content:
                #         warning_message += "## Relevant Theory and Concepts\n\n"
                #         for course_id, content in educational_content.items():
                #             warning_message += f"{content}\n\n"

                #     # Add general study tips
                #     warning_message += (
                #         "## Study Tips\n\n"
                #         "* Break down the problem into smaller parts\n"
                #         "* Review lecture notes on these topics\n"
                #         "* Check textbook chapters covering related concepts\n"
                #         "* Consider discussing conceptual approaches with your professor during office hours\n\n"
                #         "I'm here to help you learn the material, not to complete assignments for you. "
                #         "Feel free to ask about general concepts related to this topic!"
                #     )

                #     return {
                #         "courses": course_info["courses"],
                #         "content": educational_content,
                #         "summary": course_info["summary"],
                #         "integrity_warning": warning_message,
                #         "is_integrity_violation": False,
                #         "related_topics": related_topics,
                #     }

        # Regular integrity check with real API
        # integrity_result = await self.integrity_checker.check_integrity(
        #     query, [course["id"] for course in course_info["courses"]]
        # )

        # # If potential integrity violation is detected
        # if integrity_result.get("is_potential_violation", False):
        #     highest_match = integrity_result.get("data", {}).get("highest_match", {})
        #     assignment_info = highest_match.get("assignment_info", "Unknown assignment")
        #     course_id = highest_match.get("course_id", "Unknown course")
        #     score = highest_match.get("score", 0)

        #     # Find relevant topic information to help the student understand the concepts
        #     course_data = next(
        #         (c for c in course_info["courses"] if c["id"] == course_id),
        #         course_info["courses"][0] if course_info["courses"] else None,
        #     )

        #     # Let's get theoretical content that might help
        #     educational_content = {}
        #     related_topics = []

        #     if course_data:
        #         # Extract topics from the query and course description
        #         topic_query = f"theory concepts for understanding {query}"
        #         try:
        #             # Get educational content for the topic
        #             theory_content = await self.get_course_content(
        #                 course_id, topic_query
        #             )
        #             educational_content[course_id] = theory_content

        #             # Try to identify specific topics that might be helpful
        #             for course in course_info["courses"]:
        #                 if "description" in course and course["description"]:
        #                     # Extract potential topics from the course description
        #                     description_parts = course["description"].split()
        #                     potential_topics = [
        #                         word
        #                         for word in description_parts
        #                         if len(word) > 4
        #                         and word.lower()
        #                         not in [
        #                             "about",
        #                             "course",
        #                             "will",
        #                             "learn",
        #                             "this",
        #                             "that",
        #                         ]
        #                     ]
        #                     related_topics.extend(
        #                         potential_topics[:5]
        #                     )  # Take up to 5 topic keywords
        #         except Exception as e:
        #             logging.error(f"Error fetching educational content: {str(e)}")
        #             educational_content[course_id] = (
        #                 "Could not retrieve educational content."
        #             )

        #     warning_message = (
        #         f"⚠️ ACADEMIC INTEGRITY NOTICE: This appears to be related to a graded "
        #         f"assignment ({assignment_info}) from course {course_id}.\n\n"
        #         f"Instead of providing a direct answer, here are some learning resources "
        #         f"and concepts that might help you understand how to approach this problem:\n\n"
        #     )

        #     # Add educational resources to the warning message
        #     if educational_content:
        #         warning_message += "## Relevant Theory and Concepts\n\n"
        #         for course_id, content in educational_content.items():
        #             warning_message += f"{content}\n\n"

        #     # Add general study tips
        #     warning_message += (
        #         "## Study Tips\n\n"
        #         "* Break down the problem into smaller parts\n"
        #         "* Review lecture notes on these topics\n"
        #         "* Check textbook chapters covering related concepts\n"
        #         "* Consider discussing conceptual approaches with your professor during office hours\n\n"
        #         "I'm here to help you learn the material, not to complete assignments for you. "
        #         "Feel free to ask about general concepts related to this topic!"
        #     )

        #     return {
        #         "courses": course_info["courses"],
        #         "content": educational_content,  # Providing educational content instead
        #         "summary": course_info["summary"],
        #         "integrity_warning": warning_message,
        #         "is_integrity_violation": True,
        #         "related_topics": related_topics,
        #     }

        # Fetch content for each course sequentially
        content_results = {}
        for course in course_info["courses"]:
            try:
                # Get content for each course one by one
                content = await self.get_course_content(course["id"], query)
                content_results[course["id"]] = content
            except Exception as e:
                logging.error(
                    f"Error fetching content for course {course['id']}: {str(e)}"
                )
                content_results[course["id"]] = f"Error retrieving content: {str(e)}"

        return {
            "courses": course_info["courses"],
            "content": content_results,
            "summary": course_info["summary"],
            "is_integrity_violation": False,
        }
