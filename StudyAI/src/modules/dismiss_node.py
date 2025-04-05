from src.core.state import AgentState, clear_state, get_metadata
from typing import AsyncGenerator
from langchain_core.messages import SystemMessage, AIMessage
from langgraph.graph import END


async def dismiss_node(state: AgentState) -> AsyncGenerator[AgentState, None]:
    # Check the last system message to determine dismissal reason
    last_message = next(
        (
            msg.content
            for msg in reversed(state["messages"])
            if isinstance(msg, SystemMessage)
        ),
        None,
    )

    # Check if the message was routed from supervisor by looking at metadata
    from_supervisor = state.get("metadata", {}).get("from_supervisor", False)

    if last_message and "Generic" in last_message and not from_supervisor:
        response = """Hi! While I'm happy to chat, I'm designed to help with academic questions. Please feel free to ask me about your courses, assignments, or study materials!"""
    elif last_message and "Inappropriate" in last_message and not from_supervisor:
        response = f"""I apologize, but I cannot process this question. Please maintain professional and academic conduct in our interactions."""
    else:
        response = "I can only help with questions related to your enrolled courses. Please ask about your academic studies."

    state["messages"].append(AIMessage(content=response))
    state["next_step"] = END
    state = clear_state(state)
    yield state
