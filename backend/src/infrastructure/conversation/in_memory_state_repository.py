from typing import Optional
from uuid import UUID
from datetime import datetime, timedelta

from src.domain.models.conversation_state import ConversationState, ConversationStatus
from src.domain.repositories.conversation_state_repository import ConversationStateRepository


class InMemoryStateRepository:
    def __init__(self):
        self._states: dict[UUID, ConversationState] = {}

    async def save_state(self, state: ConversationState) -> None:
        self._states[state.conversation_id] = state

    async def get_state(self, conversation_id: UUID) -> Optional[ConversationState]:
        return self._states.get(conversation_id)

    async def delete_state(self, conversation_id: UUID) -> None:
        self._states.pop(conversation_id, None)

    async def get_active_conversations(self, user_id: UUID) -> list[ConversationState]:
        return [
            state for state in self._states.values()
            if state.user_id == user_id and state.status == ConversationStatus.ACTIVE
        ]

    async def cleanup_abandoned(self, hours: int = 24) -> int:
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        abandoned_ids = [
            conv_id for conv_id, state in self._states.items()
            if state.last_activity_at < cutoff_time and state.status == ConversationStatus.ACTIVE
        ]
        
        for conv_id in abandoned_ids:
            state = self._states[conv_id]
            state.mark_abandoned()
        
        return len(abandoned_ids)

    def clear(self) -> None:
        self._states.clear()

    @property
    def count(self) -> int:
        return len(self._states)