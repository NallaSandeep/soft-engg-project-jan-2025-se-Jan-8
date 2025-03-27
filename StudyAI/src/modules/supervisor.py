import logging
from langgraph.graph import END
from src.core.base import BaseAgent
from typing import AsyncGenerator, List, Literal, Dict, Any
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from src.core.state import AgentState, update_metadata, get_metadata, clear_subquestions
from src.prompt.prompts import (
    COMPLEX_QUERY_PROMPT,
    ROUTING_PROMPT,
    BREAKDOWN_QUERY_PROMPT,
    RESPONSE_SYNTHESIS_PROMPT,
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
            routing_prompt = ROUTING_PROMPT.format(query=message)
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
            routing_prompt = ROUTING_PROMPT.format(query=question)
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
        """Check if all subquestions have been processed and have results."""
        # Get the count of subquestions
        i = 0
        while get_metadata(state, f"subq_{i}") is not None:
            subq = get_metadata(state, f"subq_{i}")
            # Check if this subquestion has a result
            if "result" not in subq:
                return False
            i += 1

        # If we got here and there were any subquestions, all have results
        return i > 0

    async def generate_final_response(self, state: AgentState) -> str:
        """Generate a final synthesized response from all subquestion results."""
        # Extract the original query
        original_query = state.get("metadata", {}).get("original_query", "")

        # Get all subquestions and their results
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
            if "result" in subq:
                context_parts.append(f"Result: {subq['result']}")
            context_parts.append("")  # Add blank line between subquestions

        context = "\n".join(context_parts)

        # Create prompt for response synthesis
        prompt = RESPONSE_SYNTHESIS_PROMPT.format(
            original_query=original_query, subquestion_context=context
        )

        # Generate synthesized response
        chain = self.create_chain(prompt)
        response = await chain.ainvoke({})

        return response


async def supervisor_node(state: AgentState) -> AsyncGenerator[AgentState, None]:
    """Production-ready supervisor node."""
    try:
        if state["next_step"] == "supervisor":
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

            # Store the original query
            if "original_query" not in state.get("metadata", {}):
                state = update_metadata(state, "original_query", last_message)

            # Check if we're returning from another agent with results to store
            if state.get("current_agent") != "supervisor" and state[
                "current_agent"
            ] in ["faq_agent", "course_guide", "dismiss"]:
                # Get the most recent AI response
                last_ai_message = next(
                    (
                        msg.content
                        for msg in reversed(state["messages"])
                        if isinstance(msg, AIMessage)
                    ),
                    None,
                )

                # Find which subquestion this result belongs to
                i = 0
                while get_metadata(state, f"subq_{i}") is not None:
                    subq = get_metadata(state, f"subq_{i}")
                    if (
                        subq.get("route") == state["current_agent"]
                        and "result" not in subq
                    ):
                        # This is the subquestion we just processed
                        subq["result"] = last_ai_message
                        state = update_metadata(state, f"subq_{i}", subq)
                        break
                    i += 1

                # Check if all subquestions have been processed
                if supervisor._check_if_all_subquestions_processed(state):
                    # All subquestions are done, generate final response right here
                    try:
                        final_response = await supervisor.generate_final_response(state)
                        # Add the final response to the messages
                        state["messages"].append(AIMessage(content=final_response))
                        # Clear subquestions to avoid reprocessing
                        state = clear_subquestions(state)
                        # Set the next step to end the workflow
                        state["next_step"] = END
                        yield state
                        return
                    except Exception as e:
                        logging.error(f"Final response generation error: {str(e)}")
                        state["messages"].append(
                            SystemMessage(
                                content="I apologize, but I encountered an error while generating your response."
                            )
                        )
                        state["next_step"] = END
                        yield state
                        return

            next_step = await supervisor.route(last_message)
            logging.info(f"Routing to: {next_step}")

            # If it's a complex query, process the subquestions
            if next_step == "supervisor":
                subquestions = await supervisor._break_down_query(last_message)
                subq_metadata = await supervisor._process_subquestions(subquestions)
                for key, value in subq_metadata.items():
                    state = update_metadata(state, key, value)

                # Get the first unprocessed subquestion
                i = 0
                while get_metadata(state, f"subq_{i}") is not None:
                    subq = get_metadata(state, f"subq_{i}")
                    if "result" not in subq:
                        # Route to the appropriate agent for this subquestion
                        next_step = subq.get("route", "dismiss")
                        break
                    i += 1

                # If there are no subquestions (shouldn't happen normally), end the workflow
                if i == 0:
                    next_step = END

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
