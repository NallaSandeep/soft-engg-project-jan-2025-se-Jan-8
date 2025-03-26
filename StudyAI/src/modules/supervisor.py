import logging
from langgraph.graph import END
from src.core.base import BaseAgent
from typing import AsyncGenerator, List, Literal, Dict, Any
from langchain_core.messages import HumanMessage
from src.core.state import AgentState, update_metadata


ROUTES = Literal["faq_agent", "course_guide", "supervisor", "dismiss"]


class Supervisor(BaseAgent):
    """Supervisor agent that routes queries to appropriate handlers."""

    def __init__(self):
        super().__init__()  # Use BaseAgent's default initialization

    async def route(self, message: str) -> ROUTES:
        """Route the incoming message to the appropriate agent."""
        try:
            if await self._is_complex_query(message):
                subquestions = await self._break_down_query(message)
                await self._process_subquestions(subquestions)
                return "supervisor"  # After processing all subquestions, return to supervisor agent for final synthesis

            # Regular routing for simple queries
            routing_prompt = self._create_routing_prompt(message)
            chain = self.create_chain(routing_prompt)
            response = await chain.ainvoke({})
            return self._parse_routing_response(response)

        except Exception as e:
            logging.error(f"Routing error: {str(e)}")
            return "dismiss"

    async def _is_complex_query(self, message: str) -> bool:
        prompt = f"""Determine if this query is complex and needs to be broken down into subquestions.
        A complex query typically:
        - Contains multiple distinct questions
        - Requires information from different agents
        - Needs comparative analysis
        
        Response with only 'yes' or 'no'.
        
        Query: {message}
        Response:"""

        chain = self.create_chain(prompt)
        response = (await chain.ainvoke({"input": message})).strip().lower()
        return response == "yes"

    async def _break_down_query(self, message: str) -> List[str]:
        """Break down a complex query into subquestions."""
        prompt = """Break down this complex query into simple, atomic subquestions.
        
        Examples:
        
        Complex Query: "Compare the machine learning and web development tracks, and tell me which has better job prospects?"
        Subquestions:
        1. What are the main components of the machine learning track?
        2. What are the main components of the web development track?
        3. What are the current job market statistics for machine learning positions?
        4. What are the current job market statistics for web development positions?
        
        Complex Query: "Should I learn Python or JavaScript first, and what projects should I build?"
        Subquestions:
        1. What are the main use cases and advantages of Python?
        2. What are the main use cases and advantages of JavaScript?
        3. What are beginner-friendly Python projects?
        4. What are beginner-friendly JavaScript projects?
        
        Now break down this query:
        {message}
        
        Return only the numbered subquestions."""

        chain = self.create_chain(prompt)
        response = await chain.ainvoke({})
        subquestions = [q.strip() for q in response.split("\n") if q.strip()]
        return subquestions

    async def _process_subquestions(self, subquestions: List[str]) -> Dict[str, Any]:
        """Process each subquestion and store results in metadata."""
        metadata = {}
        for i, question in enumerate(subquestions):
            route = await self.route(question)
            # Store the subquestion and its route in metadata
            metadata[f"subq_{i}"] = {"question": question, "route": route}
        return metadata

    def _create_routing_prompt(self, message: str) -> str:
        return f"""Analyze this query and respond with only one word: faq_agent, course_guide, or dismiss.
        - faq_agent: for general FAQs
        - course_guide: for course/curriculum questions
        - dismiss: for out-of-scope queries and end the conversation
        
        Query: {message}
        Response:"""

    def _parse_routing_response(self, response: str) -> ROUTES:
        result = response.strip().lower()
        if result == "faq_agent":
            return "faq_agent"
        elif result == "course_guide":
            return "course_guide"
        else:
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
            None,
        )

        if last_message is None:
            raise ValueError("No last message found for routing.")

        next_step = await supervisor.route(last_message)
        logging.info(f"Routing to: {next_step}")

        # If it's a complex query, get metadata from subquestions
        if next_step == "supervisor" and "metadata" not in state:
            subquestions = await supervisor._break_down_query(last_message)
            subq_metadata = await supervisor._process_subquestions(subquestions)
            for key, value in subq_metadata.items():
                state = update_metadata(state, key, value)

        state["next_step"] = next_step
        state["current_agent"] = next_step
        yield state

    except ValueError as ve:
        logging.error(f"ValueError in supervisor node: {str(ve)}")
        state["next_step"] = "dismiss"
        yield state
    except Exception as e:
        logging.error(f"Supervisor node error: {str(e)}")
        state["next_step"] = "dismiss"
        yield state
    finally:
        # Ensure the state is updated even if an error occurs
        state["current_agent"] = "supervisor"
        state["next_step"] = END
        yield state
