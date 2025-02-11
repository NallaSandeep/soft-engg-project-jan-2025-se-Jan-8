from flask import Blueprint, request, jsonify, abort
from backend.services import agent_service

agent_bp = Blueprint('agent', __name__, url_prefix='/api/agent')

@agent_bp.post('/ask')
def ask_question():
    data = request.get_json()
    result = agent_service.answer_question(data)
    if not result:
        abort(400, description="Question processing failed")
    return jsonify(result), 200

@agent_bp.get('/history/<userId>')
def get_history(userId):
    history = agent_service.get_history(userId)
    return jsonify({"userId": userId, "history": history}), 200

