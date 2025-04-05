from enum import Enum
from typing import Dict, Any
from src.core.base import BaseAgent
from src.core.state import AgentState, update_metadata
from langchain_core.messages import HumanMessage, SystemMessage
from typing import AsyncGenerator
import logging


class QuestionType(str, Enum):
    GENERIC = "Generic"
    INAPPROPRIATE = "Inappropriate"
    OTHER = "Other"


class QuestionTypeCheckerAgent(BaseAgent):
    """Agent that checks question type and appropriateness."""

    def __init__(self):
        super().__init__()
        self.system_message = """You are an AI assistant that analyzes student questions for profanity check.
            Your task is to:
            1. Check if the question contains inappropriate content or abusive language.
            2. Determine if the question is generic questions like "Hi", "Hello", "How are you?" etc.
            3. If the question seems to be related to academics or FAQs you don't know then return type as "Other".

            Respond in the format:
            TYPE: <Inappropriate| Generic | Other>
            REASON: <brief explanation>
        """

    async def process_question(self, message: str) -> dict[str, Any]:
        """Process the question and determine its type."""
        chain = self.create_chain("{system_message}\n\nQuestion: {input}")
        response = await chain.ainvoke(
            {"system_message": self.system_message, "input": message}
        )

        # Parse response
        response_lines = str(response).strip().split("\n")
        q_type = None
        reason = "Unknown reason"

        for line in response_lines:
            if line.startswith("TYPE:"):
                q_type = line.split(":", 1)[1].strip()
            elif line.startswith("REASON:"):
                reason = line.split(":", 1)[1].strip()

        if not q_type:
            q_type = "Other"

        return {"q_type": q_type, "reason": reason}


async def check_question_type_node(
    state: AgentState,
) -> AsyncGenerator[AgentState, None]:
    """Check the type of the question and update the state."""
    agent = QuestionTypeCheckerAgent()

    try:
        # Get the last message from the user
        last_message = next(
            (
                msg.content
                for msg in reversed(state["messages"])
                if isinstance(msg, HumanMessage)
            ),
            None,
        )

        if last_message is None:
            raise ValueError("No user message found in the state.")

        # Process the question using the agent
        response = await agent.process_question(last_message)

        if response["q_type"] == "Inappropriate":
            state["next_step"] = "dismiss"
            # Flag that this is not coming from supervisor
            state = update_metadata(state, "from_supervisor", False)
            state["messages"].append(
                SystemMessage(content=f"Inappropriate: {response['reason']}")
            )
        elif response["q_type"] == "Generic":
            state["next_step"] = "dismiss"
            # Flag that this is not coming from supervisor
            state = update_metadata(state, "from_supervisor", False)
            state["messages"].append(
                SystemMessage(content=f"Generic: {response['reason']}")
            )
        else:
            state["next_step"] = "supervisor"

    except ValueError as ve:
        logging.error(f"Value error: {str(ve)}")
        state["next_step"] = "dismiss"
        # Flag that this is not coming from supervisor
        state = update_metadata(state, "from_supervisor", False)
        state["messages"].append(SystemMessage(content=str(ve)))
    except Exception as e:
        logging.error(f"Routing error: {str(e)}")
        state["next_step"] = "dismiss"
        # Flag that this is not coming from supervisor
        state = update_metadata(state, "from_supervisor", False)
        state["messages"].append(SystemMessage(content=str(e)))
    finally:
        # Ensure the state is yielded even in case of errors
        yield state
