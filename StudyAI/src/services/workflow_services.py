import logging
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from src.core.workflow import create_workflow
from .basic_services import add_message_to_session
from typing import Dict, Any, List, AsyncGenerator
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

# Store active workflows by thread_id
active_workflows = {}


def initialize_workflow(thread_id: str) -> bool:
    """
    Initialize a new workflow for the given thread_id.

    Args:
        thread_id (str): Unique identifier for the conversation thread

    Returns:
        bool: True if workflow was created successfully
    """
    try:
        # Create workflow if it doesn't exist
        if thread_id not in active_workflows:
            workflow = create_workflow()
            active_workflows[thread_id] = workflow
            logger.info(f"Initialized new workflow for thread_id: {thread_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize workflow: {e}")
        return False


async def process_message(thread_id: str, message: str) -> Dict[str, Any]:
    """Process message with single response."""
    try:
        if thread_id not in active_workflows:
            initialize_workflow(thread_id)

        workflow = active_workflows.get(thread_id)

        config = {"configurable": {"thread_id": "1"}}

        if message:
            add_message_to_session(thread_id, "user", message)

        human_message = HumanMessage(content=message)
        message = {"messages": [human_message]}

        state = workflow.invoke(message, config)

        # Get the last message as response
        last_message = state["messages"][-1]

        if last_message:
            add_message_to_session(thread_id, "bot", last_message.content)

        return {
            "content": last_message.content,
            "thread_id": thread_id,
            "message_count": len(state["messages"]),
        }

    except Exception as e:
        logger.error(f"Error processing message in workflow: {e}")
        return {
            "content": "Error processing message",
            "thread_id": thread_id,
            "agent": "error",
        }


async def process_message_stream(
    thread_id: str, message: str, db: Session
) -> AsyncGenerator[Dict[str, Any], None]:
    """Process a message through the workflow."""
    final_ai_message = None
    try:
        if thread_id not in active_workflows:
            initialize_workflow(thread_id)

        workflow = active_workflows.get(thread_id)
        config = {"configurable": {"thread_id": "1"}}

        human_message = HumanMessage(content=message)
        message = {"messages": [human_message]}

        async for chunk in workflow.astream(
            message,
            config,
            stream_mode="values",
        ):
            if "messages" in chunk and chunk["messages"]:
                # Get only the last AI message with content
                last_ai_message = next(
                    (
                        msg
                        for msg in reversed(chunk["messages"])
                        if isinstance(msg, AIMessage) and hasattr(msg, "content")
                    ),
                    None,
                )

                if last_ai_message:
                    final_ai_message = last_ai_message
                else:
                    logger.warning("No valid AI message found in chunk")
                    logger.info(chunk)
            else:
                logger.warning("No messages in response")
                logger.info(chunk)

    except Exception as e:
        logger.error(f"Error processing message in workflow: {e}")
    finally:
        if final_ai_message:
            # Extract content from AIMessage before adding to session
            message_content = (
                final_ai_message.content
                if hasattr(final_ai_message, "content")
                else str(final_ai_message)
            )
            add_message_to_session(db, thread_id, "bot", message_content)
            yield final_ai_message


def get_conversation_history(thread_id: str) -> List[Dict[str, Any]]:
    """
    Get the conversation history for a thread.

    Args:
        thread_id (str): Unique identifier for the conversation thread

    Returns:
        List[Dict]: List of messages in the conversation
    """
    try:
        if thread_id not in active_workflows:
            return []

        workflow = active_workflows[thread_id]
        # Get latest state (this might need adjustment based on your StateGraph implementation)
        state = workflow.get_state()

        # Format messages
        history = []
        for msg in state["messages"]:
            history.append(
                {
                    "role": "user" if msg.type == "human" else "assistant",
                    "content": msg.content,
                }
            )
        return history
    except Exception as e:
        logger.error(f"Error retrieving conversation history: {e}")
        return []
