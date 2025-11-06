from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from src.api.schemas import (
    IntentDetectRequest,
    IntentDetectResponse,
    EntityResponse,
)
from src.api.dependencies import get_intent_detector
from src.application.services.intent_detector import IntentDetectorService
from src.domain.models.conversation_state import ConversationContext


router = APIRouter(prefix="/api/v1/intents", tags=["Intent Detection"])


@router.post("/detect", response_model=IntentDetectResponse)
async def detect_intent(
    request: IntentDetectRequest,
    intent_detector: IntentDetectorService = Depends(get_intent_detector),
):
    try:
        context = None
        if request.context:
            context = ConversationContext(
                collected_entities=request.context,
                search_history=[]
            )
        
        detected_intent = await intent_detector.detect_intent(
            text=request.text,
            context=context
        )
        
        entity_responses = [
            EntityResponse(
                entity_type=entity.entity_type.value,
                value=entity.value,
                confidence=entity.confidence
            )
            for entity in detected_intent.entities
        ]
        
        return IntentDetectResponse(
            intent_type=detected_intent.intent_type.value,
            confidence=detected_intent.confidence,
            entities=entity_responses,
            raw_text=request.text,
            timestamp=datetime.utcnow()
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to detect intent: {str(e)}"
        )
