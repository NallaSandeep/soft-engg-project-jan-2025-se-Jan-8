from src.core.state import AgentState
from typing import AsyncGenerator
from langchain_core.messages import SystemMessage
from langgraph.graph import END


async def dismiss_node(state: AgentState) -> AsyncGenerator[AgentState, None]:
    # Check the last system message to determine dismissal reason
    last_message = next(
        (
            msg.content
            for msg in reversed(state["messages"])
            if isinstance(msg, SystemMessage)
        ),
        "Unknown reason",
    )

    if last_message and "Generic" in last_message:
        response = """Hi! While I'm happy to chat, I'm designed to help with academic questions.
                    Please feel free to ask me about your courses, assignments, or study materials!"""
    elif last_message and "Inappropriate" in last_message:
        response = f"""I apologize, but I cannot process this question.
            Reason: {last_message} 
            Please maintain professional and academic conduct in our interactions."""
    else:
        response = "I'm unable to process your request at this time."

    state["next_step"] = END
    state["messages"].append(SystemMessage(content=response))
    yield state
