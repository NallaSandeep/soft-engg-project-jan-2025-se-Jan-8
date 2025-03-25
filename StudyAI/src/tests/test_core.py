"""Unit tests for core functionality."""

import os
import sys
from unittest.mock import patch
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.core.base import BaseAgent
from src.core.state import StateManager


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
