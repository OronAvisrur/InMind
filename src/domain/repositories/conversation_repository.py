from typing import Protocol, List, Optional
from datetime import datetime
from ..models import Conversation, Message
from ..value_objects import ConversationIdentifier, UserIdentifier, MessageRole


class ConversationRepository(Protocol):
    async def create(self, conversation: Conversation) -> Conversation:
        ...

    async def get_by_id(self, conversation_id: ConversationIdentifier) -> Optional[Conversation]:
        ...

    async def get_by_user_id(self, user_id: UserIdentifier) -> List[Conversation]:
        ...

    async def get_active_conversation(self, user_id: UserIdentifier) -> Optional[Conversation]:
        ...

    async def add_message(
        self,
        conversation_id: ConversationIdentifier,
        role: MessageRole,
        content: str
    ) -> Message:
        ...

    async def update(self, conversation: Conversation) -> Conversation:
        ...

    async def delete(self, conversation_id: ConversationIdentifier) -> bool:
        ...

    async def get_conversations_since(
        self,
        user_id: UserIdentifier,
        since: datetime
    ) -> List[Conversation]:
        ...