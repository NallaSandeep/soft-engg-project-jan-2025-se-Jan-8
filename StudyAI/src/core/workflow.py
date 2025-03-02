import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
import logging
from langgraph.graph import StateGraph, END, MessagesState
from langgraph.checkpoint.memory import MemorySaver
from IPython.display import Image, display

from src.modules.supervisor import supervisor_node
from src.core.state import AgentState
from langchain_core.messages import SystemMessage, HumanMessage
from src.modules.rag import rag_agent_node
from src.modules.course_guide import course_guidance_node
from src.modules.integrity import integrity_node
from pprint import pprint


# ..................................................................................................


def dismiss_node(state: AgentState) -> AgentState:
    # Return a dismissive answer if the query is beyond deployed scope.
    state["messages"].append(
        SystemMessage(content="Sorry, I cannot help with that question.")
    )

    # Reset next_step so that the supervisor can reengage
    state["next_step"] = "END"
    return state


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
            END: END,
        },
    )

    # Add terminal edges: after processing, route back to supervisor
    workflow.add_edge("rag", "supervisor")
    workflow.add_edge("course_guidance", "supervisor")
    workflow.add_edge("dismiss", "supervisor")

    return workflow.compile(checkpointer=MemorySaver())


# from langchain_core.messages import HumanMessage
# from langgraph.checkpoint.memory import MemorySaver
# from langgraph.graph import START, MessagesState, StateGraph
# from langchain_google_genai import ChatGoogleGenerativeAI
# from config import Config
# from pprint import pprint

# # Define a new graph
# workflow = StateGraph(state_schema=MessagesState)

# llm = ChatGoogleGenerativeAI(
#     model = "gemini-2.0-flash-exp",
#     temperature= 0.1,
#     google_api_key= Config.get("GEMINI_API_KEY"),
# )

# # Define the function that calls the model
# def call_model(state: MessagesState):
#     response = llm.invoke(state["messages"])
#     # Update message history with response:
#     return {"messages": response}


# # Define the (single) node in the graph
# workflow.add_edge(START, "model")
# workflow.add_node("model", call_model)

# # Add memory
# memory = MemorySaver()
# app = workflow.compile(checkpointer=memory)

# def run(app):
#     config = {"configurable": {"thread_id": "1"}}

#     query = "Hi! I'm Bob."

#     input_messages = [HumanMessage(query)]
#     output = app.invoke({"messages": input_messages}, config)
#     pprint(output["messages"][-1])

#     query = "What's my name?"

#     input_messages = [HumanMessage(query)]
#     output = app.invoke({"messages": input_messages}, config)
#     pprint(output["messages"][-1])

#     return None


# if __name__ == "__main__":
#     res = run(app)
#     print(res)

# ..................................................................................................

# THIS CODE PRINTS THE GRAPH


def visualize_workflow(graph):
    return display(Image(graph.get_graph().draw_mermaid_png()))


graph = create_workflow()
visualize_workflow(graph)
