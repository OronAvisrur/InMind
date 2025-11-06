from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class EntityResponse(BaseModel):
    entity_type: str = Field(description="Type of entity")
    value: str = Field(description="Entity value")
    confidence: float = Field(ge=0.0, le=1.0, description="Extraction confidence")


class IntentDetectRequest(BaseModel):
    text: str = Field(min_length=1, max_length=1000, description="Text to analyze")
    context: Optional[dict[str, list[str]]] = Field(default=None, description="Conversation context")


class IntentDetectResponse(BaseModel):
    intent_type: str = Field(description="Detected intent type")
    confidence: float = Field(ge=0.0, le=1.0, description="Detection confidence")
    entities: list[EntityResponse] = Field(description="Extracted entities")
    raw_text: str = Field(description="Original input text")
    timestamp: datetime = Field(description="Detection timestamp")