from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime

from src.domain.models.conversation_state import (
    ConversationState,
    DialogState,
    ConversationStatus
)
from src.domain.models.memory import ConversationMemory, MemoryConfig
from src.domain.models.message import Message, MessageRole
from src.domain.models.intent import DetectedIntent
from src.domain.models.rag import RAGRequest, RAGResponse
from src.domain.repositories.conversation_state_repository import (
    ConversationStateRepository,
    ConversationMemoryRepository
)
from src.application.services.intent_detector import IntentDetectorService
from src.application.services.rag_pipeline import RAGPipeline


class ConversationManagerConfig:
    def __init__(
        self,
        memory_config: MemoryConfig,
        enable_state_persistence: bool = True,
        auto_transition: bool = True
    ):
        self.memory_config = memory_config
        self.enable_state_persistence = enable_state_persistence
        self.auto_transition = auto_transition


class ConversationManager:
    def __init__(
        self,
        state_repository: ConversationStateRepository,
        memory_repository: ConversationMemoryRepository,
        intent_detector: IntentDetectorService,
        rag_pipeline: RAGPipeline,
        config: ConversationManagerConfig
    ):
        self._state_repo = state_repository
        self._memory_repo = memory_repository
        self._intent_detector = intent_detector
        self._rag_pipeline = rag_pipeline
        self._config = config

    async def start_conversation(self, user_id: UUID) -> ConversationState:
        conversation_id = uuid4()
        state = ConversationState(
            conversation_id=conversation_id,
            user_id=user_id,
            current_state=DialogState.GREETING,
            status=ConversationStatus.ACTIVE
        )
        
        memory = ConversationMemory(
            conversation_id=conversation_id,
            max_turns=self._config.memory_config.max_turns
        )
        
        if self._config.enable_state_persistence:
            await self._state_repo.save_state(state)
            await self._memory_repo.save_memory(memory)
        
        return state

    async def process_message(
        self,
        conversation_id: UUID,
        user_message: str
    ) -> tuple[str, ConversationState]:
        state = await self._state_repo.get_state(conversation_id)
        if not state:
            raise ValueError(f"Conversation {conversation_id} not found")
        
        memory = await self._memory_repo.get_memory(conversation_id)
        if not memory:
            memory = ConversationMemory(
                conversation_id=conversation_id,
                max_turns=self._config.memory_config.max_turns
            )
        
        start_time = datetime.utcnow()
        
        user_msg = Message(
            conversation_id=conversation_id,
            role=MessageRole.USER,
            content=user_message
        )
        
        detected_intent = await self._intent_detector.detect_intent(user_message)
        
        await self._update_state_from_intent(state, detected_intent)
        
        response_text = await self._generate_response(
            state=state,
            memory=memory,
            user_message=user_message,
            detected_intent=detected_intent
        )
        
        assistant_msg = Message(
            conversation_id=conversation_id,
            role=MessageRole.ASSISTANT,
            content=response_text
        )
        
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        memory.add_turn(
            user_message=user_msg,
            assistant_message=assistant_msg,
            processing_time_ms=processing_time
        )
        
        state.increment_message_count()
        
        if self._config.enable_state_persistence:
            await self._state_repo.save_state(state)
            await self._memory_repo.save_memory(memory)
        
        return response_text, state

    async def _update_state_from_intent(
        self,
        state: ConversationState,
        intent: DetectedIntent
    ) -> None:
        if not self._config.auto_transition:
            return
        
        intent_to_state_map = {
            "SEARCH_PRODUCT": DialogState.SEARCHING,
            "GET_RECOMMENDATION": DialogState.RECOMMENDING,
            "COMPARE_PRODUCTS": DialogState.COMPARING,
            "ASK_FEATURE": DialogState.COLLECTING_INFO,
            "ASK_PRICE": DialogState.COLLECTING_INFO,
            "CLARIFICATION": DialogState.CLARIFYING,
            "GREETING": DialogState.GREETING,
            "THANK_YOU": DialogState.CLOSING,
        }
        
        new_state = intent_to_state_map.get(intent.intent_type)
        if new_state and new_state != state.current_state:
            state.transition_to(new_state)
        
        for entity in intent.entities:
            state.add_entity(entity.entity_type, entity.value)

    async def _generate_response(
        self,
        state: ConversationState,
        memory: ConversationMemory,
        user_message: str,
        detected_intent: DetectedIntent
    ) -> str:
        if detected_intent.intent_type == "GREETING":
            return "Hello! I'm here to help you find the perfect products. What are you looking for today?"
        
        if detected_intent.intent_type == "THANK_YOU":
            state.mark_completed()
            return "You're welcome! Feel free to come back anytime you need product recommendations. Have a great day!"
        
        if detected_intent.intent_type == "CLARIFICATION":
            return await self._handle_clarification(state, user_message)
        
        if detected_intent.intent_type in ["SEARCH_PRODUCT", "GET_RECOMMENDATION", "COMPARE_PRODUCTS"]:
            return await self._handle_product_query(state, memory, user_message, detected_intent)
        
        return "I'm here to help you find products. Could you tell me more about what you're looking for?"

    async def _handle_clarification(self, state: ConversationState, message: str) -> str:
        if state.context.clarification_needed:
            return f"I need a bit more information: {state.context.clarification_needed}"
        return "Could you provide more details about what you're looking for?"

    async def _handle_product_query(
        self,
        state: ConversationState,
        memory: ConversationMemory,
        query: str,
        intent: DetectedIntent
    ) -> str:
        context_messages = memory.get_context_window(
            max_tokens=self._config.memory_config.max_context_tokens
        )
        
        conversation_context = "\n".join([
            f"{msg.role.value}: {msg.content}"
            for msg in context_messages[-3:]
        ])
        
        filters = self._build_filters_from_entities(intent)
        
        rag_request = RAGRequest(
            query=query,
            conversation_context=conversation_context if conversation_context else None,
            max_results=5,
            filters=filters
        )
        
        rag_response = await self._rag_pipeline.generate_recommendation(rag_request)
        
        for product in rag_response.recommended_products:
            state.add_recommended_product(product.id)
        
        state.add_search_query(query)
        
        return rag_response.response_text

    def _build_filters_from_entities(self, intent: DetectedIntent) -> Optional[dict]:
        filters = {}
        
        for entity in intent.entities:
            if entity.entity_type == "CATEGORY":
                filters["category"] = entity.value
            elif entity.entity_type == "BRAND":
                filters["brand"] = entity.value
            elif entity.entity_type == "PRICE_RANGE":
                filters["price_range"] = entity.value
        
        return filters if filters else None

    async def end_conversation(self, conversation_id: UUID) -> None:
        state = await self._state_repo.get_state(conversation_id)
        if state:
            state.mark_completed()
            await self._state_repo.save_state(state)

    async def get_conversation_state(self, conversation_id: UUID) -> Optional[ConversationState]:
        return await self._state_repo.get_state(conversation_id)

    async def get_conversation_memory(self, conversation_id: UUID) -> Optional[ConversationMemory]:
        return await self._memory_repo.get_memory(conversation_id)