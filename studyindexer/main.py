import os
import uvicorn
import traceback
import logging
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.faq import router as faq_router
from app.api.health import router as health_router
from app.api.course_selector import router as course_selector_router
from app.api.course_content import router as course_content_router
from app.api.personal_resource import router as personal_resource_router
from app.api.integrity_check import router as integrity_check_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/app_errors.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("app")

app = FastAPI(
    title="StudyIndexerNew",
    description="Vector database system for educational content",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development - restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_exceptions(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        logger.error(f"Request to {request.url} failed: {str(e)}")
        logger.error(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={"detail": f"Error processing request: {str(e)}"}
        )

@app.get("/")
async def root():
    return {"message": "Welcome to StudyIndexerNew API"}

@app.get("/health")
@app.get("/api/health")  # Add the path expected by service manager
async def health_check():
    return {"status": "healthy"}

# Include routers
app.include_router(health_router, prefix="/api/health", tags=["Health"])
app.include_router(faq_router, prefix="/api/v1/faq", tags=["FAQ"])
app.include_router(course_selector_router, prefix="/api/v1/course-selector", tags=["Course Selector"])
app.include_router(course_content_router, prefix="/api/v1/course-content", tags=["Course Content"])
app.include_router(personal_resource_router, prefix="/api/v1/personal-resource", tags=["Personal Resource"])
# app.include_router(course_guide_router, prefix="/api/v1/course-guide", tags=["Course Guide"])
app.include_router(integrity_check_router, prefix="/api/v1/integrity-check", tags=["Integrity Check"])

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True) 