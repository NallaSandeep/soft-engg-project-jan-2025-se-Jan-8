from flask import Flask, request, jsonify, abort
from flask_pymongo import PyMongo
import uuid
from datetime import datetime

app = Flask(__name__)

# Configure your MongoDB URI; adjust as needed.
app.config["MONGO_URI"] = "mongodb://localhost:27017/AgenticAI"
mongo = PyMongo(app)

@app.get("/")
async def root():
    return {"message": "Course Assistant API"}

if __name__ == '__main__':
    app.run(debug=True)