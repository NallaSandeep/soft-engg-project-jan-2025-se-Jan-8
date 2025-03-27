from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from src.database import get_db
from src.services.basic_services import (
    create_new_session,
    add_message_to_session,
    get_session,
    list_sessions,
    apply_session_patch,
    apply_report_patch,
    delete_session,
    report_message,
    get_reported_messages,
)
from src.services.workflow_services import process_message
from src.models.db_models import (
    MessageCreate,
    MessageResponse,
    ChatSessionResponse,
    SessionPatch,
    ReportCreate,
    ReportResponse,
    ReportPatch,
    UserCreate,
    UserResponse,
)
from typing import List


router = APIRouter(prefix="/chat")


@router.post(
    "/session",
    response_model=ChatSessionResponse,
    tags=["Chat Session"],
    summary="Create New Chat Session",
    description="Creates a new chat session and returns its identifier. If user_id is provided and user doesn't exist, creates new user with metadata.",
)
async def create_session(
    user_id: str = None, metadata: dict = None, db: Session = Depends(get_db)
):
    return create_new_session(db, user_id, metadata)


# @router.post(
#     "/session/{session_id}/message",
#     tags=["Chat Session"],
#     summary="Send Message to Chat Session",
#     description="Sends a message to the specified chat session and returns the AI response",
# )
# async def post_message(
#     session_id: str, message_data: MessageCreate, db: Session = Depends(get_db)
# ):
#     response = await process_message(session_id, message_data.message)
#     return response


@router.get(
    "/session/{session_id}",
    response_model=ChatSessionResponse,
    tags=["Chat Session"],
    summary="Get Chat Session",
    description="Retrieves a specific chat session by its ID including all messages",
)
async def get_chat_session(session_id: str, db: Session = Depends(get_db)):
    session_data = get_session(db, session_id)
    if not session_data:
        raise HTTPException(status_code=404, detail="Session not found")
    return session_data


@router.get(
    "/sessions",
    response_model=List[ChatSessionResponse],
    tags=["Chat Session"],
    summary="List All Chat Sessions",
    description="Returns a list of all available chat sessions",
)
async def get_all_sessions(user_id: str = None, db: Session = Depends(get_db)):
    return list_sessions(db, user_id)


@router.patch(
    "/session/{session_id}",
    response_model=ChatSessionResponse,
    tags=["Chat Session"],
    summary="Update Chat Session",
    description="Updates a chat session using JSON Patch operations",
)
async def patch_session(
    session_id: str, patch_data: SessionPatch, db: Session = Depends(get_db)
):
    """Update a session using JSON Patch operations."""
    return apply_session_patch(db, session_id, patch_data.operations)


@router.delete(
    "/session/{session_id}",
    tags=["Chat Session"],
    summary="Delete Chat Session",
    description="Permanently removes a chat session and all its messages",
)
async def remove_session(session_id: str, db: Session = Depends(get_db)):
    return delete_session(db, session_id)


@router.post(
    "/report/{session_id}",
    response_model=ReportResponse,
    tags=["Report AI"],
    summary="Report AI Response",
    description="Reports an inappropriate or incorrect AI response for review",
)
async def report_ai_response(
    session_id: str, report_data: ReportCreate, db: Session = Depends(get_db)
):
    """Report an inappropriate or incorrect AI response."""
    result = report_message(db, report_data.message_id, session_id, report_data.reason)
    if not result:
        raise HTTPException(
            status_code=404, detail="Message not found or already reported"
        )
    return result


@router.get(
    "/reports",
    response_model=List[ReportResponse],
    tags=["Report AI"],
    summary="List All Reports",
    description="Returns a list of all reported AI responses",
)
async def get_reports(db: Session = Depends(get_db)):
    """Get all reported AI responses."""
    return get_reported_messages(db)


@router.patch(
    "/report/{report_id}",
    response_model=ReportResponse,
    tags=["Report AI"],
    summary="Update Report Status",
    description="Updates a report's status using JSON Patch operations",
)
async def patch_report(
    report_id: str, patch_data: ReportPatch, db: Session = Depends(get_db)
):
    """Update a report using JSON Patch operations."""
    return apply_report_patch(db, report_id, patch_data.operations)
