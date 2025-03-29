from typing import Annotated, Sequence, Optional, Dict, Any, List
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages
from enum import Enum


class ResearchContext(TypedDict):
    topic: str
    query: str
    sources: List[Dict[str, Any]]
    findings: List[Dict[str, Any]]


class TaskStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    context: Optional[
        Dict[str, Any]
    ]  # Changed from ResearchContext to match actual usage
    current_agent: str
    next_step: str
    metadata: Optional[Dict[str, Any]]


# ...................................................helper functions.........................................


def initialize_state() -> AgentState:
    """Initialize the agent state with default values."""
    return {
        "messages": [],
        "context": {"topic": "", "query": "", "sources": [], "findings": []},
        "current_agent": "supervisor",
        "next_step": "supervisor",
        "metadata": {},
    }


def set_task(state: AgentState, task: str) -> AgentState:
    """Set the current task and update status."""
    new_state = state.copy()
    new_state["current_task"] = task
    new_state["task_status"] = TaskStatus.IN_PROGRESS
    return new_state


def update_task_status(state: AgentState, status: TaskStatus) -> AgentState:
    """Update the status of the current task."""
    new_state = state.copy()
    new_state["task_status"] = status
    return new_state

def clear_state(state: AgentState) -> AgentState:
    """Clear the agent state."""
    new_state = initialize_state()
    new_state["messages"] = state["messages"]
    new_state["current_agent"] = state["current_agent"]
    new_state["next_step"] = state["next_step"]
    return new_state

# ...................................................research context functions.........................................


def set_research_context(state: AgentState, topic: str, query: str) -> AgentState:
    """Initialize or update the research context."""
    new_state = dict(state)
    if "context" not in new_state or new_state["context"] is None:
        new_state["context"] = {
            "topic": topic,
            "query": query,
            "sources": [],
            "findings": [],
        }
    else:
        new_state["context"]["topic"] = topic
        new_state["context"]["query"] = query

    return new_state


def add_research_source(state: AgentState, source: Dict[str, Any]) -> AgentState:
    """Add a research source to the research context."""
    new_state = dict(state)
    if new_state.get("context") is not None:
        sources = new_state["context"].get("sources", [])
        new_state["context"]["sources"] = sources + [source]
    return new_state


def add_research_finding(state: AgentState, finding: Dict[str, Any]) -> AgentState:
    """Add a research finding to the research context."""
    new_state = dict(state)
    if new_state.get("context") is not None:
        findings = new_state["context"].get("findings", [])
        new_state["context"]["findings"] = findings + [finding]
    return new_state


# ....................................................metadata functions.........................................


def update_metadata(state: AgentState, key: str, value: Any) -> AgentState:
    """
    Update a specific metadata key-value pair in the state.
    Args:
        state: Current agent state
        key: Metadata key to update
        value: New value to set
    Returns:
        AgentState: Updated state with new metadata
    """
    new_state = dict(state)  # Create a new state dict to avoid modifying the original
    metadata = dict(
        state.get("metadata", {}) or {}
    )  # Create a new metadata dict to avoid modifying the original
    metadata[key] = value
    new_state["metadata"] = metadata
    return new_state


def get_metadata(state: AgentState, key: str, default: Any = None) -> Any:
    """Get a value from the metadata by key."""
    if state.get("metadata") is None:
        return default

    return state["metadata"].get(key, default)


def get_subquestions(state: AgentState) -> List[Dict[str, Any]]:
    """Get all subquestions and their routes from state metadata."""
    metadata = state.get("metadata", {})
    subquestions = []
    i = 0
    while f"subq_{i}" in metadata:
        subquestions.append(metadata[f"subq_{i}"])
        i += 1
    return subquestions


def clear_subquestions(state: AgentState) -> AgentState:
    """Clear all subquestion data from state metadata."""
    new_state = dict(state)
    metadata = dict(state.get("metadata", {}))
    i = 0
    while f"subq_{i}" in metadata:
        del metadata[f"subq_{i}"]
        i += 1
    new_state["metadata"] = metadata
    return new_state
