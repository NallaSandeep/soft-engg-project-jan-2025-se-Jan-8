from typing import AsyncGenerator, Dict, Any
import aiohttp
import logging
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage
from src.core.state import AgentState
from src.core.base import BaseAgent


class RagAgent(BaseAgent):
    """RAG agent for general FAQs."""

    def __init__(self):
        """Initialize the RAG agent."""
        super().__init__()  # Use BaseAgent's default initialization
        self.system_message = (
            "You are an intelligent academic assistant for general FAQs."
        )
        self.search_url = "http://localhost:8000/api/v1/search"
        self.default_search_params = {
            "collection": "general_faq",
            "page": 1,
            "page_size": 5,  # Reduced from 10 to get most relevant docs
            "min_score": 0.5,
            "filters": {},
        }

    async def get_relevant_docs(self, query: str) -> str:
        """Retrieve relevant documents from the search endpoint."""
        try:
            # Prepare request body
            request_body = {"text": query, **self.default_search_params}

            async with aiohttp.ClientSession() as session:
                async with session.post(self.search_url, json=request_body) as response:
                    if response.status == 200:
                        data = await response.json()
                        # Assuming the response has a 'documents' field with relevant text
                        documents = data.get("documents", [])
                        if not documents:
                            return ""

                        # Format documents with their scores if available
                        formatted_docs = []
                        for doc in documents:
                            content = doc.get("content", "")
                            score = doc.get("score", 0)
                            if score >= self.default_search_params["min_score"]:
                                formatted_docs.append(f"{content}")

                        return "\n\n".join(formatted_docs)
                    else:
                        logging.error(f"Search API error: {response.status}")
                        return ""
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
    """RAG agent node that enriches queries and generates final response."""
    try:
        agent = RagAgent()
        last_message = next(
            (
                msg.content
                for msg in reversed(state["messages"])
                if isinstance(msg, HumanMessage)
            ),
            "",
        )

        # Get relevant documents
        context = await agent.get_relevant_docs(last_message)

        if not context:
            state["messages"].append(
                AIMessage(
                    content="I couldn't find any relevant information to help with your query."
                )
            )
            state["next_step"] = "END"
            yield state
            return

        # Store context in metadata
        state["metadata"] = state.get("metadata", {})
        state["metadata"]["rag_context"] = {
            "original_query": last_message,
            "retrieved_context": context,
        }

        # Create final response prompt
        final_prompt = f"""Based on the following context from our knowledge base, provide a comprehensive answer to the user's question.

        User Question: {last_message}

        Relevant Context:
        {context}

        Provide a clear, detailed response that directly addresses the question using the context provided."""

        # Generate final response
        async for chunk in agent.llm.astream([SystemMessage(content=final_prompt)]):
            if hasattr(chunk, "content") and chunk.content:
                state["messages"].append(AIMessage(content=chunk.content))
                state["next_step"] = "END"
                yield state
                return

    except Exception as e:
        logging.error(f"RAG agent error: {str(e)}")
        state["messages"].append(
            AIMessage(
                content="Sorry, I encountered an error while processing your query."
            )
        )
        state["next_step"] = "END"
        yield state
