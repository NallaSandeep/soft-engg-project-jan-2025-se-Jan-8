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

app = FastAPI(title="Course Assistant API")

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
        },
    )


# Add tags metadata for better organization
tags_metadata = [
    {
        "name": "chat",
        "description": "Operations with chat sessions and messages",
    },
    {
        "name": "websocket",
        "description": "Real-time chat communication",
    },
]


@app.get(
    "/health",
    tags=["system"],
    summary="System Health Check",
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
    uvicorn.run(app, host="127.0.0.1", port=8000)
