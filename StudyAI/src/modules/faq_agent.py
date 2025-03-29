from typing import AsyncGenerator, Dict, Any
import logging
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage
from src.core.state import AgentState, get_metadata, clear_state
from src.core.base import BaseAgent
from langgraph.graph import END


class RagAgent(BaseAgent):
    """RAG agent for general FAQs."""

    def __init__(self):
        super().__init__()

    async def get_relevant_docs(self, query: str) -> str:
        """Retrieve relevant documents from the knowledge base."""
        try:
            return get_docs(query)
        except Exception as e:
            logging.error(f"Error retrieving documents: {str(e)}")
            return ""

    def _create_enrichment_prompt(self, query: str, context: str) -> str:
        return f"""Based on the following context from our knowledge base, enrich the user's query with relevant information.
        Keep the enriched response focused and concise. Include only the most relevant information.

        Context from knowledge base:
        {context}

        Original Query: {query}

        Provide an enriched response that combines the query with relevant context:"""


async def rag_agent_node(state: AgentState) -> AsyncGenerator[AgentState, None]:
    """RAG agent node that processes FAQ queries and generates responses."""
    try:
        agent = RagAgent()
        
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
            clear_state(state)
    finally:
        # Ensure the state is yielded at the end of processing
        yield state


def get_docs(query: str) -> str:
    """Get documents from the knowledge base."""
    if "grading" in query.lower():
        return """
        Grading Document
        NLP
        Quiz 1 - 25%
        Quiz 2 - 25%
        End Term - 50%
        """
    elif "syllabus" in query.lower():
        return """
        Syllabus Document
        Week 1 - Introduction to NLP
        Week 2 - Text Preprocessing
        Week 3 - Feature Extraction
        Week 4 - Model Training
        Week 5 - Evaluation
        Quiz 1- Week 1-2
        Quiz 2 - Week 3-4
        End Term - Week 5
        """
    else:
        return """
        No relevant documents found.
        """
