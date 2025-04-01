from typing import Dict, Any, List, Optional, AsyncGenerator
from src.core.base import BaseAgent
import logging
from config import Config


class IntegrityChecker(BaseAgent):
    """Integrity agent that ensures academic honesty in responses."""

    def __init__(self, use_mock_data=False):
        super().__init__()
        self.use_mock_data = use_mock_data

    def _generate_mock_response(
        self, query: str, course_ids: List[str]
    ) -> Dict[str, Any]:
        """Generate a mock response for testing purposes without API dependency."""

        trigger_keywords = [
            "exam answer",
            "test solution",
            "assignment solution",
            "homework answer",
            "quiz solution",
            "sql injection",
            "derive the formula",
        ]

        # Check if query contains any trigger keywords
        contains_trigger = any(keyword in query.lower() for keyword in trigger_keywords)

        # Create a mock high match if the query contains a trigger
        if contains_trigger:
            mock_data = {
                "success": True,
                "data": {
                    "matches": [
                        {
                            "assignment_id": "mock_assignment_1",
                            "title": "Database Systems Midterm",
                            "course_id": "101" if not course_ids else course_ids[0],
                            "course_code": "CS101",
                            "course_title": "Introduction to Database Systems",
                            "highest_similarity": 0.92,
                            "matched_questions": ["q1", "q3"],
                            "segments": [
                                {
                                    "query_segment": query[:100],
                                    "matched_segment": "This is a sample matched segment from an assignment.",
                                    "similarity": 0.92,
                                }
                            ],
                        }
                    ],
                    "highest_match": {
                        "assignment_id": "mock_assignment_1",
                        "question_id": "q1",
                        "title": "Database Systems Midterm",
                        "question_title": "SQL Query Question",
                        "score": 0.92,
                        "similarity": 0.92,
                    },
                    "potential_violation": True,
                },
                "is_potential_violation": True,
            }
        else:
            # No potential violation
            mock_data = {
                "success": True,
                "data": {
                    "matches": [],
                    "highest_match": None,
                    "potential_violation": False,
                },
                "is_potential_violation": False,
            }

        return mock_data

    async def check_integrity(
        self, query: str, course_ids: List[str] = None, threshold: float = 0.85
    ) -> Dict[str, Any]:
        """
        Check query for academic integrity concerns by comparing it against known assignments.

        Args:
            query: The user query to check for integrity violations
            course_ids: List of course IDs to check against
            threshold: Score threshold above which a match is considered a potential violation

        Returns:
            Dictionary containing integrity check results
        """
        try:
            if not course_ids:
                course_ids = []

            # Return mock data if enabled
            if self.use_mock_data:
                return self._generate_mock_response(query, course_ids)

            payload = {"query": query, "course_ids": course_ids, "threshold": threshold}

            # Make API call to the integrity check endpoint using the base agent's HTTP client
            result = await self.make_http_request(
                method="POST",
                url=f"http://{Config.HOST}:{Config.STUDY_INDEXER_PORT}/api/v1/integrity-check/check",
                json=payload,
            )

            if not result["success"]:
                logging.error(
                    f"Integrity check API error: {result.get('error', 'Unknown error')}"
                )
                return {
                    "success": False,
                    "error": "Failed to check integrity",
                    "is_potential_violation": False,
                }

            # Process the result
            data = result.get("data", {})

            # Check if there are any matches above the threshold
            is_potential_violation = False
            highest_match = data.get("highest_match", {})

            if highest_match and "score" in highest_match:
                is_potential_violation = highest_match["score"] >= threshold

            return {
                "success": True,
                "data": data,
                "is_potential_violation": is_potential_violation,
            }

        except Exception as e:
            logging.error(f"Error checking integrity: {str(e)}")
            return {
                "success": False,
                "error": f"Integrity check failed: {str(e)}",
                "is_potential_violation": False,
            }
