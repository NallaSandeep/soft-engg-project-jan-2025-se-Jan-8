"""StudyIndexer service main application."""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import os
from pathlib import Path

from app.core.logging import setup_logging
from app.core.config import settings
from app.core.auth import AuthMiddleware
from app.core.errors import error_handler, StudyIndexerError
from app.core.middleware import RequestLoggingMiddleware

# Setup logging first
setup_logging()

# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="""
    StudyIndexer API provides document indexing and semantic search capabilities.
    
    Features:
    * Document upload and processing
    * Semantic search across documents
    * Role-based access control
    * JWT-based authentication
    """,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    openapi_tags=[
        {
            "name": "admin",
            "description": "Administrative operations"
        },
        {
            "name": "documents",
            "description": "Document management operations"
        },
        {
            "name": "search",
            "description": "Search operations"
        }
    ]
)

# Mount static files for API documentation
static_dir = Path("static")
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add request logging middleware
app.add_middleware(RequestLoggingMiddleware)

# Add error handling middleware
app.middleware("http")(error_handler)

# Add authentication middleware
app.middleware("http")(AuthMiddleware())

# Import and include routers
from app.api import router as api_router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Mount documentation endpoints
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """Custom Swagger UI HTML response"""
    return HTMLResponse(
        """
        <!DOCTYPE html>
        <html>
        <head>
            <title>StudyIndexer API - Documentation</title>
            <meta charset="utf-8"/>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <link rel="stylesheet" type="text/css" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css" />
            <style>
                body { margin: 0; padding: 0; }
                .swagger-ui .topbar { display: none; }
            </style>
        </head>
        <body>
            <div id="swagger-ui"></div>
            <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
            <script>
                window.onload = function() {
                    window.ui = SwaggerUIBundle({
                        url: "/api/v1/openapi.json",
                        dom_id: '#swagger-ui',
                        deepLinking: true,
                        presets: [
                            SwaggerUIBundle.presets.apis,
                            SwaggerUIBundle.SwaggerUIStandalonePreset
                        ],
                        layout: "BaseLayout",
                        requestInterceptor: (request) => {
                            // Add API key if available
                            const apiKey = localStorage.getItem('api_key');
                            if (apiKey) {
                                request.headers['X-API-Key'] = apiKey;
                            }
                            return request;
                        }
                    });
                };
            </script>
        </body>
        </html>
        """
    )

@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    """ReDoc HTML response"""
    return HTMLResponse(
        """
        <!DOCTYPE html>
        <html>
        <head>
            <title>StudyIndexer API - ReDoc</title>
            <meta charset="utf-8"/>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <link href="https://fonts.googleapis.com/css?family=Montserrat:300,400,700|Roboto:300,400,700" rel="stylesheet">
            <style>
                body { margin: 0; padding: 0; }
            </style>
        </head>
        <body>
            <redoc spec-url="/api/v1/openapi.json"></redoc>
            <script src="https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js"></script>
        </body>
        </html>
        """
    )

@app.get("/")
async def root():
    """Root endpoint"""
    return JSONResponse({
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "running",
        "environment": settings.ENV,
        "docs": "/docs",
        "explorer": "/explorer"
    })

@app.get("/explorer", include_in_schema=False)
async def api_explorer():
    """API Explorer page"""
    try:
        # Use the app/static directory path
        file_path = os.path.join(os.path.dirname(__file__), "static", "explorer.html")
        with open(file_path, "r") as f:
            content = f.read()
        return HTMLResponse(content)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "Error loading explorer page",
                "error": {
                    "code": "EXPLORER_ERROR",
                    "details": {"error": str(e)}
                }
            }
        )

@app.post("/debug/token", include_in_schema=False)
async def debug_token(request: Request):
    """Debug endpoint for JWT token validation"""
    try:
        data = await request.json()
        token = data.get("token", "")
        
        if not token:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "message": "No token provided",
                    "error": {
                        "code": "TOKEN_ERROR",
                        "details": None
                    }
                }
            )
        
        # Try to decode the token without verification first to show what's in it
        import base64
        import json
        
        # Split the token
        parts = token.split(".")
        if len(parts) != 3:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "message": "Invalid token format",
                    "error": {
                        "code": "TOKEN_ERROR",
                        "details": {"error": "Token should have 3 parts (header.payload.signature)"}
                    }
                }
            )
        
        # Decode header and payload
        try:
            header_str = base64.b64decode(parts[0] + "=" * ((4 - len(parts[0]) % 4) % 4)).decode('utf-8')
            header = json.loads(header_str)
        except Exception as e:
            header = {"error": str(e)}
            
        try:
            payload_str = base64.b64decode(parts[1] + "=" * ((4 - len(parts[1]) % 4) % 4)).decode('utf-8')
            payload = json.loads(payload_str)
        except Exception as e:
            payload = {"error": str(e)}
        
        # Now try to verify the token
        from jose import jwt, JWTError
        from app.core.config import settings
        
        verification_result = {"success": False, "error": None}
        try:
            verified_payload = jwt.decode(
                token,
                settings.JWT_SECRET,
                algorithms=[settings.JWT_ALGORITHM]
            )
            verification_result = {"success": True, "payload": verified_payload}
        except JWTError as e:
            verification_result = {"success": False, "error": str(e)}
        except Exception as e:
            verification_result = {"success": False, "error": f"Unexpected error: {str(e)}"}
        
        return JSONResponse({
            "success": True,
            "token_info": {
                "header": header,
                "payload": payload,
                "verification": verification_result,
                "app_settings": {
                    "algorithm": settings.JWT_ALGORITHM,
                    "secret_key_length": len(settings.JWT_SECRET)
                }
            }
        })
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "Error debugging token",
                "error": {
                    "code": "DEBUG_ERROR",
                    "details": {"error": str(e)}
                }
            }
        )

@app.get(settings.FASTAPI_HEALTH_ENDPOINT)
async def health():
    """Health check endpoint"""
    return JSONResponse({
        "status": "healthy",
        "version": settings.VERSION,
        "environment": settings.ENV
    }) 