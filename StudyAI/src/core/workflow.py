# ..................................................................................................

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from IPython.display import Image, display

from src.modules.supervisor import supervisor_node
from src.core.state import AgentState
from src.modules.faq_agent import faq_agent_node
from src.modules.course_guide import course_guide_node
from src.modules.dismiss_node import dismiss_node
from src.modules.q_type_checker import check_question_type_node


# ..................................................................................................


def create_workflow():
    """Create a workflow graph with integrity checking before routing."""

    # Create the graph with our state
    workflow = StateGraph(AgentState)

    # Add nodes for each agent
    workflow.add_node("check_question_type", check_question_type_node)
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("faq_agent", faq_agent_node)
    workflow.add_node("course_guide_agent", course_guide_node)
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
            "dismiss": "dismiss",
            END: END,
        },
    )

    # Add back edges to supervisor after processing
    workflow.add_edge("faq_agent", "supervisor")
    workflow.add_edge("course_guide_agent", "supervisor")

    # Add terminal edges: after processing
    workflow.add_edge("dismiss", END)

    return workflow.compile(checkpointer=MemorySaver())


# ..................................................................................................

# THIS CODE PRINTS THE GRAPH
# import sys
# import os

# sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# def visualize_workflow(graph):
#     return graph.get_graph().draw_mermaid_png()


# graph = create_workflow()
# image_data = visualize_workflow(graph)
# output_path = "workflow.png"
# with open(output_path, "wb") as f:
#     f.write(image_data)

# os.startfile(output_path)
