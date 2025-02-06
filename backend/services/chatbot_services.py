from flask import current_app
from datetime import datetime
import uuid
from backend.models.chat_session import ChatSession, Message
import google.generativeai as genai
from flask import current_app

def create_new_session():
    chat_session = ChatSession()
    db = current_app.extensions['pymongo'].db
    db.sessions.insert_one(chat_session.to_dict())
    return chat_session.to_dict()


def generate_bot_response(user_message):
    try:
        # Configure the Gemini API key
        genai.configure(api_key=current_app.config['GEMINI_API_KEY'])
        
        # Initialize the Gemini model
        model = genai.GenerativeModel(
            model="gemini-2.0-flash-exp",
            temperature=0.1
        )
        response = model.generate_content(user_message)
        return response.text
    except Exception as e:
        current_app.logger.error(f"LLM Error: {e}")
        return "I'm unable to respond right now. Please try again later."
    
    

def add_message_to_session(session_id, message_text):
    db = current_app.extensions['pymongo'].db
    
    # Add user message
    user_message = Message(message=message_text, sender="user")
    user_update = db.sessions.update_one(
        {"session_id": session_id},
        {"$push": {"messages": user_message.to_dict()}}
    )
    if user_update.modified_count == 0:
        return None
    
    # Generate and add bot response
    bot_response = generate_bot_response(message_text)
    bot_message = Message(message=bot_response, sender="bot")
    db.sessions.update_one(
        {"session_id": session_id},
        {"$push": {"messages": bot_message.to_dict()}}
    )
    return user_message.message_id

def get_session(session_id):
    db = current_app.extensions['pymongo'].db
    session = db.sessions.find_one({"session_id": session_id}, {"_id": 0})
    return session

def list_sessions():
    db = current_app.extensions['pymongo'].db
    sessions = list(db.sessions.find({}, {"_id": 0}))
    return sessions