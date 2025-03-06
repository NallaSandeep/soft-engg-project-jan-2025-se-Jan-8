from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.routes.basic_routes import router as chatbot_router
from src.routes.websocket_routes import router as websocket_router
from src.models.db_models import Base
from fastapi.openapi.docs import get_swagger_ui_html
from src.database import engine
import uvicorn
from datetime import datetime
import logging

# Create database tables (if they don't exist)
Base.metadata.create_all(bind=engine)

# Metadata for API documentation
tags_metadata = [
    {
        "name": "Chat Session",
        "description": "Operations for managing chat sessions, including creating, retrieving, and deleting sessions, as well as sending messages.",
    },
    {
        "name": "Stream Chat",
        "description": """<p>WebSocket endpoints <strong>(stream/chat/session/{session_id}/message)</strong> for real-time, streaming chat communication.</p>
        <p><strong>Note:</strong> WebSocket connections cannot be tested directly through Swagger UI. 
        Please use a WebSocket client or implement the WebSocket connection in your application.</p>""",
    },
    {
        "name": "Report AI",
        "description": "Operations for reporting and managing inappropriate or incorrect AI responses.",
    },
    {
        "name": "System",
        "description": "System-level operations including health checks and service status.",
    },
]

app = FastAPI(
    title="StudyAI API",
    description="<p><strong>StudyAI:</strong> This microservice contains all APIs for interacting with an <strong>Agentic AI</strong> course assistant. You can leverage <strong>Websocket API</strong> for streaming the chat. It also includes features to report AI responses for <strong>course team/admin</strong> review.</p>",
    version="1.0.0",
    openapi_tags=tags_metadata,
    servers=[
        {"url": "http://127.0.0.1:5000", "description": "Development server"},
    ],
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Include routers
app.include_router(chatbot_router)
app.include_router(websocket_router)


@app.get("/", include_in_schema=False)
async def custom_swagger_ui():
    """Redirect root to custom Swagger UI."""
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="Course Assistant API Documentation",
        swagger_ui_parameters={
            "defaultModelsExpandDepth": -1,
            "docExpansion": "none",
            "filter": True,
            "displayRequestDuration": True,
            "tagsSorter": "alpha",
            "operationsSorter": "alpha",
        },
    )


@app.get(
    "/health",
    tags=["System"],
    summary="System Health Check",
    description="Check the health status of the service including version and current timestamp",
    response_description="Returns the current system status",
)
async def health_check():
    """
    Perform a health check of the system.

    Returns:
        dict: A dictionary containing the system status
    """
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
    }


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5000)
