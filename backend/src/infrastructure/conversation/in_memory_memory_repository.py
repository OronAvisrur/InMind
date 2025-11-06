from typing import Optional
from uuid import UUID

from src.domain.models.memory import ConversationMemory
from src.domain.repositories.conversation_state_repository import ConversationMemoryRepository


class InMemoryMemoryRepository:
    def __init__(self):
        self._memories: dict[UUID, ConversationMemory] = {}

    async def save_memory(self, memory: ConversationMemory) -> None:
        self._memories[memory.conversation_id] = memory

    async def get_memory(self, conversation_id: UUID) -> Optional[ConversationMemory]:
        return self._memories.get(conversation_id)

    async def delete_memory(self, conversation_id: UUID) -> None:
        self._memories.pop(conversation_id, None)

    async def clear_old_turns(self, conversation_id: UUID, keep_last: int) -> None:
        memory = self._memories.get(conversation_id)
        if memory and len(memory.turns) > keep_last:
            memory.turns = memory.turns[-keep_last:]

    def clear(self) -> None:
        self._memories.clear()

    @property
    def count(self) -> int:
        return len(self._memories)