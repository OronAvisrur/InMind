from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ConversationStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class DialogState(str, Enum):
    INITIAL = "initial"
    GREETING = "greeting"
    COLLECTING_INFO = "collecting_info"
    SEARCHING = "searching"
    RECOMMENDING = "recommending"
    COMPARING = "comparing"
    CLARIFYING = "clarifying"
    CLOSING = "closing"


class ConversationContext(BaseModel):
    collected_entities: dict[str, list[str]] = Field(default_factory=dict)
    search_history: list[str] = Field(default_factory=list)
    recommended_products: list[UUID] = Field(default_factory=list)
    user_preferences: dict[str, str] = Field(default_factory=dict)
    clarification_needed: Optional[str] = None


class ConversationState(BaseModel):
    conversation_id: UUID
    user_id: UUID
    current_state: DialogState = Field(default=DialogState.INITIAL)
    status: ConversationStatus = Field(default=ConversationStatus.ACTIVE)
    context: ConversationContext = Field(default_factory=ConversationContext)
    message_count: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_activity_at: datetime = Field(default_factory=datetime.utcnow)

    def update_activity(self) -> None:
        self.updated_at = datetime.utcnow()
        self.last_activity_at = datetime.utcnow()

    def increment_message_count(self) -> None:
        self.message_count += 1
        self.update_activity()

    def transition_to(self, new_state: DialogState) -> None:
        self.current_state = new_state
        self.update_activity()

    def add_entity(self, entity_type: str, value: str) -> None:
        if entity_type not in self.context.collected_entities:
            self.context.collected_entities[entity_type] = []
        if value not in self.context.collected_entities[entity_type]:
            self.context.collected_entities[entity_type].append(value)
        self.update_activity()

    def add_search_query(self, query: str) -> None:
        self.context.search_history.append(query)
        self.update_activity()

    def add_recommended_product(self, product_id: UUID) -> None:
        if product_id not in self.context.recommended_products:
            self.context.recommended_products.append(product_id)
        self.update_activity()

    def mark_completed(self) -> None:
        self.status = ConversationStatus.COMPLETED
        self.current_state = DialogState.CLOSING
        self.update_activity()

    def mark_abandoned(self) -> None:
        self.status = ConversationStatus.ABANDONED
        self.update_activity()