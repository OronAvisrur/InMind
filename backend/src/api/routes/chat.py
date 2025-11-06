from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from src.api.schemas import (
    ChatRequest,
    ChatResponse,
    ConversationStartRequest,
    ConversationStartResponse,
    ConversationEndRequest,
    ConversationEndResponse,
)
from src.api.dependencies import (
    get_conversation_manager,
    get_state_repository,
)
from src.application.services.conversation_manager import ConversationManager
from src.domain.repositories.conversation_state_repository import ConversationStateRepository
from src.domain.value_objects.identifiers import UserId, ConversationId
from src.domain.models.conversation_state import ConversationStatus


router = APIRouter(prefix="/api/v1/conversations", tags=["Chat"])


@router.post("/start", response_model=ConversationStartResponse)
async def start_conversation(
    request: ConversationStartRequest,
    manager: ConversationManager = Depends(get_conversation_manager),
):
    try:
        user_id = UserId.from_string(request.user_id)
        state = await manager.start_conversation(user_id)
        
        return ConversationStartResponse(
            conversation_id=str(state.conversation_id.value),
            user_id=str(state.user_id.value),
            status=state.status.value,
            dialog_state=state.dialog_state.value,
            created_at=state.created_at
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start conversation: {str(e)}"
        )


@router.post("/{conversation_id}/message", response_model=ChatResponse)
async def send_message(
    conversation_id: str,
    request: ChatRequest,
    manager: ConversationManager = Depends(get_conversation_manager),
):
    try:
        user_id = UserId.from_string(request.user_id)
        conv_id = ConversationId.from_string(conversation_id)
        
        response = await manager.process_message(
            conversation_id=conv_id,
            user_id=user_id,
            message=request.message
        )
        
        state = await manager._state_repository.get_by_id(conv_id)
        if not state:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        entities_dict = {}
        for entity in response.detected_intent.entities:
            if entity.entity_type.value not in entities_dict:
                entities_dict[entity.entity_type.value] = []
            entities_dict[entity.entity_type.value].append(entity.value)
        
        return ChatResponse(
            conversation_id=str(conv_id.value),
            user_id=str(user_id.value),
            user_message=request.message,
            assistant_message=response.assistant_response,
            intent_type=response.detected_intent.intent_type.value,
            entities=entities_dict,
            confidence=response.detected_intent.confidence,
            dialog_state=state.dialog_state.value,
            timestamp=datetime.utcnow()
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process message: {str(e)}"
        )


@router.post("/{conversation_id}/end", response_model=ConversationEndResponse)
async def end_conversation(
    conversation_id: str,
    request: ConversationEndRequest,
    state_repo: ConversationStateRepository = Depends(get_state_repository),
):
    try:
        conv_id = ConversationId.from_string(conversation_id)
        state = await state_repo.get_by_id(conv_id)
        
        if not state:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        state.status = ConversationStatus.COMPLETED
        state.updated_at = datetime.utcnow()
        await state_repo.update(state)
        
        return ConversationEndResponse(
            conversation_id=str(conv_id.value),
            status=state.status.value,
            ended_at=state.updated_at
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to end conversation: {str(e)}"
        )


@router.get("/{conversation_id}", response_model=ConversationStartResponse)
async def get_conversation(
    conversation_id: str,
    state_repo: ConversationStateRepository = Depends(get_state_repository),
):
    try:
        conv_id = ConversationId.from_string(conversation_id)
        state = await state_repo.get_by_id(conv_id)
        
        if not state:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        return ConversationStartResponse(
            conversation_id=str(state.conversation_id.value),
            user_id=str(state.user_id.value),
            status=state.status.value,
            dialog_state=state.dialog_state.value,
            created_at=state.created_at
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get conversation: {str(e)}"
        )
