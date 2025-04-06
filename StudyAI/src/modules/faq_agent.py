import logging
from config import Config
from typing import AsyncGenerator, Dict, Any, List
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage
from src.core.state import AgentState, get_metadata, clear_state
from src.core.base import BaseAgent
from langgraph.graph import END


class FAQAgent(BaseAgent):
    """RAG agent for general FAQs."""

    def __init__(self):
        super().__init__()

    async def get_relevant_docs(self, query: str) -> str:
        """Retrieve relevant documents from the knowledge base."""
        try:
            payload = {
                "query": query,
                "limit": 6,
                "min_score": 0.3,
                "tags": [""],
                "topic": "",
                "source": "",
            }

            # Make API call to the FAQ search endpoint using the base agent's HTTP client
            response = await self.make_http_request(
                method="POST",
                url=f"http://{Config.HOST}:{Config.STUDY_INDEXER_PORT}/api/v1/faq/search",
                json=payload,
                headers={"Content-Type": "application/json"},
            )
            
            print(f"Response from FAQ search: {response.get('success', False)}")
            print(response)

            if response.get("success", False):
                # Check if the data field exists and contains the actual results
                if "data" in response and isinstance(response["data"], dict):
                    data = response["data"]

                    # Check if the nested data structure contains the results
                    if (
                        data.get("success", False)
                        and "results" in data
                        and len(data["results"]) > 0
                    ):
                        results = data["results"]
                        context = "\n\n".join(
                            [
                                f"Source: {result.get('source', 'Unknown')}\n"
                                f"Topic: {result.get('topic', 'General')}\n"
                                f"Q: {result.get('question', '')}\n"
                                f"A: {result.get('answer', '')}"
                                for result in results
                            ]
                        )
                        return context

            return "No relevant documents found."

        except Exception as e:
            logging.error(f"Error retrieving documents: {str(e)}")
            return ""


async def faq_agent_node(state: AgentState) -> AsyncGenerator[AgentState, None]:
    """RAG agent node that processes FAQ queries and generates responses."""
    try:
        agent = FAQAgent()

        state["current_agent"] = "faq_agent"
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
                AIMessage(content="I couldn't process your query. Please try again.")
            )
            state["next_step"] = END
            state = clear_state(state)
            yield state
            return

        # Get relevant documents
        context = await agent.get_relevant_docs(query_to_process)
        if not context or "No relevant documents found" in context:
            response_message = "I couldn't find specific information about your query. If this is about course content, you might want to ask the course guide agent."

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

        # Initialize context structure if it doesn't exist
        if "context" not in state or state["context"] is None:
            state["context"] = {
                "topic": "FAQ",
                "query": query_to_process,
                "sources": [],
                "findings": [],
            }

        # Create the finding with the expected structure
        finding = {
            "query": query_to_process,
            "content": context,
            "sources": [{"title": "FAQ Knowledge Base"}],
        }

        # Add to findings list
        if "findings" not in state["context"]:
            state["context"]["findings"] = []

        state["context"]["findings"].append(finding)

        # Process result based on whether this is a subquestion or original query
        if is_subquestion:
            # Mark the subquestion as processed
            subq_index = state["active_subq_index"]
            if f"subq_{subq_index}" in state["metadata"]:
                response = f"FAQ agent found: {context.strip()}"
                state["metadata"][f"subq_{subq_index}"]["result"] = response
        else:
            yield state

    except Exception as e:
        logging.error(f"RAG agent error: {str(e)}")
        error_message = "I apologize, but I encountered an error while processing your query. Please try again or rephrase your question."

        if state.get("active_subq_index") is not None:
            # Mark the subquestion as errored
            subq_index = state["active_subq_index"]
            if f"subq_{subq_index}" in state["metadata"]:
                state["metadata"][f"subq_{subq_index}"]["result"] = error_message
        else:
            # Direct error message for standalone query
            state["messages"].append(AIMessage(content=error_message))
            state["next_step"] = END
            state = clear_state(state)
    finally:
        # Ensure the state is yielded at the end of processing
        yield state
