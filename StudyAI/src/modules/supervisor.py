import logging
from langgraph.graph import END
from typing import AsyncGenerator
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from src.core.state import (
    AgentState,
    update_metadata,
    get_metadata,
)
from src.modules.supervisor_class import Supervisor


async def supervisor_node(state: AgentState) -> AsyncGenerator[AgentState, None]:
    """Production-ready supervisor node."""
    try:
        if state["next_step"] == "supervisor":
            # Initialize required state fields if they don't exist
            if "current_agent" not in state:
                state["current_agent"] = "supervisor"
            if "metadata" not in state:
                state["metadata"] = {}
            if "context" not in state:
                state["context"] = {
                    "topic": "",
                    "query": "",
                    "sources": [],
                    "findings": [],
                }

            supervisor = Supervisor()

            if state["current_agent"] != "supervisor" and state["current_agent"] in [
                "faq_agent",
                "course_guide",
            ]:
                # Check if we're handling a complex query with subquestions
                has_subquestions = any(
                    key.startswith("subq_") for key in state.get("metadata", {})
                )

                if not has_subquestions:
                    # Simple query case - generate final response if original query exists
                    if "original_query" in state.get("metadata", {}):
                        logging.info("Generating final response for original query.")
                        final_response = await supervisor.generate_final_response(state)
                        # Add response as a message
                        state["messages"].append(
                            AIMessage(
                                content=final_response,
                                kwargs={"metadata": state.get("metadata", {})},
                            )
                        )

                        # Clear metadata and context after processing
                        state["current_agent"] = ""
                        state["next_step"] = END
                        state["metadata"] = {}
                        state["context"] = {
                            "topic": "",
                            "query": "",
                            "sources": [],
                            "findings": [],
                        }
                        yield state
                        return
                else:
                    # Complex query case - check if all subquestions are processed
                    if await supervisor._check_if_all_subquestions_processed(state):
                        # All subquestions processed, generate final response
                        final_response = await supervisor.generate_final_response(state)
                        # Add response as a message
                        state["messages"].append(
                            AIMessage(
                                content=final_response,
                                kwargs={
                                    "metadata": state.get("metadata", {})
                                },
                            )
                        )
                        # Clear metadata and context after processing
                        state["current_agent"] = ""
                        state["next_step"] = END
                        state["metadata"] = {}
                        state["context"] = {
                            "topic": "",
                            "query": "",
                            "sources": [],
                            "findings": [],
                        }
                        yield state
                        return
                    else:
                        # Some subquestions still need processing
                        # Find the next unprocessed subquestion
                        i = 0
                        while get_metadata(state, f"subq_{i}") is not None:
                            subq = get_metadata(state, f"subq_{i}")
                            if "result" not in subq:
                                # Route to the appropriate agent for this subquestion
                                next_step = subq.get("route", "dismiss")
                                state["current_agent"] = next_step
                                state["next_step"] = next_step

                                # Set the current subquestion as the active one
                                state["metadata"]["active_subq_index"] = i

                                # Update the context to include this subquestion
                                state["context"]["query"] = subq.get("question", "")

                                yield state
                                return
                            i += 1

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
            if "original_query" not in state["metadata"]:
                state = update_metadata(state, "original_query", last_message)
                state["context"]["topic"] = "AgentAI"
                state["context"]["query"] = last_message

            next_step = await supervisor.route(last_message)
            logging.info(f"Routing to: {next_step}")

            # If it's a complex query, process the subquestions
            if next_step == "supervisor":
                subquestions = await supervisor._break_down_query(last_message)
                if not subquestions:
                    next_step = "dismiss"
                    # Add system message explaining the dismissal
                    state["messages"].append(
                        SystemMessage(
                            content="I couldn't break down your question properly. Please try a more specific query."
                        )
                    )
                else:
                    subq_metadata = await supervisor._process_subquestions(subquestions)
                    for key, value in subq_metadata.items():
                        state = update_metadata(state, key, value)

                    # Get the first unprocessed subquestion
                    i = 0
                    found_unprocessed = False
                    while get_metadata(state, f"subq_{i}") is not None:
                        subq = get_metadata(state, f"subq_{i}")
                        if "result" not in subq:
                            found_unprocessed = True
                            next_step = subq.get("route", "dismiss")
                            state["metadata"]["active_subq_index"] = (
                                i  # Track the active subquestion
                            )
                            state["context"]["query"] = subq.get(
                                "question", ""
                            )  # Set the context query to the subquestion
                            break
                        i += 1

                    if not found_unprocessed:
                        next_step = END

            # Update state with routing decision
            state["next_step"] = next_step
            state["current_agent"] = next_step

    except ValueError as ve:
        logging.error(f"ValueError in supervisor node: {str(ve)}")
        state["next_step"] = "dismiss"
        state["messages"].append(
            AIMessage(content=f"I encountered an issue: {str(ve)}")
        )
    except Exception as e:
        logging.error(f"Supervisor node error: {str(e)}")
        state["next_step"] = "dismiss"
        state["messages"].append(
            AIMessage(content="Sorry, I encountered an error processing your request.")
        )

    yield state
