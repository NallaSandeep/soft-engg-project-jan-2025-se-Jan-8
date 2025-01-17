from typing import Dict, List, Deque
from collections import deque
from datetime import datetime, timedelta
import json
import os

class ConversationManager:
    def __init__(self):
        self.conversation_history = deque(maxlen=10)
        self.context_window = 4000
        self.request_timestamps = deque(maxlen=100)
        self.rate_limit = 60
        self.artifacts_path = "artifacts/"
        self.conversation_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        os.makedirs(self.artifacts_path, exist_ok=True)

    def check_rate_limit(self) -> bool:
        now = datetime.now()
        self.request_timestamps.append(now)
        minute_ago = now - timedelta(minutes=1)
        recent_requests = sum(1 for ts in self.request_timestamps if ts > minute_ago)
        return recent_requests <= self.rate_limit

    def store_interaction(self, interaction: Dict):
        filepath = os.path.join(self.artifacts_path, f"conversation_{self.conversation_id}.json")
        artifacts = []
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                artifacts = json.load(f)
        
        artifacts.append({
            'timestamp': datetime.now().isoformat(),
            'interaction': interaction
        })
        
        with open(filepath, 'w') as f:
            json.dump(artifacts, f, indent=2)

    def add_to_history(self, role: str, content: str):
        self.conversation_history.append({
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat()
        })

    def get_context(self) -> str:
        context = []
        total_length = 0
        for msg in reversed(self.conversation_history):
            msg_content = f"{msg['role']}: {msg['content']}"
            if total_length + len(msg_content.split()) > self.context_window:
                break
            context.insert(0, msg_content)
            total_length += len(msg_content.split())
        return "\n".join(context)