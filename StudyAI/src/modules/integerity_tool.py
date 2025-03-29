from typing import Dict, Any, List, Optional, AsyncGenerator
from src.core.base import BaseAgent
import logging
from config import Config


class IntegrityChecker(BaseAgent):
    """Integrity agent that ensures academic honesty in responses."""

    def __init__(self):
        super().__init__()

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
