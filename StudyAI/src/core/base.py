from typing import Optional, Dict, Any
from langchain_core.language_models import BaseLanguageModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from .memory import ConversationMemory
from .state import AgentState
from config import Config

class BaseAgent:
    """Base agent class with common functionality."""
    
    def __init__(
        self,
        model_name: str = "gemini-2.0-flash-exp",
        temperature: float = 0.1
    ):
        """Initialize the base agent with model configuration."""
        self.config = Config
        self.model_name = model_name
        self.temperature = temperature
        self.llm = self._load_model()
        self.memory = ConversationMemory()
        self.output_parser = StrOutputParser()

    def _load_model(self) -> BaseLanguageModel:
        """Load the language model based on configuration."""
        return ChatGoogleGenerativeAI(
            model=self.model_name,
            temperature=self.temperature,
            google_api_key=self.config.get("GEMINI_API_KEY")
        )

    def create_chain(self, prompt_template: str):
        """Create a processing chain with the prompt template."""
        prompt = ChatPromptTemplate.from_template(prompt_template)
        return prompt | self.llm | self.output_parser

    def format_response(self, response: str, thread_id: str) -> Dict[str, Any]:
        """Format the model's response with metadata."""
        return {
            "content": response,
            "thread_id": thread_id,
            "metadata": {
                "model": self.model_name,
                "temperature": self.temperature
            }
        }

    def process_with_memory(
        self,
        message: str,
        thread_id: str,
        state: AgentState
    ) -> Dict[str, Any]:
        """Process a message using conversation memory."""
        # Get relevant conversation history
        history = self.memory.retrieve_past_messages(state)
        
        # Create full context
        context = {
            "chat_history": history["messages"],
            "input": message,
            "system_message": self.system_message
        }
        
        # Generate response
        response = self._generate_response(context)
        
        # Format and return
        return self.format_response(response, thread_id)
