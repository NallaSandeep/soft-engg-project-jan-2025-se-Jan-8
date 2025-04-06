from src.core.state import AgentState, clear_state
from src.core.base import BaseAgent
from typing import AsyncGenerator
from langchain_core.messages import SystemMessage, AIMessage,  HumanMessage
from langgraph.graph import END

class DismissAgent(BaseAgent):  
    def __init__(self):
        super().__init__()

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

    last_human_message = next(
        (
            msg.content
            for msg in reversed(state["messages"])
            if isinstance(msg, HumanMessage)
        ),
        None,
    )

    agent = DismissAgent()

    # Check if the message was routed from supervisor by looking at metadata
    from_supervisor = state.get("metadata", {}).get("from_supervisor", False)

    if last_message and "Generic" in last_message and not from_supervisor:
        prompt = f"""Answer this generic question: {last_human_message}, and add note to ask questions related to your enrolled courses. Ask the user how you can help them with their academic studies."""
        chain = agent.create_chain(prompt)
        response = await chain.ainvoke({})
    elif last_message and "Inappropriate" in last_message and not from_supervisor:
        response = f"""I apologize, but I cannot process this question. Please maintain professional and academic conduct in our interactions."""
    else:
        response = "I can only help with questions related to your enrolled courses. Please ask about your academic studies."

    state["messages"].append(AIMessage(content=response))
    state["next_step"] = END
    state = clear_state(state)
    yield state
