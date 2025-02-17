"""StudyIndexer service main application"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.core.logging import setup_logging
from app.core.errors import error_handler
from app.core.auth import AuthMiddleware
import os

# Set up logging
setup_logging()

# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="""
    StudyIndexer API - Document Processing and Semantic Search Service
    
    Features:
    * Document upload and processing (PDF, DOCX, TEXT, MARKDOWN)
    * Semantic search across documents
    * Course-specific document collections
    * Role-based access control
    * Document metadata management
    
    Authentication:
    * JWT-based authentication required for all endpoints
    * Role-specific access controls (admin, teacher, student)
    
    For more information, visit the documentation at /api/v1/docs
    """,
    version=settings.VERSION,
    docs_url=None,  # We'll mount these manually
    redoc_url=None,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    openapi_tags=[
        {
            "name": "admin",
            "description": "Administrative operations (admin only)"
        },
        {
            "name": "documents",
            "description": "Document management operations"
        },
        {
            "name": "search",
            "description": "Document search operations"
        }
    ]
)

# Mount static files for API documentation
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add error handling middleware
app.middleware("http")(error_handler)

# Add authentication middleware
app.middleware("http")(AuthMiddleware())

# Import and include routers
from app.api import router as api_router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Mount documentation endpoints
@app.get("/docs", include_in_schema=False)
@app.get(f"{settings.API_V1_STR}/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        title=f"{settings.PROJECT_NAME} - API Documentation",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui.css",
    )

@app.get("/redoc", include_in_schema=False)
@app.get(f"{settings.API_V1_STR}/redoc", include_in_schema=False)
async def redoc_html():
    return get_swagger_ui_html(
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        title=f"{settings.PROJECT_NAME} - API Documentation",
        redoc_js_url="https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js",
    )

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "running",
        "environment": settings.ENV,
        "documentation": f"{settings.API_V1_STR}/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "environment": settings.ENV
    } 