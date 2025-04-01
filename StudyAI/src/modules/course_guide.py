from typing import AsyncGenerator
from src.core.state import AgentState, get_metadata, clear_state
from src.modules.integerity_tool import IntegrityChecker
from src.modules.course_guide_class import CourseGuideAgent
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph import END
import logging


async def course_guide_node(state: AgentState) -> AsyncGenerator[AgentState, None]:
    """Course guide node that processes course-related queries"""
    try:
        agent = CourseGuideAgent()

        state["current_agent"] = "course_guide"
        state["next_step"] = "supervisor"

        # Determine if we're processing a subquestion or the original query
        is_subquestion = False
        query_to_process = ""

        if "active_subq_index" in state["metadata"]:
            # We're processing a subquestion from a complex query
            is_subquestion = True
            subq_index = state["metadata"]["active_subq_index"]
            subq = get_metadata(state, f"subq_{subq_index}")
            if subq and "question" in subq:
                query_to_process = subq["question"]

        if not query_to_process:
            # Process the original query or the last human message
            query_to_process = next(
                (
                    msg.content
                    for msg in reversed(state["messages"])
                    if isinstance(msg, HumanMessage)
                ),
                "",
            )

        if not query_to_process:
            state["messages"].append(
                AIMessage(
                    content="I couldn't process your course-related query. Please try again."
                )
            )
            state["next_step"] = END
            yield state
            return

        # Get relevant courses and their content in one optimized call
        courses_data = await agent.get_courses_with_content(query_to_process)

        # Initialize context structure if it doesn't exist
        if "context" not in state or state["context"] is None:
            state["context"] = {
                "topic": "Course Guide",
                "query": query_to_process,
                "sources": [],
                "findings": [],
            }

        # Check if there's an integrity violation
        if courses_data.get("is_integrity_violation", False):
            
            if "integrity_warnings" not in state["context"]:
                state["context"]["integrity_warnings"] = []

            warning_data = {
                "query": query_to_process,
                "warning": courses_data["integrity_warning"],
            }

            # Add related educational topics if available
            if "related_topics" in courses_data and courses_data["related_topics"]:
                warning_data["related_topics"] = courses_data["related_topics"]

            # Add educational content to the context
            if "content" in courses_data and courses_data["content"]:
                warning_data["educational_content"] = courses_data["content"]

            state["context"]["integrity_warnings"].append(warning_data)

            # Create response based on the integrity warning and educational content
            response = courses_data["integrity_warning"]

            # Include the response in the state
            if is_subquestion:
                # This is a subquestion - mark it as processed with the warning and educational content
                subq_index = state["metadata"]["active_subq_index"]
                if f"subq_{subq_index}" in state["metadata"]:
                    state["metadata"][f"subq_{subq_index}"]["result"] = response
            else:
                # This is a standalone query - add the warning message with educational content directly
                state["messages"].append(AIMessage(content=response))
                state["next_step"] = END
                state = clear_state(state)

            yield state
            return

        if not courses_data["courses"]:
            response_message = "I couldn't find specific courses related to your query. Please try a more specific course-related question or topic."

            if is_subquestion:
                # This is a subquestion - mark it as processed with no useful result
                subq_index = state["metadata"]["active_subq_index"]
                if f"subq_{subq_index}" in state["metadata"]:
                    state["metadata"][f"subq_{subq_index}"]["result"] = response_message
            else:
                # This is a standalone query - add the message directly
                state["messages"].append(AIMessage(content=response_message))
                state["next_step"] = END
                state = clear_state(state)

            yield state
            return

        # Build the response with course information
        courses_found = courses_data["courses"]
        response_parts = []
        response_parts.append(courses_data["summary"])
        response_parts.append("\nRelevant courses:")

        course_details = []
        for course in courses_found:
            course_content = courses_data["content"].get(
                course["id"], "No content available"
            )
            course_details.append(
                f"- {course['id']}: {course['name']})"
            )
            course_details.append(f"  {course_content}")

        response_parts.extend(course_details)
        response = "\n".join(response_parts)

        # Create the finding with the expected structure
        finding = {
            "query": query_to_process,
            "content": response,
            "sources": [{"title": "Course Guide Database"}],
        }

        # Add to findings list
        if "findings" not in state["context"]:
            state["context"]["findings"] = []

        state["context"]["findings"].append(finding)

        # Process result based on whether this is a subquestion or original query
        if is_subquestion:
            # Mark the subquestion as processed
            subq_index = state["metadata"]["active_subq_index"]
            if f"subq_{subq_index}" in state["metadata"]:
                state["metadata"][f"subq_{subq_index}"]["result"] = response
        else:
            # state["messages"].append(AIMessage(content=response))
            # state["next_step"] = "supervisor"
            pass

    except Exception as e:
        logging.error(f"Course guide agent error: {str(e)}")
        state["messages"].append(
            AIMessage(
                content="I apologize, but I encountered an error while processing your query. "
                "Please try again or rephrase your question."
            )
        )
        state["next_step"] = END
        state = clear_state(state)
    finally:
        yield state
