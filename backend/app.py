from flask import Flask, jsonify, abort
from flask_pymongo import PyMongo
from backend.config.config import Config 

from backend.routes.chatbot_routes import chatbot_bp
import logging

app = Flask(__name__)

# Load configuration
app.config.from_object(Config)

# Configure logging
app.logger.addHandler(logging.StreamHandler())  # Log to console
app.logger.setLevel(logging.INFO)  # Set logging level to INFO

# Register blueprints
app.register_blueprint(chatbot_bp)

# Configure your MongoDB URI; adjust as needed.
app.config["MONGO_URI"] = "mongodb://localhost:27017/AgenticAI"

mongo = PyMongo(app)

@app.get("/")
async def root():
    return {"message": "Course Assistant API"}

if __name__ == '__main__':
    app.run(debug=True)