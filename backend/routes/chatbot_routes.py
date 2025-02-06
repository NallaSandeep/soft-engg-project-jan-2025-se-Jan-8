from flask import Blueprint, request, jsonify, abort
from backend.services import chatbot_service

chatbot_bp = Blueprint('chatbot', __name__, url_prefix='/chat')

# Create a new chat session
@chatbot_bp.post("/session")
async def create_session():
    session = chatbot_service.create_new_session()
    return jsonify({"session_id": session["session_id"]}), 201

# Add a new message to a chat session
@chatbot_bp.post("/message")
async def post_message():
    data = request.get_json()
    session_id = data.get("session_id")
    message_text = data.get("message")
    if not session_id or not message_text:
        abort(400, description="session_id and message are required")
    message_id = chatbot_service.add_message_to_session(session_id, message_text)
    if not message_id:
        abort(404, description="Session not found")
    return jsonify({"message": "Message added", "message_id": message_id}), 201

@chatbot_bp.get("/session/<session_id>")
async def get_session(session_id):
    session = chatbot_service.get_session(session_id)
    if not session:
        abort(404, description="Session not found")
    return jsonify(session), 200

@chatbot_bp.get("/sessions")
async def list_sessions():
    sessions = chatbot_service.list_sessions()
    return jsonify(sessions), 200