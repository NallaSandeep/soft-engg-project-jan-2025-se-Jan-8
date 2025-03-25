import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# ..................................................................................................

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from IPython.display import Image, display

from src.modules.supervisor import supervisor_node
from src.core.state import AgentState
from src.modules.faq_agent import rag_agent_node
from src.modules.course_guide import course_guidance_node
from src.modules.dismiss_node import dismiss_node
from src.modules.q_type_checker import check_question_type_node
from pprint import pprint


# ..................................................................................................


def create_workflow():
    """Create a workflow graph with integrity checking before routing."""

    # Create the graph with our state
    workflow = StateGraph(AgentState)

    # Add nodes for each agent
    workflow.add_node("check_question_type", check_question_type_node)
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("faq_agent", rag_agent_node)
    workflow.add_node("course_guide_agent", course_guidance_node)
    workflow.add_node("dismiss", dismiss_node)

    # Set entry point to integrity checker
    workflow.set_entry_point("check_question_type")

    # Set conditional node at check_question_type   
    workflow.add_conditional_edges(
        "check_question_type",
        lambda state: state["next_step"],
        {
            "supervisor": "supervisor",
            "dismiss": "dismiss",
        },
    )
    
    # Set up conditional edges from the supervisor node
    workflow.add_conditional_edges(
        "supervisor",
        lambda state: state["next_step"],
        {
            "faq_agent": "faq_agent",
            "course_guide": "course_guide_agent",
        },
    )
    
    # Add back edges to supervisor after processing
    workflow.add_edge("faq_agent", "supervisor")
    workflow.add_edge("course_guide_agent", "supervisor")

    # Add terminal edges: after processing
    workflow.add_edge("supervisor", END)
    workflow.add_edge("dismiss", END)

    return workflow.compile(checkpointer=MemorySaver())


# ..................................................................................................

# THIS CODE PRINTS THE GRAPH


def visualize_workflow(graph):
    return display(Image(graph.get_graph().draw_mermaid_png()))


graph = create_workflow()
visualize_workflow(graph)
