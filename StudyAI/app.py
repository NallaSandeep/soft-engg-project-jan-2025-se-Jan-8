"""Application entry point for StudyAI API."""

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
from datetime import datetime
from typing import Dict, Any, Callable
import logging
import time
import uvicorn
from contextlib import asynccontextmanager

# Import LangChain cache modules
from langchain_community.cache import InMemoryCache
from langchain.globals import set_llm_cache

from src.routes.basic_routes import router as chatbot_router
from src.routes.websocket_routes import router as websocket_router
from src.services.websocket_services import disconnect_all_clients
from src.database import init_db
from config import Config

logger = logging.getLogger(__name__)

# ...............................................................................................


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application lifespan events."""
    # Startup logic
    config_status = Config.validate_config()
    if not all(config_status.values()):
        missing_vars = [var for var, status in config_status.items() if not status]
        logger.warning(f"Missing configuration: {missing_vars}")

    # Initialize LangChain cache if enabled
    if Config.ENABLE_LANGCHAIN_CACHE:
        try:
            set_llm_cache(InMemoryCache())
            logger.info("LangChain cache initialized with InMemoryCache")
        except Exception as e:
            logger.warning(f"Failed to initialize LangChain cache: {e}")

    logger.info("StudyAI API started successfully")

    yield  # Application runs here

    # Shutdown logic
    logger.info("StudyAI API shutting down")
    await disconnect_all_clients() 
    logger.info("WebSocket connections closed")

# .......................................................................................................



def create_application() -> FastAPI:
    """Create and configure FastAPI application."""

    init_db()

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
        description="StudyAI: Agentic AI course assistant API",
        version="1.0.0",
        openapi_tags=tags_metadata,
        servers=[
            {
                "url": f"http://{Config.HOST}:{Config.PORT}",
                "description": "Development server",
            },
        ],
        lifespan=lifespan,
    )

    # Configure middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=Config.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
        allow_headers=["*"],
    )
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    # Configure rate limiting
    if Config.RATE_LIMIT_ENABLED:
        limiter = Limiter(key_func=get_remote_address)
        app.state.limiter = limiter
        app.add_middleware(SlowAPIMiddleware)

        @app.exception_handler(RateLimitExceeded)
        async def rate_limit_handler(
            request: Request, exc: RateLimitExceeded
        ) -> JSONResponse:
            return JSONResponse(
                status_code=429,
                content={"error": "Rate limit exceeded", "detail": str(exc)},
            )

    @app.middleware("http")
    async def add_process_time_header(
        request: Request, call_next: Callable
    ) -> Response:
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response

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

    @app.get("/health", tags=["System"])
    async def health_check() -> Dict[str, Any]:
        """System health check endpoint."""
        config_valid = Config.is_valid()
        return {
            "status": "healthy" if config_valid else "degraded",
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat(),
            "config_status": "valid" if config_valid else "invalid",
            "database_status": "connected",
        }

    return app

# ...............................................................................


app = create_application()

if __name__ == "__main__":
    uvicorn.run(app, host=Config.HOST, port=Config.PORT)
