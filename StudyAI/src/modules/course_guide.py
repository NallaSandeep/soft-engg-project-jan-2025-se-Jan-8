from typing import AsyncGenerator, Dict, Any, List
from src.core.base import BaseAgent
from src.core.state import AgentState, get_metadata, clear_state
from src.modules.integerity_tool import IntegrityChecker
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph import END
import logging


class CourseGuideAgent(BaseAgent):
    """Agent responsible for handling course-related queries and determining relevant courses."""

    def __init__(self):
        super().__init__()

    async def get_relevant_courses(self, query: str) -> Dict[str, Any]:
        """Retrieve relevant courses based on the query."""
        # Simple keyword matching algorithm
        query_lower = query.lower()

        for keyword, data in self.course_guide_db.items():
            if keyword.lower() in query_lower:
                return data

        # Return empty result if no match found
        return {"courses": [], "summary": "No relevant courses found for your query."}

    async def get_course_content(self, course_id: str) -> str:
        """Retrieve course content based on the course ID."""
        course_contents = {
            "CS101": "Linear Algebra covers vector spaces, matrices, eigenvalues and eigenvectors, and factorization methods like SVD.",
            "CS105": "Software Engineering teaches software development methodologies, testing approaches including path testing, and project management.",
            "CS106": "Software Development focuses on practical application of SDLC with hands-on projects and coding practices.",
            "CS110": "Machine Learning covers algorithms like regression, classification, neural networks, and matrix factorization techniques including SVD.",
        }

        return course_contents.get(
            course_id, f"No content available for course {course_id}"
        )


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

        # Get relevant courses information
        course_info = await agent.get_relevant_courses(query_to_process)

        # Initialize context structure if it doesn't exist
        if "context" not in state or state["context"] is None:
            state["context"] = {
                "topic": "Course Guide",
                "query": query_to_process,
                "sources": [],
                "findings": [],
            }

        if not course_info["courses"]:
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

            yield state
            return

        # Build the response with course information
        courses_found = course_info["courses"]
        response_parts = []
        response_parts.append(course_info["summary"])
        response_parts.append("\nRelevant courses:")

        course_details = []
        for course in courses_found:
            course_content = await agent.get_course_content(course["id"])
            course_details.append(
                f"- {course['id']}: {course['name']} (Confidence: {course['confidence']:.2f})"
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
            yield state

    except Exception as e:
        logging.error(f"Course guide agent error: {str(e)}")
        state["messages"].append(
            AIMessage(
                content="I apologize, but I encountered an error while processing your query. "
                "Please try again or rephrase your question."
            )
        )
        state["next_step"] = END
        clear_state(state)
    finally:
        yield state
