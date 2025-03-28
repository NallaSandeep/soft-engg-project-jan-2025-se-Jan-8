from typing import AsyncGenerator, Dict, Any
import logging
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage
from src.core.state import AgentState
from src.core.base import BaseAgent
from langgraph.graph import END


class RagAgent(BaseAgent):
    """RAG agent for general FAQs."""

    def __init__(self):
        """Initialize the RAG agent."""
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
        state["current_agent"] = "faq_agent"  # Set the current agent to rag_agent
        state["next_step"] = "supervisor"  # Set the next step to rag_agent
        last_message = next(
            (
                msg.content
                for msg in reversed(state["messages"])
                if isinstance(msg, HumanMessage)
            ),
            "",
        )
        if not last_message:
            state["messages"].append(
                AIMessage(content="I couldn't process your query. Please try again.")
            )
            state["next_step"] = END
            yield state
            return

        # Get relevant documents
        context = await agent.get_relevant_docs(last_message)
        if not context or "No relevant documents found" in context:
            state["messages"].append(
                AIMessage(
                    content="I couldn't find specific information about your query. "
                    "If this is about course content, you might want to ask the course guide agent."
                )
            )
            state["next_step"] = END
            yield state
            return

        # Initialize context structure if it doesn't exist
        if "context" not in state or state["context"] is None:
            state["context"] = {
                "topic": "FAQ",
                "query": last_message,
                "sources": [],
                "findings": [],
            }

        # Create the finding with the expected structure
        finding = {
            "query": last_message,
            "content": context,
            "sources": [{"title": "FAQ Knowledge Base"}],
        }

        # Add to findings list
        if "findings" not in state["context"]:
            state["context"]["findings"] = []

        state["context"]["findings"].append(finding)

        # Mark processing as complete for subquestion if this is part of a complex query
        subq_index = None
        i = 0
        while state.get("metadata", {}).get(f"subq_{i}") is not None:
            subq = state["metadata"][f"subq_{i}"]
            if subq.get("question") == last_message:
                subq_index = i
                break
            i += 1

        if subq_index is not None:
            # This is a subquestion, mark it as processed
            state["metadata"][f"subq_{subq_index}"]["result"] = "Processed by FAQ agent"
            
    except Exception as e:
        logging.error(f"RAG agent error: {str(e)}")
        state["messages"].append(
            AIMessage(
                content="I apologize, but I encountered an error while processing your query. "
                "Please try again or rephrase your question."
            )
        )
        state["next_step"] = END
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
