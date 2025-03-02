from src.core.state import AgentState
from src.core.base import BaseAgent


class RagAgent(BaseAgent):
    """RAG agent for general FAQs."""

    def __init__(self):
        """Initialize the RAG agent."""
        super().__init__()  # Use BaseAgent's default initialization
        self.system_message = "You are an intelligent academic assistant for general FAQs."

    async def respond(self, message: str) -> str:
        """Respond to the incoming message."""
        return "RAG response"

def rag_agent_node(state: AgentState) -> AgentState:
    return state