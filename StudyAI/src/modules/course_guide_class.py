from typing import AsyncGenerator, Dict, Any, List
from src.core.base import BaseAgent
from src.modules.integerity_tool import IntegrityChecker
from langgraph.graph import END
from config import Config
from collections import OrderedDict
import json
import logging


class CourseGuideAgent(BaseAgent):
    """Agent responsible for handling course-related queries and determining relevant courses."""

    def __init__(self, max_cache_size=3):
        super().__init__()
        self._course_cache = OrderedDict()
        self._max_cache_size = max_cache_size

    def _add_to_cache(self, key, value):
        if key in self._course_cache:
            del self._course_cache[key]
        elif len(self._course_cache) >= self._max_cache_size:
            self._course_cache.popitem(last=False)
        self._course_cache[key] = value

    async def get_relevant_courses(
        self,
        query: str,
        limit: int = 5,
        min_score: float = 0.3,
        subscribed_courses: List[str] = None,
    ) -> Dict[str, Any]:
        """Retrieve relevant courses based on the query using StudyIndexer API."""

        if cache_key in self._course_cache:
            # Get and refresh position
            value = self._course_cache[cache_key]
            del self._course_cache[cache_key]
            self._course_cache[cache_key] = value
            return value

        if subscribed_courses is None:
            subscribed_courses = ["CS101"]

        # Use cache key based on query and parameters
        cache_key = f"{query}_{limit}_{min_score}"
        if cache_key in self._course_cache:
            return self._course_cache[cache_key]

        try:
            payload = {
                "query": query,
                "limit": limit,
                "min_score": min_score,
                "subscribed_courses": ["CS101"],
            }

            result = await self.make_http_request(
                method="POST",
                url=f"http://{Config.HOST}:{Config.STUDY_INDEXER_PORT}/api/v1/course-selector/search",
                json=payload,
                headers={"accept": "application/json"},
            )
            
            logging.info(f"Response from course selector: {result.get('success', False)}")

            if isinstance(result, str):
                result = json.loads(result)

            if isinstance(result, dict) and not result.get("success", False):
                return {
                    "courses": [],
                    "summary": f"Error finding courses: {result.get('error', 'Unknown error')}",
                }

            # Extract courses from the nested "data" key
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
                    "confidence": course.get("score", 0.0),
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
        try:
            result = await self.make_http_request(
                method="GET",
                url=f"http://{Config.HOST}:{Config.STUDY_INDEXER_PORT}/api/v1/course-content/search",
                params={"query": query, "course_ids": course_id, "limit": 10},
                headers={"accept": "application/json"},
            )
            
            logging.info(f"Response from course content search: {result.get('success', False)}")

            if isinstance(result, str):
                result = json.loads(result)

            if not result["success"]:
                return f"Error retrieving content for course {course_id}: {result.get('message', 'Unknown error')}"

            data = result.get("data", {})
            content_chunks = data.get("content_chunks", [])

            if not content_chunks:
                return f"No relevant content found for course {course_id}{' and query ' + query if query else ''}."

            summary_parts = []
            for chunk in content_chunks:
                source_course = chunk.get("source_course", {})
                course_title = source_course.get("title", "Unknown Course")
                summary_parts.append(f"Course: {course_title}")

                for content in chunk.get("content_chunks", []):
                    content_type = content.get("type", "Unknown Type")
                    title = content.get("title", "Untitled")
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

        if not course_info["courses"]:
            return {"courses": [], "content": {}, "summary": course_info["summary"]}

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
        }
