from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import course_content, course_selector, personal_resource, faq

app = FastAPI(
    title="StudyIndexer API",
    description="API for managing and searching course content",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Include routers
app.include_router(course_content.router, prefix="/api/v1/course-content", tags=["Course Content"])
app.include_router(course_selector.router, prefix="/api/v1/course-selector", tags=["Course Selector"])
app.include_router(personal_resource.router, prefix="/api/v1/personal-resources", tags=["Personal Resources"])
app.include_router(faq.router, prefix="/api/v1/faq", tags=["FAQ"])

@app.get("/")
async def root():
    return {"message": "Welcome to StudyIndexer API"} 