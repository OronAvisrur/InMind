from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from src.domain.value_objects.identifiers import ConversationId, UserId


class ChatRequest(BaseModel):
    user_id: str = Field(description="User identifier")
    message: str = Field(min_length=1, max_length=1000, description="User message")
    conversation_id: Optional[str] = Field(default=None, description="Existing conversation ID")


class ChatResponse(BaseModel):
    conversation_id: str = Field(description="Conversation identifier")
    user_id: str = Field(description="User identifier")
    user_message: str = Field(description="User's input message")
    assistant_message: str = Field(description="Assistant's response")
    intent_type: str = Field(description="Detected intent type")
    entities: dict[str, list[str]] = Field(description="Extracted entities")
    confidence: float = Field(ge=0.0, le=1.0, description="Response confidence score")
    dialog_state: str = Field(description="Current dialog state")
    timestamp: datetime = Field(description="Response timestamp")


class ConversationStartRequest(BaseModel):
    user_id: str = Field(description="User identifier")


class ConversationStartResponse(BaseModel):
    conversation_id: str = Field(description="New conversation identifier")
    user_id: str = Field(description="User identifier")
    status: str = Field(description="Conversation status")
    dialog_state: str = Field(description="Initial dialog state")
    created_at: datetime = Field(description="Conversation creation timestamp")


class ConversationEndRequest(BaseModel):
    reason: Optional[str] = Field(default=None, description="Reason for ending conversation")


class ConversationEndResponse(BaseModel):
    conversation_id: str = Field(description="Ended conversation identifier")
    status: str = Field(description="Final conversation status")
    ended_at: datetime = Field(description="Conversation end timestamp")