from fastapi import (
    APIRouter,
    WebSocket,
    WebSocketDisconnect,
    Depends,
    Query,
    HTTPException,
)
from sqlalchemy.orm import Session
from src.database import get_db
from src.services.websocket_services import (
    connect,
    disconnect,
    process_and_stream_message,
)
import logging
import json
from typing import Optional

router = APIRouter(prefix="/stream", tags=["Stream Chat"])
logger = logging.getLogger(__name__)


@router.websocket(
    "/chat/session/{session_id}/message",
    name="Stream Chat Messages",
)
async def websocket_stream_endpoint(
    websocket: WebSocket,
    session_id: str,
    db: Session = Depends(get_db),
):
    """
    WebSocket endpoint for streaming chat responses.

    Establishes a persistent connection allowing for real-time communication.
    The AI will stream responses token by token as they are generated.

    Args:
        websocket (WebSocket): The WebSocket connection
        session_id (str): Session ID for existing conversations
        db (Session): Database session
    """
    try:
        # Accept the connection and get session ID
        session_id = await connect(websocket, session_id)
        logger.info(f"New WebSocket connection established: {session_id}")

        while True:
            try:
                # Wait for incoming message
                data = await websocket.receive_text()

                # Validate message format
                if not data:
                    await websocket.send_json(
                        {"type": "error", "content": "Empty message received"}
                    )
                    continue

                # Parse message
                message_data = json.loads(data)
                user_message = message_data.get("message", "").strip()

                # Validate message content
                if not user_message:
                    await websocket.send_json(
                        {"type": "error", "content": "Message content cannot be empty"}
                    )
                    continue

                # Process message with streaming
                await process_and_stream_message(
                    websocket=websocket, session_id=session_id, message=user_message
                )

            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {e}")
                await websocket.send_json(
                    {
                        "type": "error",
                        "content": "Invalid message format - expecting JSON",
                    }
                )
            except Exception as e:
                logger.error(f"Error processing message: {str(e)}")
                await websocket.send_json(
                    {"type": "error", "content": "Internal server error"}
                )

    except WebSocketDisconnect:
        disconnect(session_id)
        logger.info(f"WebSocket client disconnected: {session_id}")
    except Exception as e:
        logger.error(f"WebSocket connection error: {str(e)}")
        await websocket.close(code=1011)  # Internal Server Error
        disconnect(session_id)
