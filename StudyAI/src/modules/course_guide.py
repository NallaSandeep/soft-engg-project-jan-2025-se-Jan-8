from src.core.state import AgentState
from src.core.base import BaseAgent


class CourseGuideAgent(BaseAgent):
    """Course guide agent for course/curriculum questions."""

    def __init__(self):
        """Initialize the course guide agent."""
        super().__init__()  # Use BaseAgent's default initialization
        self.system_message = "You are an intelligent academic assistant for course guidance."
        
    async def respond(self, message: str) -> str:
        """Respond to the incoming message."""
        return "Course guidance response"

def course_guidance_node(state: AgentState) -> AgentState:
    return state