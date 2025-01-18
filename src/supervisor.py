from typing import Literal, Dict, List
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import MessagesState, END
from langgraph.types import Command
from src.agents.rag_agent import RAGAgent
from src.agents.course_guidance import CourseGuidanceAgent
from src.utils.helper import create_agent
from src.core.manager import ConversationManager
from config.config import load_environment_variables, configure_langsmith

# Routing literals
RouterNextLiteral = Literal["course_guidance", "rag", "FINISH"]
SupervisorReturnLiteral = Literal["course_guidance", "rag", "__end__"]

SYSTEM_PROMPTS = {
    "course_guidance": "You help students with course-related queries and guidance",
    "rag": "You retrieve and analyze relevant course materials",
}

class RouterResponse(BaseModel):
    next: RouterNextLiteral
    confidence: float
    reasoning: str

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
        agents["course_guidance"] = CourseGuidanceAgent(self.config)
        
        # Initialize other agents using helper
        # for member in ["course_guidance", "academic_integrity", "study_plan"]:
        #     agents[member] = create_agent(
        #         llm=self.llm,
        #         tools=[],
        #         system_prompt=SYSTEM_PROMPTS[member]
        #     )
        return agents

    def process_query(self, query: str, state: MessagesState) -> MessagesState:
        if not self.conversation_manager.check_rate_limit():
            state["messages"].append({
                "role": "assistant",
                "content": "Rate limit exceeded. Please wait."
            })
            return state

        current_agent = state.get("current_agent", "rag_agent")
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
        try:
            context = self.conversation_manager.get_context()
            
            prompt = {
                "role": "system",
                "content": """Based on the conversation context and last message, determine:
                1. Which agent should handle the next interaction (course_guidance, rag, or FINISH)
                2. Your confidence in this decision (0-1)
                3. Brief reasoning for your choice

                Respond with:
                {
                    "next": "chosen_agent",
                    "confidence": 0.9,
                    "reasoning": "explanation"
                }"""
            }
            
            response = self.llm.with_structured_output(RouterResponse).invoke(
                [prompt] + messages[-3:]
            )
            return response.next
        except Exception as e:
            print(f"Routing error: {str(e)}")
            return "rag"  # Default fallback

def get_last_user_message(messages: List[dict]) -> str:
    for message in reversed(messages):
        if message["role"] == "user":
            return message["content"]
    return ""

def supervisor_node(state: MessagesState) -> Command[SupervisorReturnLiteral]:
    try:
        config = load_environment_variables()
        configure_langsmith(config)

        if "supervisor" not in state:
            state["supervisor"] = AgentSupervisor(config)

        last_message = get_last_user_message(state["messages"])
        if not last_message:
            return Command("__end__")

        updated_state = state["supervisor"].process_query(last_message, state)
        state.update(updated_state)
        
        next_agent = state["supervisor"].determine_next_agent(state["messages"])
        return Command(goto=END if next_agent == "FINISH" else next_agent)
    except Exception as e:
        print(f"Supervisor error: {str(e)}")
        return Command("__end__")