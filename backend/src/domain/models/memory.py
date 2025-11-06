from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from .message import Message, MessageRole


class ConversationTurn(BaseModel):
    turn_number: int
    user_message: Message
    assistant_message: Optional[Message] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    processing_time_ms: Optional[float] = None


class ConversationMemory(BaseModel):
    conversation_id: UUID
    turns: list[ConversationTurn] = Field(default_factory=list)
    max_turns: int = Field(default=10)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def add_turn(
        self,
        user_message: Message,
        assistant_message: Optional[Message] = None,
        processing_time_ms: Optional[float] = None
    ) -> None:
        turn = ConversationTurn(
            turn_number=len(self.turns) + 1,
            user_message=user_message,
            assistant_message=assistant_message,
            processing_time_ms=processing_time_ms
        )
        self.turns.append(turn)
        self._enforce_max_turns()
        self.updated_at = datetime.utcnow()

    def _enforce_max_turns(self) -> None:
        if len(self.turns) > self.max_turns:
            self.turns = self.turns[-self.max_turns:]

    def get_recent_turns(self, count: int) -> list[ConversationTurn]:
        return self.turns[-count:] if count < len(self.turns) else self.turns

    def get_all_messages(self) -> list[Message]:
        messages: list[Message] = []
        for turn in self.turns:
            messages.append(turn.user_message)
            if turn.assistant_message:
                messages.append(turn.assistant_message)
        return messages

    def get_context_window(self, max_tokens: int = 2000) -> list[Message]:
        messages = self.get_all_messages()
        context_messages: list[Message] = []
        estimated_tokens = 0
        
        for message in reversed(messages):
            message_tokens = len(message.content.split()) * 1.3
            if estimated_tokens + message_tokens > max_tokens:
                break
            context_messages.insert(0, message)
            estimated_tokens += message_tokens
        
        return context_messages

    def clear_history(self) -> None:
        self.turns = []
        self.updated_at = datetime.utcnow()

    @property
    def turn_count(self) -> int:
        return len(self.turns)

    @property
    def total_messages(self) -> int:
        return sum(2 if turn.assistant_message else 1 for turn in self.turns)


class MemoryConfig(BaseModel):
    max_turns: int = Field(default=10, ge=1, le=50)
    max_context_tokens: int = Field(default=2000, ge=100, le=8000)
    enable_summarization: bool = Field(default=False)
    summarization_threshold: int = Field(default=20)