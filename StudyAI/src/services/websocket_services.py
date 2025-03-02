import logging
import json
import uuid
from typing import Dict, Any, Optional
from fastapi import WebSocket
from fastapi.websockets import WebSocketState
from src.services.workflow_services import process_message_stream

logger = logging.getLogger(__name__)

# Store active WebSocket connections by session_id
active_connections: Dict[str, WebSocket] = {}


async def connect(websocket: WebSocket, session_id: Optional[str] = None) -> str:
    """
    Connect a WebSocket client and return the session ID.

    Args:
        websocket (WebSocket): The WebSocket connection
        session_id (Optional[str]): The session identifier or None to generate a new one

    Returns:
        str: Session ID for the connection
    """
    await websocket.accept()

    # Generate a new session ID if none is provided
    if not session_id:
        session_id = str(uuid.uuid4())

    # Store the connection
    active_connections[session_id] = websocket
    logger.info(f"Client connected with session ID: {session_id}")

    # Send confirmation of connection
    try:
        await websocket.send_json({"type": "connected", "session_id": session_id})
    except Exception as e:
        logger.error(f"Error sending connection confirmation: {e}")

    return session_id


def disconnect(session_id: str) -> None:
    """
    Remove a WebSocket client from active connections.

    Args:
        session_id (str): The session ID to disconnect
    """
    if session_id in active_connections:
        del active_connections[session_id]
        logger.info(f"Client disconnected: {session_id}")


def is_connected(websocket: WebSocket) -> bool:
    """
    Check if the websocket is still connected.

    Args:
        websocket (WebSocket): The WebSocket to check

    Returns:
        bool: True if connected, False otherwise
    """
    return websocket.client_state == WebSocketState.CONNECTED


async def process_and_stream_message(
    websocket: WebSocket, session_id: str, message: str
) -> None:
    """
    Process a message through the workflow and stream the response chunks.

    Args:
        websocket (WebSocket): The WebSocket connection
        session_id (str): The session identifier
        message (str): The user message to process
    """
    try:
        # Check if websocket is still connected
        if not is_connected(websocket):
            logger.warning(f"WebSocket for session {session_id} is no longer connected")
            return

        # Send acknowledgment that processing has started
        await websocket.send_json(
            {"type": "start", "session_id": session_id, "status": "processing"}
        )

        # Stream response chunks
        async for chunk in process_message_stream(session_id, message):
            # Check connection before sending each chunk
            if not is_connected(websocket):
                logger.warning(
                    f"WebSocket disconnected during streaming for session {session_id}"
                )
                return

            if hasattr(chunk, "content") and chunk.content:
                # Send each chunk as it becomes available
                await websocket.send_json(
                    {
                        "type": "chunk",
                        "content": chunk.content,
                        "session_id": session_id,
                        "final": False,
                    }
                )

        # Check connection before sending completion
        if is_connected(websocket):
            # Send completion message
            await websocket.send_json(
                {"type": "complete", "session_id": session_id, "final": True}
            )

            # Optional: Add artificial delay for smoother streaming
            # await asyncio.sleep(0.1)

    except RuntimeError as e:
        # Handle specific case of already closed connection
        if "already completed" in str(e) or "websocket.close" in str(e):
            logger.warning(f"Connection already closed for session {session_id}: {e}")
            disconnect(session_id)
        else:
            # For other runtime errors
            logger.error(f"Runtime error in streaming: {e}")
            # Only try to send error if still connected
            if is_connected(websocket):
                try:
                    await websocket.send_json(
                        {
                            "type": "error",
                            "content": "Internal server error occurred",
                            "session_id": session_id,
                        }
                    )
                except Exception:
                    pass
    except Exception as e:
        logger.error(f"Error streaming message: {e}")
        # Only try to send error if still connected
        if is_connected(websocket):
            try:
                await websocket.send_json(
                    {
                        "type": "error",
                        "content": f"Failed to process message",
                        "session_id": session_id,
                    }
                )
            except Exception:
                pass
