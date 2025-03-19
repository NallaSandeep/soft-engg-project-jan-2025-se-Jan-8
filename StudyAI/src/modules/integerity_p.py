from typing import Dict, Any, List, Optional, AsyncGenerator
from src.core.base import BaseAgent
from src.core.state import AgentState
from langchain_core.tools import Tool
from langchain_core.messages import SystemMessage, HumanMessage
import logging
import re

logger = logging.getLogger(__name__)


class IntegrityChecker(BaseAgent):
    """Integrity agent that ensures academic honesty in responses."""

    def __init__(self):
        """Initialize the Integrity agent."""
        super().__init__()
        self.system_message = (
            "You are an academic integrity guardian. Your job is to analyze queries "
            "for potential academic integrity issues and add appropriate context."
        )

    def _create_check_prompt(self, query: str) -> str:
        return f"""Analyze this query for academic integrity concerns and respond in JSON format:
        {{
            "is_graded_assignment": boolean,
            "risk_level": "low"|"medium"|"high",
            "concerns": ["list", "of", "concerns"],
            "modified_query": "query with academic integrity context"
        }}
        
        Consider:
        - Is this for a graded assignment?
        - Is this asking for direct answers?
        - Does this need academic integrity warnings?
        
        Query: {query}
        Response:"""

    async def check_integrity(self, query: str) -> Dict[str, Any]:
        """Check query for academic integrity concerns."""
        try:
            check_prompt = self._create_check_prompt(query)
            chain = self.create_chain(check_prompt)
            response = await chain.ainvoke({})

            # Parse the JSON response
            import json

            return json.loads(response)
        except Exception as e:
            logger.error(f"Integrity check error: {str(e)}")
            return {
                "is_graded_assignment": False,
                "risk_level": "low",
                "concerns": [],
                "modified_query": query,
            }


async def integrity_node(state: AgentState) -> AsyncGenerator[AgentState, None]:
    """Integrity check node that processes queries before routing."""
    try:
        checker = IntegrityChecker()
        last_message = state["messages"][-1].content if state["messages"] else ""

        # Perform integrity check
        integrity_result = await checker.check_integrity(last_message)

        # Store integrity check results in metadata
        state["metadata"] = state.get("metadata", {})
        state["metadata"]["integrity"] = integrity_result

        # Add integrity context if needed
        if integrity_result["risk_level"] in ["medium", "high"]:
            warnings = []
            if integrity_result["is_graded_assignment"]:
                warnings.append(
                    "⚠️ This appears to be related to graded work. Remember to:"
                    "\n- Apply your own understanding"
                    "\n- Follow your institution's academic integrity policies"
                    "\n- Use this as guidance, not direct answers"
                )

            if warnings:
                state["messages"].append(SystemMessage(content="\n".join(warnings)))

        # Add modified query with academic integrity context
        if integrity_result["modified_query"] != last_message:
            state["messages"].append(
                SystemMessage(
                    content=f"I'll help you learn about this topic while maintaining academic integrity. "
                    f"Understanding: {integrity_result['modified_query']}"
                )
            )

        # Always route to supervisor next
        state["next_step"] = "supervisor"
        state["current_agent"] = "supervisor"

        yield state

    except Exception as e:
        logger.error(f"Integrity node error: {str(e)}")
        # On error, proceed to supervisor with a warning
        state["messages"].append(
            SystemMessage(
                content="Note: Please ensure you follow academic integrity guidelines."
            )
        )
        state["next_step"] = "supervisor"
        yield state
