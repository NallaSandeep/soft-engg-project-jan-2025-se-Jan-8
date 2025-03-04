from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field
from typing import Optional, List, Literal, Any

Base = declarative_base()


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True)
    message_id = Column(String(50), unique=True, default=lambda: str(uuid.uuid4()))
    message = Column(String(2000), nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    sender = Column(String(10), nullable=False)  # 'user' or 'bot'
    session_id = Column(
        String(50), ForeignKey("chat_sessions.session_id"), nullable=False
    )

    def __init__(self, message, sender, session_id):
        self.message_id = str(uuid.uuid4())
        self.message = message
        self.sender = sender
        self.session_id = session_id

    def to_dict(self):
        return {
            "message_id": self.message_id,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "sender": self.sender,
            "session_id": self.session_id,
        }


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True)
    session_id = Column(String(50), unique=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    name = Column(String(100), nullable=True)
    status = Column(String(20), default="active")
    is_bookmarked = Column(Boolean, default=False)

    def __init__(self, name=None, status="active", is_bookmarked=False):
        self.session_id = str(uuid.uuid4())
        self.name = name
        self.status = status
        self.is_bookmarked = is_bookmarked

    def to_dict(self):
        return {
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat(),
            "name": self.name,
            "status": self.status,
            "is_bookmarked": self.is_bookmarked,
        }


class ReportedResponse(Base):
    __tablename__ = "reported_responses"

    id = Column(Integer, primary_key=True)
    report_id = Column(String(50), unique=True, default=lambda: str(uuid.uuid4()))
    message_id = Column(String(50), ForeignKey("messages.message_id"), nullable=False)
    session_id = Column(
        String(50), ForeignKey("chat_sessions.session_id"), nullable=False
    )
    reason = Column(String(500), nullable=True)
    report_timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    status = Column(String(20), default="pending")  # pending, reviewed, dismissed

    def __init__(self, message_id, session_id, reason=None, status="pending"):
        self.report_id = str(uuid.uuid4())
        self.message_id = message_id
        self.session_id = session_id
        self.reason = reason
        self.status = status

    def to_dict(self):
        return {
            "report_id": self.report_id,
            "message_id": self.message_id,
            "session_id": self.session_id,
            "reason": self.reason,
            "report_timestamp": self.report_timestamp.isoformat(),
            "status": self.status,
        }


# Pydantic models for API
# .............................................................................................


class MessageCreate(BaseModel):
    message: str


class MessageResponse(BaseModel):
    message_id: str
    message: str
    timestamp: str
    sender: str
    session_id: str


class ChatSessionResponse(BaseModel):
    session_id: str
    created_at: str
    name: Optional[str] = None
    status: str
    is_bookmarked: bool

    class Config:
        from_attributes = True


# JSON Patch model
class JSONPatchOperation(BaseModel):
    op: Literal["replace", "add", "remove", "test", "move", "copy"]
    path: str
    value: Optional[Any] = None
    from_: Optional[str] = Field(None, alias="from")


# Replace SessionRename and SessionBookmark with JSONPatch
class SessionPatch(BaseModel):
    operations: List[JSONPatchOperation]


class ReportCreate(BaseModel):
    message_id: str
    reason: Optional[str] = None


class ReportResponse(BaseModel):
    report_id: str
    message_id: str
    session_id: str
    reason: Optional[str] = None
    report_timestamp: str
    status: str

    class Config:
        from_attributes = True


# Replace ReportUpdateStatus with JSONPatch
class ReportPatch(BaseModel):
    operations: List[JSONPatchOperation]
