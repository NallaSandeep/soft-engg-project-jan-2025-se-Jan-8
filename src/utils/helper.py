from langchain.agents import AgentExecutor, initialize_agent, AgentType
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import List

def create_agent(
    llm: ChatGoogleGenerativeAI,
    tools: List,
    system_prompt: str
) -> AgentExecutor:
    """
    Creates a Gemini agent with specified tools and system prompt.
    
    Args:
        llm: Initialized Gemini language model
        tools: List of tools available to the agent
        system_prompt: Initial instructions for the agent
    
    Returns:
        AgentExecutor: Configured agent executor
    """
    try:
        # Create prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="messages"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        # Initialize agent
        agent = initialize_agent(
            llm=llm,
            tools=tools,
            agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
            verbose=True
        )

        # Create executor
        executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            handle_parsing_errors=True
        )
        
        return executor
    
    except Exception as e:
        raise RuntimeError(f"Failed to create agent: {e}")