import logging
from src.core.base import BaseAgent
from typing import List, Literal, Dict, Any
from src.core.state import (
    AgentState,
    get_metadata,
)

from src.prompt.prompts import (
    COMPLEX_QUERY_PROMPT,
    get_routing_prompt,
    BREAKDOWN_QUERY_PROMPT,
    get_response_synthesis_prompt,
)


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
            routing_prompt = get_routing_prompt(query=message)
            chain = self.create_chain(routing_prompt)
            response = await chain.ainvoke({})
            return self._parse_routing_response(response)

        except Exception as e:
            logging.error(f"Routing error: {str(e)}")
            return "dismiss"

    async def _is_complex_query(self, message: str) -> bool:
        prompt = COMPLEX_QUERY_PROMPT.format(query=message)
        chain = self.create_chain(prompt)
        response = (await chain.ainvoke({})).strip().lower()
        return response == "yes"

    async def _break_down_query(self, message: str) -> List[str]:
        """Break down a complex query into subquestions."""
        prompt = BREAKDOWN_QUERY_PROMPT.format(query=message)
        chain = self.create_chain(prompt)
        response = await chain.ainvoke({})
        subquestions = [q.strip() for q in response.split("\n") if q.strip()]
        return subquestions

    async def _process_subquestions(self, subquestions: List[str]) -> Dict[str, Any]:
        """Process each subquestion and store results in metadata."""
        metadata = {}
        for i, question in enumerate(subquestions):
            # Prevent infinite recursion by not checking if this is complex
            routing_prompt = get_routing_prompt(query=question)
            chain = self.create_chain(routing_prompt)
            response = await chain.ainvoke({})
            route = self._parse_routing_response(response)

            # Store the subquestion and its route in metadata
            metadata[f"subq_{i}"] = {"question": question, "route": route}
        return metadata

    def _parse_routing_response(self, response: str) -> ROUTES:
        result = response.strip().lower()
        if result == "faq_agent":
            return "faq_agent"
        elif result == "course_guide":
            return "course_guide"
        else:
            return "dismiss"

    def _check_if_all_subquestions_processed(self, state: AgentState) -> bool:
        """Check if all subquestions have been processed and have results.

        Also verifies if relevant research context exists for subquestions that need it.
        """
        # Get the count of subquestions
        i = 0
        found_subquestions = False

        while get_metadata(state, f"subq_{i}") is not None:
            found_subquestions = True
            subq = get_metadata(state, f"subq_{i}")
            # Check if this subquestion has a result
            if "result" not in subq:
                return False

            # Check if the research context has findings for this specific subquery
            subquery_text = subq.get("question", "")
            if state.get("context") and state["context"].get("findings"):
                found_relevant_finding = False
                for finding in state["context"].get("findings", []):
                    if finding.get("query") == subquery_text:
                        found_relevant_finding = True
                        break

                if not found_relevant_finding:
                    return False
            i += 1
        return found_subquestions

    async def generate_final_response(self, state: AgentState) -> str:
        """Generate a final synthesized response from all subquestion results and research context."""
        # Extract the original query
        original_query = state["metadata"].get("original_query", "")

        # If there are subquestions, get them from metadata
        if any(key.startswith("subq_") for key in state["metadata"]):
            i = 0
            subquestions = []
            while get_metadata(state, f"subq_{i}") is not None:
                subq = get_metadata(state, f"subq_{i}")
                subquestions.append(subq)
                i += 1

            # Format context from subquestions
            context_parts = []
            for i, subq in enumerate(subquestions):
                context_parts.append(f"Subquestion {i+1}: {subq['question']}")
                context_parts.append(f"Route: {subq['route']}")

                # Add result if available
                if "result" in subq:
                    context_parts.append(f"Result: {subq['result']}")

                # Add research findings for this subquestion if available
                if state["context"] and state["context"].get("findings"):
                    for finding in state["context"].get("findings", []):
                        if finding.get("query") == subq["question"]:
                            context_parts.append(
                                f"Research Finding: {finding.get('content', '')}"
                            )

                            # Add sources if available
                            if finding.get("sources"):
                                sources_text = ", ".join(
                                    [
                                        src.get("title", "Untitled Source")
                                        for src in finding.get("sources", [])
                                    ]
                                )
                                context_parts.append(f"Sources: {sources_text}")

                            break

            context_parts.append("")  # Add blank line between subquestions
        else:
            # Handle context for original query when there are no subquestions
            context_parts = []
            original_query = state["metadata"].get("original_query", "")

            # Add research findings for the original query if available
            if state["context"] and state["context"].get("findings"):
                for finding in state["context"].get("findings", []):
                    if finding.get("query") == original_query:
                        context_parts.append(
                            f"Research Finding: {finding.get('content', '')}"
                        )

                        # Add sources if available
                        if finding.get("sources"):
                            sources_text = ", ".join(
                                [
                                    src.get("title", "Untitled Source")
                                    for src in finding.get("sources", [])
                                ]
                            )
                            context_parts.append(f"Sources: {sources_text}")

        context = "\n".join(context_parts)

        # Create prompt for response synthesis
        prompt = get_response_synthesis_prompt(
            original_query=original_query, context=context
        )

        # Generate synthesized response
        chain = self.create_chain(prompt)
        response = await chain.ainvoke({})

        return response
