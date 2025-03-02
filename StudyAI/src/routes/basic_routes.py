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
)
from typing import List


router = APIRouter(prefix="/chat")


@router.post("/session", response_model=ChatSessionResponse)
async def create_session(db: Session = Depends(get_db)):
    return create_new_session(db)


@router.post("/session/{session_id}/message")
async def post_message(
    session_id: str, message_data: MessageCreate, db: Session = Depends(get_db)
):
    response = await process_message(session_id, message_data.message)
    return response


@router.get("/session/{session_id}", response_model=ChatSessionResponse)
async def get_chat_session(session_id: str, db: Session = Depends(get_db)):
    session_data = get_session(db, session_id)
    if not session_data:
        raise HTTPException(status_code=404, detail="Session not found")
    return session_data


@router.get("/sessions", response_model=List[ChatSessionResponse])
async def get_all_sessions(db: Session = Depends(get_db)):
    return list_sessions(db)


@router.patch("/session/{session_id}", response_model=ChatSessionResponse)
async def patch_session(
    session_id: str, patch_data: SessionPatch, db: Session = Depends(get_db)
):
    """Update a session using JSON Patch operations."""
    return apply_session_patch(db, session_id, patch_data.operations)


@router.delete("/session/{session_id}")
async def remove_session(session_id: str, db: Session = Depends(get_db)):
    return delete_session(db, session_id)


@router.post("/report/{session_id}", response_model=ReportResponse)
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


@router.get("/reports", response_model=List[ReportResponse])
async def get_reports(db: Session = Depends(get_db)):
    """Get all reported AI responses."""
    return get_reported_messages(db)


@router.patch("/report/{report_id}", response_model=ReportResponse)
async def patch_report(
    report_id: str, patch_data: ReportPatch, db: Session = Depends(get_db)
):
    """Update a report using JSON Patch operations."""
    return apply_report_patch(db, report_id, patch_data.operations)
