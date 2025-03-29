import logging
import asyncio
import signal
from typing import Dict
from fastapi import WebSocket
from fastapi.websockets import WebSocketState
from sqlalchemy.orm import Session
from src.services.workflow_services import process_message_stream

logger = logging.getLogger(__name__)

# Store active WebSocket connections by session_id
active_connections: Dict[str, WebSocket] = {}
# Store locks to prevent race conditions when sending messages
connection_locks: Dict[str, asyncio.Lock] = {}
# Flag to indicate server is shutting down
is_shutting_down = False


async def connect(websocket: WebSocket, session_id: str) -> str:
    """
    Connect a WebSocket client and return the session ID.
    Args:
        websocket (WebSocket): The WebSocket connection
        session_id (str): The session identifier
    Returns:
        str: Session ID for the connection
    """
    if is_shutting_down:
        # Don't accept new connections during shutdown
        logger.info(f"Rejecting connection during shutdown: {session_id}")
        return session_id

    await websocket.accept()

    # Store the connection and create a lock for it
    active_connections[session_id] = websocket
    connection_locks[session_id] = asyncio.Lock()
    logger.info(f"Client connected with session ID: {session_id}")

    # Send confirmation of connection
    try:
        await websocket.send_json({"type": "connected", "session_id": session_id})
    except Exception as e:
        logger.error(f"Error sending connection confirmation: {e}")
        # If we can't send the initial confirmation, the connection may be broken
        disconnect(session_id)

    return session_id


def disconnect(session_id: str) -> None:
    """
    Remove a WebSocket client from active connections.
    Args:
        session_id (str): The session ID to disconnect
    """
    if session_id in active_connections:
        del active_connections[session_id]
        # Also remove the lock if it exists
        if session_id in connection_locks:
            del connection_locks[session_id]
        logger.info(f"Client disconnected: {session_id}")


def is_connected(websocket: WebSocket) -> bool:
    """
    Check if the websocket is still connected.
    Args:
        websocket (WebSocket): The WebSocket to check
    Returns:
        bool: True if connected, False otherwise
    """
    # Early return if server is shutting down
    if is_shutting_down:
        return False

    try:
        # Check both client and application states
        return (
            websocket.client_state == WebSocketState.CONNECTED
            and websocket.application_state == WebSocketState.CONNECTED
        )
    except Exception:
        # If there's any exception checking the state, assume it's disconnected
        return False


async def safe_send_json(
    websocket: WebSocket, data: dict, session_id: str = None
) -> bool:
    """
    Safely send JSON data over the WebSocket with connection checking.
    Args:
        websocket (WebSocket): The WebSocket connection
        data (dict): The data to send
        session_id (str, optional): The session ID for locking
    Returns:
        bool: True if sent successfully, False otherwise
    """
    # Check global shutdown flag first
    if is_shutting_down:
        return False

    if not is_connected(websocket):
        return False

    # Use a lock if session_id is provided to prevent race conditions
    if session_id and session_id in connection_locks:
        lock = connection_locks[session_id]
        async with lock:
            # Double-check connection state after acquiring the lock
            if not is_connected(websocket) or is_shutting_down:
                return False

            try:
                await websocket.send_json(data)
                return True
            except RuntimeError as e:
                if "websocket.close" in str(e) or "already completed" in str(e):
                    # Connection already closed
                    logger.debug(
                        f"Cannot send message, WebSocket already closed: {str(e)[:100]}..."
                    )
                    return False
                raise  # Re-raise other RuntimeErrors
            except Exception as e:
                logger.error(f"Error sending data: {str(e)[:100]}...")
                return False
    else:
        # No lock available, proceed with normal send
        try:
            await websocket.send_json(data)
            return True
        except RuntimeError as e:
            if "websocket.close" in str(e) or "already completed" in str(e):
                # Connection already closed
                logger.debug(
                    f"Cannot send message, WebSocket already closed: {str(e)[:100]}..."
                )
                return False
            raise  # Re-raise other RuntimeErrors
        except Exception as e:
            logger.error(f"Error sending data: {str(e)[:100]}...")
            return False


async def disconnect_all_clients():
    """
    Disconnect all active WebSocket clients.
    Used during shutdown to ensure clean termination.
    """
    global is_shutting_down
    is_shutting_down = True

    logger.info(f"Disconnecting all {len(active_connections)} clients during shutdown")

    # Create a copy of session IDs to avoid dict modification during iteration
    session_ids = list(active_connections.keys())
    for session_id in session_ids:
        try:
            websocket = active_connections.get(session_id)
            if websocket:
                # Try to send a close message if possible
                try:
                    if is_connected(websocket):
                        await websocket.send_json(
                            {
                                "type": "system",
                                "content": "Server is shutting down",
                                "session_id": session_id,
                            }
                        )
                except Exception:
                    pass  # Ignore errors during shutdown

            # Disconnect the session
            disconnect(session_id)
        except Exception as e:
            logger.error(f"Error disconnecting client {session_id}: {e}")

    logger.info("All clients disconnected")


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
    if is_shutting_down:
        logger.info(f"Skipping message processing during shutdown: {session_id}")
        return

    try:
        # Check if websocket is still connected
        if not is_connected(websocket):
            logger.warning(f"WebSocket for session {session_id} is no longer connected")
            disconnect(session_id)  # Make sure to clean up
            return

        # Send acknowledgment that processing has started
        if not await safe_send_json(
            websocket,
            {"type": "start", "session_id": session_id, "status": "processing"},
            session_id,
        ):
            disconnect(session_id)
            return

        # Stream response chunks
        async for chunk_data in process_message_stream(session_id, message, db):
            # Check shutdown flag during processing
            if is_shutting_down:
                break

            # Use our safe send method
            if chunk_data and "content" in chunk_data:
                if not await safe_send_json(
                    websocket,
                    {
                        "type": "chunk",
                        "content": chunk_data["content"],
                        "message_id": chunk_data["message_id"],
                        "session_id": session_id,
                        "final": False,
                    },
                    session_id,
                ):
                    disconnect(session_id)
                    return

        # Send completion message if still connected
        if is_connected(websocket) and not is_shutting_down:
            await safe_send_json(
                websocket,
                {"type": "complete", "session_id": session_id, "final": True},
                session_id,
            )

    except RuntimeError as e:
        # Handle specific case of already closed connection
        if "already completed" in str(e) or "websocket.close" in str(e):
            logger.warning(f"Connection already closed for session {session_id}: {e}")
            disconnect(session_id)
        else:
            logger.error(f"Runtime error in streaming: {e}")
            # Only try to send error if still connected
            if is_connected(websocket) and not is_shutting_down:
                await safe_send_json(
                    websocket,
                    {
                        "type": "error",
                        "content": "Internal server error occurred",
                        "session_id": session_id,
                    },
                    session_id,
                )
    except Exception as e:
        logger.error(f"Error streaming message: {e}")
        if is_connected(websocket) and not is_shutting_down:
            await safe_send_json(
                websocket,
                {
                    "type": "error",
                    "content": f"Failed to process message",
                    "session_id": session_id,
                },
                session_id,
            )
    finally:
        # Ensure we clean up any broken connections
        if not is_connected(websocket) and session_id in active_connections:
            disconnect(session_id)


# Register shutdown handlers
def setup_shutdown_handlers(app):
    """
    Set up event handlers for graceful shutdown.
    Should be called when initializing the FastAPI app.

    Args:
        app: The FastAPI application instance
    """

    @app.on_event("shutdown")
    async def handle_shutdown():
        """Handle graceful shutdown of WebSocket connections"""
        await disconnect_all_clients()
