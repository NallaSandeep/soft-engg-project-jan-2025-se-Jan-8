from typing import Literal, Dict, List
from typing_extensions import TypedDict
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import MessagesState, END
from langgraph.types import Command
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from config.config import load_environment_variables, configure_langsmith
from src.utils.helper import create_agent

# Routing literals
RouterNextLiteral = Literal["course_guidance", "rag", "academic_integrity", "study_plan", "FINISH"]

members = [
    "course_guidance",
    "rag",
    "academic_integrity",
    "study_plan"
]

SYSTEM_PROMPTS = {
    "course_guidance": "You help students with course-related queries and guidance",
    "rag": "You retrieve and analyze relevant course materials",
    "academic_integrity": "You ensure academic integrity and prevent plagiarism",
    "study_plan": "You help create and optimize study plans"
}

class Router(TypedDict):
    """Worker to route to next. If no workers needed, route to FINISH."""
    next: RouterNextLiteral

SupervisorReturnLiteral = Literal["course_guidance", "rag", "academic_integrity", "study_plan", "__end__"]

class AgentSupervisor:
    def __init__(self, config: dict):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            google_api_key=config['google_api_key'],
            temperature=0.7
        )
        self.agents: Dict = self._initialize_agents()
        self.current_agent = "course_guidance"

    def _initialize_agents(self) -> Dict:
        """Initialize all agents with their specific tools and prompts."""
        agents = {}
        for member in members:
            agents[member] = create_agent(
                llm=self.llm,
                tools=[],  # Add specific tools for each agent type
                system_prompt=SYSTEM_PROMPTS[member]
            )
        return agents

    def execute_agent(self, agent_type: str, query: str) -> str:
        """Execute specific agent with the given query."""
        if agent_type not in self.agents:
            raise ValueError(f"Unknown agent type: {agent_type}")
        return self.agents[agent_type].run(query)

    def determine_next_agent(self, messages: List[dict]) -> str:
        """Determine which agent should handle the next interaction."""
        llm_response = self.llm.with_structured_output(Router).invoke(messages)
        return llm_response["next"]

def get_last_user_message(messages: List[dict]) -> str:
    """Extract the last user message from the message history."""
    for message in reversed(messages):
        if message["role"] == "user":
            return message["content"]
    return ""

def supervisor_node(state: MessagesState) -> Command[SupervisorReturnLiteral]:
    """Main supervisor function that handles message routing and agent execution."""
    # Load configuration
    config = load_environment_variables()
    configure_langsmith(config)

    # Initialize or get supervisor
    if "supervisor" not in state:
        state["supervisor"] = AgentSupervisor(config)

    # Get current agent and last message
    current_agent = state.get("current_agent", "course_guidance")
    last_message = get_last_user_message(state["messages"])

    # Execute current agent
    response = state["supervisor"].execute_agent(current_agent, last_message)

    # Add response to message history
    state["messages"].append({
        "role": "assistant",
        "content": response
    })

    # Determine next agent
    next_agent = state["supervisor"].determine_next_agent(state["messages"])

    # Update state and return command
    if next_agent == "FINISH":
        return Command(goto=END)
    
    state["current_agent"] = next_agent
    return Command(goto=next_agent)