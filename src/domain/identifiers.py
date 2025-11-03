from typing import NewType
from uuid import UUID, uuid4
from pydantic import BaseModel, Field

ProductId = NewType("ProductId", UUID)
UserId = NewType("UserId", UUID)
ConversationId = NewType("ConversationId", UUID)
MessageId = NewType("MessageId", UUID)


class Identifier(BaseModel):
    value: UUID = Field(default_factory=uuid4)

    def __str__(self) -> str:
        return str(self.value)

    def __hash__(self) -> int:
        return hash(self.value)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Identifier):
            return False
        return self.value == other.value


class ProductIdentifier(Identifier):
    pass


class UserIdentifier(Identifier):
    pass


class ConversationIdentifier(Identifier):
    pass


class MessageIdentifier(Identifier):
    pass