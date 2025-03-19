"""Unit tests for core functionality."""

import pytest
import os
import sys
from unittest.mock import MagicMock, patch
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.core.base import BaseAgent
from src.core.memory import ConversationMemory
from src.core.state import AgentState, StateManager
from src.core.workflow import create_workflow


class TestBaseAgent:
    """Tests for the BaseAgent class."""

    def test_initialization(self):
        """Test that the BaseAgent initializes correctly."""
        with patch("src.core.base.ChatGoogleGenerativeAI"):
            agent = BaseAgent(model_name="test-model", temperature=0.5)
            assert agent.model_name == "test-model"
            assert agent.temperature == 0.5
            assert agent.memory is not None
            assert agent.output_parser is not None

    def test_format_response(self):
        """Test that format_response returns the expected structure."""
        with patch("src.core.base.ChatGoogleGenerativeAI"):
            agent = BaseAgent()
            response = agent.format_response("Test response", "test-thread")

            assert response["content"] == "Test response"
            assert response["thread_id"] == "test-thread"
            assert "metadata" in response
            assert response["metadata"]["model"] == agent.model_name
            assert response["metadata"]["temperature"] == agent.temperature

    def test_create_chain(self):
        """Test that create_chain returns a callable chain."""
        with patch("src.core.base.ChatGoogleGenerativeAI"):
            with patch("src.core.base.ChatPromptTemplate"):
                agent = BaseAgent()
                chain = agent.create_chain("Test prompt {input}")
                assert callable(chain)


class TestConversationMemory:
    """Tests for the ConversationMemory class."""

    def test_initialization(self):
        """Test that ConversationMemory initializes correctly."""
        memory = ConversationMemory(max_token_limit=5000)
        assert memory.max_token_limit == 5000

    def test_retrieve_past_messages(self):
        """Test retrieving past messages from state."""
        memory = ConversationMemory()

        # Create a test state with messages
        state = AgentState(
            messages=[
                SystemMessage(content="System message"),
                HumanMessage(content="User message 1"),
                AIMessage(content="AI response 1"),
                HumanMessage(content="User message 2"),
                AIMessage(content="AI response 2"),
            ],
            current_agent="test",
            next_step="test",
            metadata={},
        )

        # Retrieve messages
        result = memory.retrieve_past_messages(state, max_messages=3)

        assert "messages" in result
        assert len(result["messages"]) <= 3

    def test_get_timestamp(self):
        """Test that get_timestamp returns a string."""
        memory = ConversationMemory()
        timestamp = memory.get_timestamp()
        assert isinstance(timestamp, str)
        assert "T" in timestamp  # ISO format contains T between date and time

    def test_summarize_conversation(self):
        """Test summarizing conversation history."""
        memory = ConversationMemory()

        # Create test messages
        messages = [
            HumanMessage(content="Hello, how are you?"),
            AIMessage(content="I'm doing well, thank you for asking!"),
            HumanMessage(content="Can you help me with a question?"),
            AIMessage(content="Of course, I'd be happy to help. What's your question?"),
        ]

        summary = memory.summarize_conversation(messages, max_length=100)

        assert isinstance(summary, str)
        assert len(summary) <= 100
        assert "User" in summary
        assert "Assistant" in summary


class TestStateManager:
    """Tests for the StateManager class."""

    def test_create_initial_state(self):
        """Test creating an initial state."""
        initial_messages = [HumanMessage(content="Initial message")]
        metadata = {"test_key": "test_value"}

        state = StateManager.create_initial_state(initial_messages, metadata)

        assert state["messages"] == initial_messages
        assert state["current_agent"] == "supervisor"
        assert state["next_step"] == "supervisor"
        assert state["metadata"] == metadata

    def test_update_metadata(self):
        """Test updating metadata in state."""
        # Create initial state
        state = StateManager.create_initial_state(
            metadata={"existing_key": "existing_value"}
        )

        # Update metadata
        updated_state = StateManager.update_metadata(state, "new_key", "new_value")

        assert updated_state["metadata"]["existing_key"] == "existing_value"
        assert updated_state["metadata"]["new_key"] == "new_value"

    def test_get_metadata(self):
        """Test getting metadata from state."""
        # Create state with metadata
        state = StateManager.create_initial_state(metadata={"test_key": "test_value"})

        # Get existing metadata
        value = StateManager.get_metadata(state, "test_key")
        assert value == "test_value"

        # Get non-existent metadata with default
        value = StateManager.get_metadata(state, "non_existent", "default_value")
        assert value == "default_value"


class TestWorkflow:
    """Tests for the workflow functionality."""

    def test_create_workflow(self):
        """Test creating a workflow."""
        with patch("src.core.workflow.supervisor_node"):
            with patch("src.core.workflow.rag_agent_node"):
                with patch("src.core.workflow.course_guidance_node"):
                    with patch("src.core.workflow.integrity_node"):
                        with patch("src.core.workflow.dismiss_node"):
                            with patch("langgraph.graph.StateGraph.compile"):
                                workflow = create_workflow()
                                assert workflow is not None

    @pytest.mark.asyncio
    async def test_dismiss_node(self):
        """Test the dismiss node functionality."""
        from src.core.workflow import dismiss_node

        # Create initial state
        state = StateManager.create_initial_state()

        # Process through dismiss node
        async for updated_state in dismiss_node(state):
            assert (
                "I cannot help with that question"
                in updated_state["messages"][-1].content
            )
            assert updated_state["current_agent"] == "supervisor"
            assert updated_state["next_step"] == "END"
            break
