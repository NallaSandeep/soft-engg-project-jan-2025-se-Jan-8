import logging
import asyncio
from typing import Dict
from fastapi import WebSocket
from fastapi.websockets import WebSocketState
from sqlalchemy.orm import Session
from src.services.workflow_services import process_message_stream

logger = logging.getLogger(__name__)

# Store active WebSocket connections by session_id
active_connections: Dict[str, WebSocket] = {}


async def connect(websocket: WebSocket, session_id: str) -> str:
    """
    Connect a WebSocket client and return the session ID.
    Args:
        websocket (WebSocket): The WebSocket connection
        session_id (str): The session identifier
    Returns:
        str: Session ID for the connection
    """
    await websocket.accept()

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
    websocket: WebSocket, session_id: str, message: str, db: Session
) -> None:
    """
    Process a message through the workflow and stream the response chunks.
    Args:
        websocket (WebSocket): The WebSocket connection
        session_id (str): The session identifier
        message (str): The user message to process
        db (Session): Database session
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
        async for chunk_data in process_message_stream(session_id, message, db):
            # Check connection before sending each chunk
            if not is_connected(websocket):
                logger.warning(
                    f"WebSocket disconnected during streaming for session {session_id}"
                )
                return

            if chunk_data and "content" in chunk_data:
                await websocket.send_json(
                    {
                        "type": "chunk",
                        "content": chunk_data["content"],
                        "message_id": chunk_data["message_id"],
                        "session_id": session_id,
                        "final": False,
                    }
                )

        # Check connection before sending completion
        if is_connected(websocket):
            await websocket.send_json(
                {"type": "complete", "session_id": session_id, "final": True}
            )

    except RuntimeError as e:
        # Handle specific case of already closed connection
        if "already completed" in str(e) or "websocket.close" in str(e):
            logger.warning(f"Connection already closed for session {session_id}: {e}")
            disconnect(session_id)
        else:
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
