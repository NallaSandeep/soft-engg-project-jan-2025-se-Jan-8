from typing import Dict, Any, List
from langchain_core.messages import trim_messages, BaseMessage
from src.core.state import AgentState

class ConversationMemory:
    def retrieve_past_messages(
        self,
        state: AgentState,
        max_messages: int = 5
    ) -> Dict[str, Any]:
        """Retrieve conversation history for a specific thread.
        
        Args:
            state (AgentState): Current conversation state
            max_messages (int): Maximum number of messages to return
            
        Returns:
            Dict[str, Any]: Dictionary containing trimmed message history
        """
        messages = state["messages"]
        
        selected_messages = trim_messages(
            messages,
            token_counter=max_messages,
            max_tokens=5,
            strategy="last",
            start_on="human",
            include_system=True,
            allow_partial=False,
        )
        
        return {"messages": selected_messages}