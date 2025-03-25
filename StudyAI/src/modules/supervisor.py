from typing import Literal
from langgraph.graph import END
import logging
import asyncio
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage
from src.core.base import BaseAgent
from src.core.state import AgentState

from typing import AsyncGenerator


class Supervisor(BaseAgent):
    """Supervisor agent that routes queries to appropriate handlers."""

    ROUTES = Literal["rag", "course_guidance", "dismiss"]

    def __init__(self):
        """Initialize the supervisor agent."""
        super().__init__()  # Use BaseAgent's default initialization

    async def route(self, message: str) -> ROUTES:
        """Route the incoming message to the appropriate agent."""
        try:
            # Use the chain creation from BaseAgent
            routing_prompt = self._create_routing_prompt(message)
            chain = self.create_chain(routing_prompt)

            # Generate routing decision
            response = await chain.ainvoke({})
            return self._parse_routing_response(response)
        except Exception as e:
            logging.error(f"Routing error: {str(e)}")
            return "END"

    def _create_routing_prompt(self, message: str) -> str:
        return f"""Analyze this query and respond with only one word: rag, course_guidance, or dismiss.
        - rag: for general FAQs
        - course_guidance: for course/curriculum questions
        - dismiss: for out-of-scope queries and end the conversation
        
        Query: {message}
        Response:"""

    def _parse_routing_response(self, response: str) -> ROUTES:
        result = response.strip().lower()
        if result in ("rag", "course_guidance", "dismiss", "end"):
            return result
        return "dismiss"


async def supervisor_node(state: AgentState) -> AsyncGenerator[AgentState, None]:
    """Production-ready supervisor node."""
    try:
        if "current_agent" not in state:
            state["current_agent"] = "supervisor"
        if "metadata" not in state:
            state["metadata"] = {}

        supervisor = Supervisor()

        # Get original query
        last_message = next(
            (
                msg.content
                for msg in reversed(state["messages"])
                if isinstance(msg, HumanMessage)
            ),
            "No messages yet",
        )

        # Initial routing only - since agents now go directly to END
        next_step = await supervisor.route(last_message)
        logging.info(f"Routing to: {next_step}")

        state["next_step"] = next_step
        state["current_agent"] = next_step
        yield state

    except Exception as e:
        logging.error(f"Supervisor node error: {str(e)}")
        state["next_step"] = "dismiss"
        yield state
