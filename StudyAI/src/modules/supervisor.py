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
                return "supervisor"  # Complex query, route to supervisor

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
        response = (await chain.ainvoke({})).strip().lower()
        return response == "yes"

    async def _break_down_query(self, message: str) -> List[str]:
        """Break down a complex query into subquestions."""
        prompt = f""" Given the different agents capability:
        - faq_agent: for general FAQs about exam dates, course content, etc.
        - course_guide: for course/curriculum questions actual content of courses
        - dismiss: for out-of-scope queries
        
        Break down the query into simple subquestions to be handled by different agents (max 3 questions).
        Each subquestion should be clear and concise, and should not contain any complex or compound questions.
        
        Examples:
        
        Complex Query: "What is the definition of SVD and is it covered in the end term of Maths 2 course?"
        Subquestions:
        1. What is the syllabus for Maths 2? Is SVD covered? ( Relevent for FAQ agent to ask)
        2. What is the definition of SVD? (Relevent for Course guide agent to ask)
        3. When is the end term for Maths 2? (Relevent for FAQ agent to ask)

        
        Complex Query: "How NASA's Mars rover works and what are the main use cases of Python and JavaScript?"
        Subquestions:
        1. What are the main use cases and advantages of Python? (Relevent for Course guide agent to ask)
        2. What are the main use cases and advantages of JavaScript? (Relevent for Course guide agent to ask)
        3. How does NASA's Mars rover work? (Not relevant for any agent, heading to dismiss agent)
        
        Now break down this query:
        {message}
        
        Return only the numbered subquestions along with relevent agent to ask."""

        chain = self.create_chain(prompt)
        response = await chain.ainvoke({})
        subquestions = [q.strip() for q in response.split("\n") if q.strip()]
        return subquestions

    async def _process_subquestions(self, subquestions: List[str]) -> Dict[str, Any]:
        """Process each subquestion and store results in metadata."""
        metadata = {}
        for i, question in enumerate(subquestions):
            # Prevent infinite recursion by not checking if this is complex
            routing_prompt = self._create_routing_prompt(question)
            chain = self.create_chain(routing_prompt)
            response = await chain.ainvoke({})
            route = self._parse_routing_response(response)

            # Store the subquestion and its route in metadata
            metadata[f"subq_{i}"] = {"question": question, "route": route}
        return metadata

    def _create_routing_prompt(self, message: str) -> str:
        return f"""Analyze this query and respond with only one word: faq_agent, course_guide, or dismiss.
        - faq_agent: for general FAQs
        - course_guide: for course/curriculum questions
        - dismiss: for out-of-scope queries
        
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

        # If it's a complex query, process the subquestions
        if next_step == "supervisor":
            subquestions = await supervisor._break_down_query(last_message)
            subq_metadata = await supervisor._process_subquestions(subquestions)
            for key, value in subq_metadata.items():
                state = update_metadata(state, key, value)

        # Update state with routing decision
        state["next_step"] = next_step
        state["current_agent"] = next_step

    except ValueError as ve:
        logging.error(f"ValueError in supervisor node: {str(ve)}")
        state["next_step"] = "dismiss"
    except Exception as e:
        logging.error(f"Supervisor node error: {str(e)}")
        state["next_step"] = "dismiss"
    finally:
        # Ensure the state is always yielded
        yield state
