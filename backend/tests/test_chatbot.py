import unittest
from backend.app import app
import json

class ChatBotAPITestCase(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        # Use a test database to avoid interfering with production data.
        app.config["MONGO_URI"] = "mongodb://localhost:27017/test_AgenticAI"
        self.client = app.test_client()
        with app.app_context():
            db = app.extensions['pymongo'].db
            db.sessions.delete_many({})

    def test_create_session(self):
        response = self.client.post("/chat/session")
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertIn("session_id", data)
        self.session_id = data["session_id"]

    def test_post_and_get_message(self):
        # Create a new session.
        response = self.client.post("/chat/session")
        data = json.loads(response.data)
        session_id = data["session_id"]

        # Add a new message.
        message_payload = {"session_id": session_id, "message": "Hello"}
        response = self.client.post("/chat/message", json=message_payload)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertIn("message_id", data)

        # Retrieve the session.
        response = self.client.get(f"/chat/session/{session_id}")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["session_id"], session_id)
        self.assertEqual(len(data["messages"]), 1)
        self.assertEqual(data["messages"][0]["message"], "Hello")

    def test_list_sessions(self):
        # Create a session.
        self.client.post("/chat/session")
        # List all sessions.
        response = self.client.get("/chat/sessions")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)

if __name__ == '__main__':
    unittest.main()