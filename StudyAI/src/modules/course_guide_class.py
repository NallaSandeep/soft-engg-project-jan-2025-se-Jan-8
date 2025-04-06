from src.prompt.prompts import get_relevent_course_prompt
from src.modules.integerity_tool import IntegrityChecker
from typing import Dict, Any, List
from src.core.base import BaseAgent
from config import Config
import json
import pprint
import logging


class CourseGuideAgent(BaseAgent):
    """Agent responsible for handling course-related queries and determining relevant courses."""

    def __init__(self):
        super().__init__()
        self.integrity_checker = IntegrityChecker()

    async def get_relevant_courses(
        self,
        query: str,
        subscribed_courses: List[str] = None,
    ) -> Dict[str, Any]:
        """Retrieve relevant courses based on the query using StudyIndexer API."""

        if subscribed_courses is None:
            subscribed_courses = ["SE101", "MAD201", "DBMS101", "BA201"]

        try:
            prompt = get_relevent_course_prompt(query)
            chain = self.create_chain(prompt)
            course_result = await chain.ainvoke({})

            if course_result in ["None", "none", ""]:
                return {
                    "courses": [],
                    "summary": "No relevant courses found for your query.",
                }

            # Parse the result which should be in format: "COURSE_CODE|COURSE_NAME|BRIEF_SUMMARY"
            parts = course_result.split("|", 2)

            if len(parts) < 3:
                # Handle malformed response
                course_code = parts[0] if len(parts) > 0 else "Unknown"
                course_name = parts[1] if len(parts) > 1 else "Unknown Course"
                course_summary = "No summary provided"
            else:
                course_code, course_name, course_summary = parts

            formatted_course = {
                "id": course_code,
                "name": course_name,
                "summary": course_summary,
            }

            summary = (
                f"Found relevant course for your query: {course_code} - {course_name}"
            )

            response = {"courses": [formatted_course], "summary": summary}

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

        course_info = await self.get_relevant_courses(query)

        # Replace print with proper logging
        logging.debug(f"Course Info: {course_info}")

        if not course_info["courses"]:
            return {"courses": [], "content": {}, "summary": course_info["summary"]}

        # Since get_relevant_courses only returns one course, we can simplify this
        content_results = {}

        try:
            # Get the single course directly
            course = course_info["courses"][0]
            course_id = course["id"]
            content = await self.get_course_content(course_id, query)

            # Combine course details with content
            content_results[course_id] = {
                "name": course.get("name", "Unknown Course"),
                "summary": course.get("summary", "No summary provided"),
                "content": content,
            }
        except Exception as e:
            logging.error(f"Error fetching content for course: {str(e)}")
            course_id = (
                course_info["courses"][0]["id"] if course_info["courses"] else "unknown"
            )
            content_results[course_id] = {
                "name": (
                    course_info["courses"][0].get("name", "Unknown Course")
                    if course_info["courses"]
                    else "Unknown Course"
                ),
                "summary": (
                    course_info["courses"][0].get("summary", "No summary provided")
                    if course_info["courses"]
                    else "No summary provided"
                ),
                "content": f"Error retrieving content: {str(e)}",
            }

        return {
            "courses": course_info["courses"],
            "content": content_results,
            "summary": course_info["summary"],
        }
