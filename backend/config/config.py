import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/AgenticAI")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")