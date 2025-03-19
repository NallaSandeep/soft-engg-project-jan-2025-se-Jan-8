"""Integration tests for API endpoints."""

import pytest
from fastapi import status


class TestChatSessionAPI:
    """Tests for the chat session API endpoints."""

    def test_create_session(self, client):
        """Test creating a new chat session."""
        response = client.post("/chat/session")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert "session_id" in data
        assert "created_at" in data
        assert data["status"] == "active"
        assert data["is_bookmarked"] == False

    def test_get_session(self, client, test_session):
        """Test retrieving a chat session."""
        session_id = test_session["session_id"]

        response = client.get(f"/chat/session/{session_id}")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["session_id"] == session_id
        assert data["status"] == "active"

    def test_get_nonexistent_session(self, client):
        """Test retrieving a non-existent chat session."""
        response = client.get("/chat/session/nonexistent-id")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_list_sessions(self, client, test_session):
        """Test listing all chat sessions."""
        response = client.get("/chat/sessions")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

        # Check if our test session is in the list
        session_ids = [session["session_id"] for session in data]
        assert test_session["session_id"] in session_ids

    def test_update_session(self, client, test_session):
        """Test updating a chat session."""
        session_id = test_session["session_id"]

        # Update session name
        patch_data = {
            "operations": [
                {"op": "replace", "path": "/name", "value": "Test Session Name"}
            ]
        }

        response = client.patch(f"/chat/session/{session_id}", json=patch_data)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["name"] == "Test Session Name"

        # Update bookmark status
        patch_data = {
            "operations": [{"op": "replace", "path": "/is_bookmarked", "value": True}]
        }

        response = client.patch(f"/chat/session/{session_id}", json=patch_data)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["is_bookmarked"] == True

    def test_delete_session(self, client, test_session):
        """Test deleting a chat session."""
        session_id = test_session["session_id"]

        response = client.delete(f"/chat/session/{session_id}")
        assert response.status_code == status.HTTP_200_OK

        # Verify session is deleted
        response = client.get(f"/chat/session/{session_id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestMessageAPI:
    """Tests for the message API endpoints."""

    def test_get_messages(self, client, mock_data):
        """Test getting messages from an existing chat session."""
        # Get an existing session with messages
        if mock_data["sessions"] and mock_data["messages"]:
            session = mock_data["sessions"][0]
            session_id = session.session_id

            response = client.get(f"/chat/session/{session_id}/messages")
            assert response.status_code == status.HTTP_200_OK

            data = response.json()
            assert isinstance(data, list)
            assert len(data) > 0

            # Verify that the messages belong to the session
            for message in data:
                assert message["session_id"] == session_id

    @pytest.mark.parametrize(
        "message",
        [
            "Hello, how are you?",
            "Tell me about computer science",
            "What's the weather like today?",
        ],
    )
    def test_send_message(self, client, test_session, message):
        """Test sending a message to a chat session."""
        session_id = test_session["session_id"]

        response = client.post(
            f"/chat/session/{session_id}/message", json={"message": message}
        )
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["message"] == message
        assert data["session_id"] == session_id
        assert data["sender"] == "user"

        # Check that bot response was also created
        response = client.get(f"/chat/session/{session_id}/messages")
        assert response.status_code == status.HTTP_200_OK

        messages = response.json()
        assert len(messages) >= 2  # At least user message and bot response

        # Last message should be from bot
        assert messages[-1]["sender"] == "bot"

    def test_send_empty_message(self, client, test_session):
        """Test sending an empty message."""
        session_id = test_session["session_id"]

        response = client.post(
            f"/chat/session/{session_id}/message", json={"message": ""}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_send_message_to_nonexistent_session(self, client):
        """Test sending a message to a non-existent session."""
        response = client.post(
            "/chat/session/nonexistent-id/message", json={"message": "Hello"}
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestReportAPI:
    """Tests for the report API endpoints."""

    @staticmethod
    def verify_test_data(mock_data):
        """Verify that test data is properly set up."""
        assert mock_data is not None, "Mock data is None"
        assert "messages" in mock_data, "No messages in mock data"
        assert "sessions" in mock_data, "No sessions in mock data"

        bot_messages = [msg for msg in mock_data["messages"] if msg.sender == "bot"]
        assert len(bot_messages) > 0, "No bot messages available for testing"

        # Print available data for debugging
        print("\nAvailable test data:")
        print(f"Total messages: {len(mock_data['messages'])}")
        print(f"Bot messages: {len(bot_messages)}")
        print(f"Sessions: {len(mock_data['sessions'])}")
        print(f"Bot messages: {bot_messages[0]}")
        return bot_messages[0]

    def test_report_message(self, client, mock_data):
        """Test reporting a message."""
        # Verify test data
        bot_message = self.verify_test_data(mock_data)

        # Report the first bot message
        report_data = {
            "message_id": bot_message.message_id,
            "reason": "inappropriate_content",
        }

        print(f"\nAttempting to report message:")
        print(f"Message ID: {bot_message.message_id}")
        print(f"Session ID: {bot_message.session_id}")

        # The endpoint needs the /chat prefix as defined in the router
        response = client.post(
            f"/chat/report/{bot_message.session_id}", json=report_data
        )

        print(f"Response status: {response.status_code}")
        print(
            f"Response body: {response.json() if response.status_code != 404 else 'Not Found'}"
        )

        assert response.status_code == status.HTTP_200_OK, "Failed to create report"

    def test_list_reports(self, client, mock_data):
        """Test listing all reports."""
        response = client.get("/chat/reports")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert isinstance(data, list)

        # There should be at least the mock reports
        assert len(data) >= len(mock_data["reports"])

    def test_update_report_status(self, client, mock_data):
        """Test updating a report status."""
        # Use an existing report
        if mock_data["reports"]:
            report = mock_data["reports"][0]
            report_id = report.report_id

            # Update the report status
            patch_data = {
                "operations": [
                    {"op": "replace", "path": "/status", "value": "reviewed"}
                ]
            }

            response = client.patch(f"/chat/report/{report_id}", json=patch_data)
            assert response.status_code == status.HTTP_200_OK

            # Verify the update
            data = response.json()
            assert data["status"] == "reviewed"
            assert data["report_id"] == report_id
        else:
            pytest.skip("No reports available for testing")

    def test_create_report_invalid_session(self, client):
        """Test creating a report for an invalid session"""
        report_data = {
            "message_id": "test-message-id",
            "reason": "incorrect_information",
        }
        response = client.post("/chat/report/invalid-session-id", json=report_data)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_patch_report_invalid_status(self, client, mock_data):
        """Test updating a report with an invalid status"""
        # Use an existing report if available
        if mock_data["reports"]:
            report_id = mock_data["reports"][0].report_id

            # Try to update with invalid status
            patch_data = {
                "operations": [
                    {"op": "replace", "path": "/status", "value": "invalid_status"}
                ]
            }
            response = client.patch(f"/chat/report/{report_id}", json=patch_data)
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        else:
            pytest.skip("No reports available for testing")


class TestHealthAPI:
    """Tests for the health check API endpoint."""

    def test_health_check(self, client):
        """Test the health check endpoint."""
        response = client.get("/health")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert "status" in data
        assert "version" in data
        assert "timestamp" in data
