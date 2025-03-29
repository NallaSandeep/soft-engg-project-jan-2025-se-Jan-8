import json
import logging

from fastapi import (
    APIRouter,
    Depends,
    WebSocket,
    WebSocketDisconnect,
)
from sqlalchemy.orm import Session

from src.database import get_db
from src.services.basic_services import add_message_to_session
from src.services.websocket_services import (
    connect,
    disconnect,
    process_and_stream_message,
    safe_send_json,
    is_connected,
)

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
                data = await websocket.receive_text()  # Wait for incoming message

                # Validate message format
                if not data:
                    await safe_send_json(
                        websocket,
                        {"type": "error", "content": "Empty message received"},
                        session_id,
                    )
                    continue

                # Parse message
                message_data = json.loads(data)
                user_message = message_data.get("message", "").strip()

                # Validate message content
                if not user_message:
                    await safe_send_json(
                        websocket,
                        {"type": "error", "content": "Message content cannot be empty"},
                        session_id,
                    )
                    continue

                # Add user message to session in the database
                add_message_to_session(db, session_id, "user", user_message)

                # Process message with streaming
                await process_and_stream_message(
                    websocket=websocket,
                    session_id=session_id,
                    message=user_message,
                    db=db,
                )

            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {e}")
                if is_connected(websocket):
                    await safe_send_json(
                        websocket,
                        {
                            "type": "error",
                            "content": "Invalid message format - expecting JSON",
                        },
                        session_id,
                    )
            except WebSocketDisconnect:
                # Handle disconnection inside the inner loop
                logger.info(
                    f"Client disconnected during message processing: {session_id}"
                )
                disconnect(session_id)
                return  # Exit the handler
            except Exception as e:
                logger.error(f"Error processing message: {str(e)}")
                if is_connected(websocket):
                    await safe_send_json(
                        websocket,
                        {"type": "error", "content": "Internal server error"},
                        session_id,
                    )

    except WebSocketDisconnect:
        logger.info(f"WebSocket client disconnected: {session_id}")
        disconnect(session_id)
    except Exception as e:
        logger.error(f"WebSocket connection error: {str(e)}")
        # Only try to close if not already closed
        if is_connected(websocket):
            try:
                await websocket.close(code=1011)  # Internal Server Error
            except Exception:
                pass  # Already closed, ignore
        disconnect(session_id)
