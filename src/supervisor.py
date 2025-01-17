from typing import Literal, Dict, List
from typing_extensions import TypedDict
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import MessagesState, StateGraph, END
from langgraph.types import Command
from src.agents.rag_agent import RAGAgent
from src.utils.helper import create_agent
from src.core.manager import ConversationManager
from config.config import load_environment_variables, configure_langsmith

# Routing literals
RouterNextLiteral = Literal["course_guidance", "rag", "academic_integrity", "study_plan", "FINISH"]
SupervisorReturnLiteral = Literal["course_guidance", "rag", "academic_integrity", "study_plan", "__end__"]

SYSTEM_PROMPTS = {
    "course_guidance": "You help students with course-related queries and guidance",
    "rag": "You retrieve and analyze relevant course materials",
    "academic_integrity": "You ensure academic integrity and prevent plagiarism",
    "study_plan": "You help create and optimize study plans"
}

class Router(TypedDict):
    next: RouterNextLiteral

class AgentSupervisor:
    def __init__(self, config: dict):
        self.config = config
        self.conversation_manager = ConversationManager()
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            google_api_key=config['google_api_key'],
            temperature=0.7
        )
        self.agents = self._initialize_agents()

    def _initialize_agents(self) -> Dict:
        agents = {}
        # Initialize RAG agent separately due to its unique requirements
        agents["rag"] = RAGAgent(self.config)
        
        # Initialize other agents using helper
        for member in ["course_guidance", "academic_integrity", "study_plan"]:
            agents[member] = create_agent(
                llm=self.llm,
                tools=[],
                system_prompt=SYSTEM_PROMPTS[member]
            )
        return agents

    def process_query(self, query: str, state: MessagesState) -> MessagesState:
        if not self.conversation_manager.check_rate_limit():
            state["messages"].append({
                "role": "assistant",
                "content": "Rate limit exceeded. Please wait."
            })
            return state

        current_agent = state.get("current_agent", "course_guidance")
        agent = self.agents[current_agent]
        
        # Process through current agent
        response = agent.process_query(query)
        
        state["messages"].append({
            "role": "assistant",
            "content": response,
            "agent": current_agent
        })
        
        return state

    def determine_next_agent(self, messages: List[dict]) -> str:
        context = self.conversation_manager.get_context()
        
        prompt = {
            "role": "system",
            "content": f"""Based on the conversation context and last message, determine which agent should handle the next interaction:
            Context: {context}
            Options: course_guidance, rag, academic_integrity, study_plan, or FINISH"""
        }
        
        llm_response = self.llm.with_structured_output(Router).invoke([prompt] + messages[-3:])
        return llm_response["next"]

def get_last_user_message(messages: List[dict]) -> str:
    for message in reversed(messages):
        if message["role"] == "user":
            return message["content"]
    return ""

def supervisor_node(state: MessagesState) -> Command[SupervisorReturnLiteral]:
    config = load_environment_variables()
    configure_langsmith(config)

    if "supervisor" not in state:
        state["supervisor"] = AgentSupervisor(config)

    last_message = get_last_user_message(state["messages"])
    updated_state = state["supervisor"].process_query(last_message, state)
    state.update(updated_state)
    
    next_agent = state["supervisor"].determine_next_agent(state["messages"])
    return Command(goto=END if next_agent == "FINISH" else next_agent)