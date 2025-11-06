from typing import Protocol, Optional
from uuid import UUID

from src.domain.models.conversation_state import ConversationState
from src.domain.models.memory import ConversationMemory


class ConversationStateRepository(Protocol):
    async def save_state(self, state: ConversationState) -> None:
        ...

    async def get_state(self, conversation_id: UUID) -> Optional[ConversationState]:
        ...

    async def delete_state(self, conversation_id: UUID) -> None:
        ...

    async def get_active_conversations(self, user_id: UUID) -> list[ConversationState]:
        ...

    async def cleanup_abandoned(self, hours: int = 24) -> int:
        ...


class ConversationMemoryRepository(Protocol):
    async def save_memory(self, memory: ConversationMemory) -> None:
        ...

    async def get_memory(self, conversation_id: UUID) -> Optional[ConversationMemory]:
        ...

    async def delete_memory(self, conversation_id: UUID) -> None:
        ...

    async def clear_old_turns(self, conversation_id: UUID, keep_last: int) -> None:
        ...