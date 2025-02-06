from dataclasses import dataclass, field, asdict
from datetime import datetime
import uuid
from typing import List

@dataclass
class Message:
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    message: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    sender: str = "user"  # New field

    def to_dict(self):
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return data

@dataclass
class ChatSession:
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.now(datetime.timezone.utc))
    messages: List[dict] = field(default_factory=list)

    def add_message(self, message: Message):
        self.messages.append(message.to_dict())

    def to_dict(self):
        return {
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat(),
            "messages": self.messages,
        }