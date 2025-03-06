from typing import Literal
from langgraph.graph import END
import logging
import asyncio
from langchain_core.messages import SystemMessage, AIMessage
from src.core.base import BaseAgent
from src.core.state import AgentState

from typing import AsyncGenerator


class Supervisor(BaseAgent):
    """Supervisor agent that routes queries to appropriate handlers."""

    ROUTES = Literal["rag", "course_guidance", "dismiss"]

    def __init__(self):
        """Initialize the supervisor agent."""
        super().__init__()  # Use BaseAgent's default initialization
        self.system_message = "You are an intelligent academic assistant router."

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
        supervisor = Supervisor()
        # last_message = (
        #     state["messages"][-1].content if state["messages"] else "No messages yet"
        # )

        # Make it awaitable since route is an async method
        # next_step = asyncio.run(supervisor.route(last_message))

        # state["next_step"] = END if next_step == "END" else next_step
        # state["current_agent"] = next_step if next_step != "END" else "supervisor"

        # logging.info(f"Routing to: {next_step}")

        # Use astream instead of invoke for streaming
        async for chunk in supervisor.llm.astream(state["messages"]):
            if hasattr(chunk, "content") and chunk.content:
                state["messages"].append(AIMessage(content=chunk.content))
                # Allow streaming to propagate through the graph
                state["next_step"] = END
                yield state

        # Two lines for testing
        # res = supervisor.llm.invoke(state["messages"])
        # state["messages"].append(AIMessage(content=res.content))
        # state["next_step"] = END
        # return state

    except Exception as e:
        logging.error(f"Supervisor node error: {str(e)}")
        state["messages"].append(
            SystemMessage(
                content="Sorry, I cannot help with that question due to internal error."
            )
        )
        state["next_step"] = END
        yield state
