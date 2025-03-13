from typing import Dict, Any, List, Optional
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
        super().__init__()  # Use BaseAgent's default initialization
        self.system_message = (
            "You are an academic integrity guardian. Your job is to analyze responses "
            "for potential academic integrity issues and add appropriate remarks."
        )
        self.tools = self._initialize_tools()

    def _initialize_tools(self) -> List[Tool]:
        """Initialize the tools for integrity checking."""
        return [
            Tool.from_function(
                func=self.check_assignment_type,
                name="check_assignment_type",
                description="Check if the content is for a graded assignment",
                return_direct=True,
            ),
            Tool.from_function(
                func=self.add_academic_remarks,
                name="add_academic_remarks",
                description="Add appropriate academic integrity remarks to the response",
                return_direct=True,
            ),
            Tool.from_function(
                func=self.add_noise,
                name="add_noise",
                description="Add educational noise to prevent direct answers for graded work",
                return_direct=True,
            ),
        ]

    async def check_assignment_type(self, query: str) -> Dict[str, Any]:
        """
        Determine if the query is related to a graded assignment.

        Args:
            query: The user's query

        Returns:
            Dict with assignment type information
        """
        # Keywords that might indicate graded work
        graded_keywords = [
            "assignment",
            "exam",
            "quiz",
            "homework",
            "test",
            "graded",
            "due tomorrow",
            "due today",
            "solution",
            "answer key",
        ]

        # Check if any keywords are in the query
        is_graded = any(keyword.lower() in query.lower() for keyword in graded_keywords)

        # More sophisticated detection would use ML classification
        confidence = 0.7 if is_graded else 0.3

        return {"is_graded_assignment": is_graded, "confidence": confidence}

    async def add_academic_remarks(
        self, content: str, integrity_data: Dict[str, Any]
    ) -> str:
        """
        Add academic integrity remarks to the content.

        Args:
            content: The response content
            integrity_data: Data from integrity checks

        Returns:
            Content with added remarks
        """
        remarks = []

        # Add appropriate remarks based on integrity data
        if integrity_data.get("is_graded_assignment", False):
            remarks.append(
                "**Note:** This response provides guidance for learning purposes. "
                "Remember to apply your own understanding when completing graded work."
            )

        # Add general academic integrity reminder
        remarks.append(
            "**Academic Integrity:** Your institution's academic integrity "
            "policies should be followed when using AI assistance."
        )

        # Add remarks to content
        if remarks:
            remarks_text = "\n\n" + "\n\n".join(remarks)
            return content + remarks_text

        return content

    async def add_noise(
        self, content: str, is_graded: bool, noise_level: float = 0.3
    ) -> str:
        """
        Add educational noise to prevent direct answers for graded work.

        Args:
            content: The response content
            is_graded: Whether this is for a graded assignment
            noise_level: How much to modify the content (0-1)

        Returns:
            Content with added educational noise
        """
        if not is_graded:
            return content

        # For graded assignments, replace direct answers with educational guidance
        modified_content = content

        # 1. Replace specific numbers/answers with ranges or guidance
        modified_content = re.sub(
            r"\b(\d+\.?\d*)\b",
            lambda m: f"a value approximately between {float(m.group(1))*0.9:.1f} and {float(m.group(1))*1.1:.1f}",
            modified_content,
        )

        # 2. Add educational prompts
        prompts = [
            "Consider how you might approach this by...",
            "A useful strategy here would be to...",
            "Think about applying these concepts:",
            "You might want to explore:",
        ]

        # Break content into paragraphs and add prompts
        paragraphs = modified_content.split("\n\n")
        if len(paragraphs) > 1:
            for i in range(1, len(paragraphs), 2):
                if i < len(prompts):
                    paragraphs[i] = f"{prompts[i-1]} {paragraphs[i]}"

            modified_content = "\n\n".join(paragraphs)

        # 3. Replace direct conclusions with reflection questions
        conclusion_pattern = r"(In conclusion|Therefore|Thus|Hence|The answer is)"
        modified_content = re.sub(
            conclusion_pattern, "Consider whether", modified_content
        )

        return modified_content

    async def process_response(self, query: str, response: Optional[str] = None) -> str:
        """
        Process a response through integrity checks.

        Args:
            query: The original user query
            response: The generated response

        Returns:
            Processed response with integrity checks applied
        """
        try:
            # Check if this is a graded assignment
            assignment_info = await self.check_assignment_type(query)
            is_graded = assignment_info["is_graded_assignment"]

            # Combine integrity data
            integrity_data = {**assignment_info}

            # Apply transformations based on integrity checks
            processed_response = query

            # Add educational noise for graded assignments
            if is_graded:
                processed_response = await self.add_noise(
                    processed_response, is_graded, noise_level=0.4
                )

            # Add academic remarks
            # processed_response = await self.add_academic_remarks(
            #     processed_response, integrity_data
            # )

            return processed_response

        except Exception as e:
            logger.error(f"Integrity check error: {e}")
            # Fall back to original response with basic disclaimer
            return (
                response + "\n\n**Note:** Please follow academic integrity guidelines."
            )


async def integrity_node(state: AgentState) -> AgentState:
    """Process responses through integrity checks."""
    try:
        # Skip integrity checks if no messages
        if not state["messages"]:
            return state

        # Get the last user message and bot response
        # messages = state["messages"]
        # last_user_message = next(
        #     (
        #         msg.content
        #         for msg in reversed(messages)
        #         if isinstance(msg, HumanMessage)
        #     ),
        #     "",
        # )
        # last_bot_message = messages[-1].content if messages else ""

        # # Skip if no bot message to check
        # if not last_bot_message:
        #     return state

        last_message = (
            state["messages"][-1].content if state["messages"] else "No messages yet"
        )

        # Initialize integrity checker
        integrity_checker = IntegrityChecker()

        # Process the response through integrity checks
        processed_response = await integrity_checker.process_response(last_message)

        # Update the last message with the processed response
        state["messages"].append(SystemMessage(content=processed_response))

        # Add integrity metadata to state if needed
        state["metadata"]["integrity_checked"] = True

        return state

    except Exception as e:
        logger.error(f"Integrity node error: {e}")
        return state
