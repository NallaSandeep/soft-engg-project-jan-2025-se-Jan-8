from pydantic import BaseModel
from typing import Optional, List, Dict, Any, Union


class ChatMessage(BaseModel):
    """Message sent by the client to the server."""

    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    """Response sent from server to client."""

    type: str  # "message", "chunk", "error", "connected", "complete"
    content: Optional[str] = None
    session_id: str
