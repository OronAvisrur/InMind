from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from ..value_objects import (
    ConversationIdentifier,
    MessageIdentifier,
    UserIdentifier,
    MessageRole,
)


class Message(BaseModel):
    id: MessageIdentifier = Field(default_factory=MessageIdentifier)
    role: MessageRole
    content: str = Field(min_length=1)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Conversation(BaseModel):
    id: ConversationIdentifier = Field(default_factory=ConversationIdentifier)
    user_id: UserIdentifier
    messages: List[Message] = Field(default_factory=list)
    context: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)

    def add_message(self, role: MessageRole, content: str, metadata: Optional[Dict[str, Any]] = None) -> Message:
        message = Message(
            role=role,
            content=content,
            metadata=metadata or {}
        )
        self.messages.append(message)
        self.updated_at = datetime.utcnow()
        return message

    def get_recent_messages(self, limit: int = 10) -> List[Message]:
        return self.messages[-limit:]

    def clear_messages(self) -> None:
        self.messages = []
        self.updated_at = datetime.utcnow()