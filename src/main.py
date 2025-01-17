from typing import Dict, List
from langgraph.graph import MessagesState, END
from langgraph.types import Command
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.supervisor import supervisor_node

def format_agent_response(response: str) -> str:
    """Format the agent's response for display"""
    return f"Assistant: {response}\n"

def main():
    # Initialize message state
    state = MessagesState({
        "messages": [],
        "current_agent": "course_guidance"
    })

    print("Welcome to the academic assistant. Type 'exit' to quit.\n")

    while True:
        try:
            # Get user input
            user_input = input("User: ").strip()
            
            # Check exit condition
            if user_input.lower() == "exit":
                print("Ending conversation.")
                break

            # Add user message to state
            state["messages"].append({
                "role": "user", 
                "content": user_input
            })

            # Process through supervisor
            command: Command = supervisor_node(state)

            # Get last assistant message
            if state["messages"]:
                last_message = next(
                    msg for msg in reversed(state["messages"]) 
                    if msg["role"] == "assistant"
                )
                print(format_agent_response(last_message["content"]))

            # Handle routing
            if command.goto == END:
                print("The conversation has concluded.")
                break
            else:
                print(f"[System: Routing to {command.goto} agent]\n")
                state["current_agent"] = command.goto

        except KeyboardInterrupt:
            print("\nConversation terminated by user.")
            break
        except Exception as e:
            print(f"\nAn error occurred: {str(e)}")
            print("Please try again.")

if __name__ == "__main__":
    main()