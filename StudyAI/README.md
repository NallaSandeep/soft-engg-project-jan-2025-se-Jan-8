# StudyAI Service

AI-powered study agent assistance component for the StudyHub platform. This service leverages Google's Gemini API and LangChain for providing personalized learning experiences.

## Features

- AI-powered study assistance 
- Content recommendations
- Learning path optimization
- Personalized tutoring

## Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- Google AI Studio account (for Gemini API)
- LangSmith account (for LangChain observability)

## Installation

1. Clone the repository:
   ```bash
    git clone https://github.com/NallaSandeep/soft-engg-project-jan-2025-se-Jan-8.git
    cd studyai
   ```

2. Create a virtual environment:
   ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv/Scripts/activate
   ```

3. Install dependencies:
   ```bash
    pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   ```

4. Configure the `.env` file with your API keys (see API Key Setup section below)

5. Start the development server:
   ```bash
    python app.py
    # or
    uvicorn app:app --reload
   ```

## API Key Setup

### Google Gemini API

1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Create a google studio account(use personal email id) if you don't have one
3. Generate an API key from the home page
4. Add the API key to your `.env` file:

   ```
   GEMINI_API_KEY=your_api_key_here
   ```

### LangSmith API

1. Create an account at [LangSmith](https://smith.langchain.com/)
2. Navigate to the API Keys section in your account settings
3. Create a new API key
4. Add the API key to your `.env` file:

   ```
   LANGCHAIN_API_KEY=your_api_key_here
   LANGCHAIN_PROJECT=your_project_name
   LANGSMITH_TRACING_V2=true
   ```

## Usage

After installation, you can access:

- API server at `http://127.0.0.1:8000`
- Swagger API docs UI at `http://127.0.0.1:8000/`
- Health check endpoint at `http://127.0.0.1:8000/health`

## API Endpoints
### Chat Endpoints

- `POST /chat/session` - Create a new chat session
- `GET /chat/session`s - List all chat sessions
- `GET /chat/session/{session_id}` - Get a specific session
- `POST /chat/session/{session_id}/message` - Send a message
- `DELETE /chat/session/{session_id}` - Delete a session

Check routes for more details.


### Websocket Streaming

- `ws://localhost:8000/stream/chat/session/{session_id}` - Real-time chat streaming


> **Note:** `POST /chat/session/{session_id}/message` will not work, use websocket for testing. It was created for testing purposes. Later it wiil be removed.

## Development

- Run tests: `pytest`
- Format code: `black.`

## Project Structure

```bash
studyai/
├── app.py              # FastAPI application entry point
├── config.py           # Configuration management
├── requirements.txt    # Python dependencies
├── src/
│   ├── core/           # Core components (agents, workflow)
│   ├── database.py     # Database connection
│   ├── models/         # Data models (Pydantic & SQLAlchemy)
│   ├── modules/        # Agent modules
│   ├── routes/         # API routes
│   └── services/       # Business logic
```

Currently in active development. Stay tuned for updates!
