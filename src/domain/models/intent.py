from typing import List, Dict, Any
from pydantic import BaseModel, Field
from ..value_objects import IntentType, Entity


class DetectedIntent(BaseModel):
    intent_type: IntentType
    confidence: float = Field(ge=0.0, le=1.0)
    entities: List[Entity] = Field(default_factory=list)
    raw_query: str = Field(min_length=1)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def get_entities_by_type(self, entity_type: str) -> List[Entity]:
        return [e for e in self.entities if e.type.value == entity_type]

    def has_entity_type(self, entity_type: str) -> bool:
        return any(e.type.value == entity_type for e in self.entities)


class IntentDetectionResult(BaseModel):
    primary_intent: DetectedIntent
    alternative_intents: List[DetectedIntent] = Field(default_factory=list)
    processing_time_ms: float = Field(ge=0.0)