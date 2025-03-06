from fastapi import HTTPException
from sqlalchemy.orm import Session
from src.models.db_models import (
    Message,
    ChatSession,
    ReportedResponse,
    JSONPatchOperation,
)
from typing import List
import logging


logger = logging.getLogger(__name__)


def create_new_session(db: Session):
    """Create a new chat session in the database."""
    try:
        chat_session = ChatSession()
        db.add(chat_session)
        db.commit()
        db.refresh(chat_session)
        return chat_session.to_dict()
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create new session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def add_message_to_session(
    db: Session, session_id: str, sender: str, message_text: str
):
    """Add a user message and a bot response to the database."""
    try:
        if sender in ["user", "bot"]:
            # Check if the session exists
            chat_session = (
                db.query(ChatSession)
                .filter(ChatSession.session_id == session_id)
                .first()
            )
            if not chat_session:
                raise HTTPException(status_code=404, detail="Session not found")

            # User message
            message = Message(
                message=message_text, sender=sender, session_id=session_id
            )
            db.add(message)
            db.commit()
        else:
            raise HTTPException(status_code=400, detail="Invalid sender type")

        return {"messsage_id": message.message_id}
    except Exception as e:
        db.rollback()
        logger.error(f"Database Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def get_session(db: Session, session_id: str):
    """Retrieve a chat session and its messages from the database."""
    try:
        chat_session = (
            db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
        )
        if not chat_session:
            return None

        messages = (
            db.query(Message)
            .filter(Message.session_id == session_id)
            .order_by(Message.timestamp)
            .all()
        )

        return {
            **chat_session.to_dict(),
            "messages": [message.to_dict() for message in messages],
        }
    except Exception as e:
        logger.error(f"Session retrieval error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def list_sessions(db: Session):
    """List all chat sessions with their messages from the database."""
    try:
        chat_sessions = db.query(ChatSession).all()
        results = []

        for chat_session in chat_sessions:
            messages = (
                db.query(Message)
                .filter(Message.session_id == chat_session.session_id)
                .order_by(Message.timestamp)
                .all()
            )
            results.append(
                {
                    **chat_session.to_dict(),
                    "messages": [message.to_dict() for message in messages],
                }
            )

        return results
    except Exception as e:
        logger.error(f"List sessions error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def delete_session(db: Session, session_id: str):
    """Delete a chat session and its messages."""
    try:
        # Delete all messages first due to foreign key constraint
        db.query(Message).filter(Message.session_id == session_id).delete()

        # Delete the session
        result = (
            db.query(ChatSession).filter(ChatSession.session_id == session_id).delete()
        )

        if result == 0:
            raise HTTPException(status_code=404, detail="Session not found")

        db.commit()
        return {"message": "Session deleted successfully"}
    except Exception as e:
        db.rollback()
        logger.error(f"Delete session error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def report_message(db: Session, message_id: str, session_id: str, reason: str = None):
    """Report an AI message for review."""
    try:
        # Check if the message exists
        message = (
            db.query(Message)
            .filter(
                Message.message_id == message_id,
                Message.session_id == session_id,
                Message.sender == "bot",  # Only bot messages can be reported
            )
            .first()
        )

        if not message:
            return None

        # Check if already reported
        existing_report = (
            db.query(ReportedResponse)
            .filter(ReportedResponse.message_id == message_id)
            .first()
        )

        if existing_report:
            return None  # Already reported

        # Create new report
        report = ReportedResponse(
            message_id=message_id, session_id=session_id, reason=reason
        )

        db.add(report)
        db.commit()
        db.refresh(report)

        return report.to_dict()

    except Exception as e:
        db.rollback()
        logger.error(f"Report message error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def get_reported_messages(db: Session):
    """Get all reported messages with their reports."""
    try:
        reports = db.query(ReportedResponse).all()
        results = []

        for report in reports:
            # Get the associated message
            message = (
                db.query(Message)
                .filter(Message.message_id == report.message_id)
                .first()
            )

            if message:
                report_dict = report.to_dict()
                report_dict["message"] = message.message
                results.append(report_dict)

        return results

    except Exception as e:
        logger.error(f"Get reported messages error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def apply_session_patch(
    db: Session, session_id: str, operations: List[JSONPatchOperation]
):
    """Apply JSON Patch operations to a chat session."""
    try:
        chat_session = (
            db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
        )
        if not chat_session:
            raise HTTPException(status_code=404, detail="Session not found")

        for op in operations:
            if op.op == "replace":
                if op.path == "/name":
                    chat_session.name = op.value
                elif op.path == "/is_bookmarked":
                    chat_session.is_bookmarked = op.value
                else:
                    raise HTTPException(
                        status_code=400, detail=f"Unsupported path: {op.path}"
                    )
            elif op.op == "test":
                # Test operation for validation
                if op.path == "/name" and chat_session.name != op.value:
                    raise HTTPException(status_code=409, detail="Test operation failed")
                elif (
                    op.path == "/is_bookmarked"
                    and chat_session.is_bookmarked != op.value
                ):
                    raise HTTPException(status_code=409, detail="Test operation failed")
            else:
                raise HTTPException(
                    status_code=400, detail=f"Unsupported operation: {op.op}"
                )

        db.commit()
        return chat_session.to_dict()
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Patch session error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def apply_report_patch(
    db: Session, report_id: str, operations: List[JSONPatchOperation]
):
    """Apply JSON Patch operations to a report."""
    try:
        report = (
            db.query(ReportedResponse)
            .filter(ReportedResponse.report_id == report_id)
            .first()
        )

        if not report:
            raise HTTPException(status_code=404, detail="Report not found")

        for op in operations:
            if op.op == "replace":
                if op.path == "/status":
                    # Validate status
                    valid_statuses = ["pending", "reviewed", "dismissed"]
                    if op.value not in valid_statuses:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}",
                        )
                    report.status = op.value
                else:
                    raise HTTPException(
                        status_code=400, detail=f"Unsupported path: {op.path}"
                    )
            elif op.op == "test":
                if op.path == "/status" and report.status != op.value:
                    raise HTTPException(status_code=409, detail="Test operation failed")
            else:
                raise HTTPException(
                    status_code=400, detail=f"Unsupported operation: {op.op}"
                )

        db.commit()
        db.refresh(report)

        # Return updated report with message
        message = (
            db.query(Message).filter(Message.message_id == report.message_id).first()
        )

        report_dict = report.to_dict()
        if message:
            report_dict["message"] = message.message

        return report_dict

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Update report status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
