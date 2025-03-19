# import sys
# import os

# sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
import logging
from langgraph.graph import StateGraph, END, MessagesState
from langgraph.checkpoint.memory import MemorySaver
from IPython.display import Image, display

from src.modules.supervisor import supervisor_node
from src.core.state import AgentState
from langchain_core.messages import SystemMessage, HumanMessage
from src.modules.faq_agent import rag_agent_node
from src.modules.course_guide import course_guidance_node
from src.modules.integrity import integrity_node
from pprint import pprint
from typing import AsyncGenerator


# ..................................................................................................


async def dismiss_node(state: AgentState) -> AsyncGenerator[AgentState, None]:
    # Return a dismissive answer if the query is beyond deployed scope.
    state["messages"].append(
        SystemMessage(content="Sorry, I cannot help with that question.")
    )
    state["current_agent"] = "supervisor"
    state["next_step"] = END
    yield state


def create_workflow():
    """Create a workflow graph with integrity checking before routing.

    Flow:
    1. Integrity check on question
    2. Supervisor routes based on integrity remarks
    3. Handler processes (RAG, course_guide, or dismiss)
    4. End
    """

    # Create the graph with our state
    workflow = StateGraph(AgentState)

    # Add nodes for each agent including a new dismiss node
    # workflow.add_node("integrity", integrity_node)
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("rag", rag_agent_node)
    workflow.add_node("course_guidance", course_guidance_node)
    workflow.add_node("dismiss", dismiss_node)

    # Set entry point to integrity checker
    # workflow.set_entry_point("integrity")
    workflow.set_entry_point("supervisor")

    # After integrity check, always go to supervisor
    # workflow.add_edge("integrity", "supervisor")

    # Set up conditional edges from the supervisor node
    workflow.add_conditional_edges(
        "supervisor",
        lambda state: state["next_step"],
        {
            "rag": "rag",
            "course_guidance": "course_guidance",
            "dismiss": "dismiss",
            "END": END,
        },
    )

    # Add terminal edges: after processing, route back to supervisor
    workflow.add_edge("rag", END)
    workflow.add_edge("course_guidance", END)
    workflow.add_edge("dismiss", END)

    return workflow.compile(checkpointer=MemorySaver())


# ..................................................................................................

# THIS CODE PRINTS THE GRAPH


# def visualize_workflow(graph):
#     return display(Image(graph.get_graph().draw_mermaid_png()))


# graph = create_workflow()
# visualize_workflow(graph)
