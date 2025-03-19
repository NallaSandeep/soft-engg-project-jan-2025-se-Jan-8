"""Tests for WebSocket functionality."""

import pytest
import asyncio
from fastapi.websockets import WebSocketDisconnect


class TestWebSocketAPI:
    """Tests for the WebSocket API endpoints."""

    def test_websocket_connection(self, client, test_session):
        """Test establishing a WebSocket connection."""
        session_id = test_session["session_id"]

        with client.websocket_connect(
            f"/stream/chat/session/{session_id}/message"
        ) as websocket:
            # Check for connection confirmation
            data = websocket.receive_json()
            assert data["type"] == "connected"
            assert data["session_id"] == session_id

    def test_websocket_send_message(self, client, test_session, mock_llm):
        """Test sending a message through WebSocket."""
        session_id = test_session["session_id"]

        with client.websocket_connect(
            f"/stream/chat/session/{session_id}/message"
        ) as websocket:
            # Skip connection confirmation
            websocket.receive_json()

            # Send a message
            websocket.send_json({"message": "Hello from WebSocket test"})

            # Check for processing start
            data = websocket.receive_json()
            assert data["type"] == "start"
            assert data["session_id"] == session_id

            # Receive response chunks until complete
            received_chunks = []
            complete_received = False

            # Set a timeout to prevent infinite loop
            start_time = asyncio.get_event_loop().time()
            timeout = 5  # seconds

            while not complete_received:
                # Check timeout
                if asyncio.get_event_loop().time() - start_time > timeout:
                    break

                data = websocket.receive_json()

                if data["type"] == "chunk":
                    received_chunks.append(data["content"])
                elif data["type"] == "complete":
                    complete_received = True
                elif data["type"] == "error":
                    pytest.fail(f"Received error: {data['content']}")

                # Break if we've received enough chunks for testing
                if len(received_chunks) >= 3 or complete_received:
                    break

            # Verify we received some response
            assert len(received_chunks) > 0 or complete_received

    def test_websocket_empty_message(self, client, test_session):
        """Test sending an empty message through WebSocket."""
        session_id = test_session["session_id"]

        with client.websocket_connect(
            f"/stream/chat/session/{session_id}/message"
        ) as websocket:
            # Skip connection confirmation
            websocket.receive_json()

            # Send an empty message
            websocket.send_json({"message": ""})

            # Check for error response
            data = websocket.receive_json()
            assert data["type"] == "error"
            assert "empty" in data["content"].lower()

    def test_websocket_invalid_json(self, client, test_session):
        """Test sending invalid JSON through WebSocket."""
        session_id = test_session["session_id"]

        with client.websocket_connect(
            f"/stream/chat/session/{session_id}/message"
        ) as websocket:
            # Skip connection confirmation
            websocket.receive_json()

            # Send invalid JSON
            websocket.send_text("This is not JSON")

            # Check for error response
            data = websocket.receive_json()
            assert data["type"] == "error"
            assert "json" in data["content"].lower()

    def test_websocket_nonexistent_session(self, client):
        """Test connecting to a non-existent session."""
        # This should fail with a 404 or similar
        with pytest.raises(WebSocketDisconnect):
            with client.websocket_connect(
                "/stream/chat/session/nonexistent-id/message"
            ):
                pass
