import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock

from src.application.services.conversation_manager import (
    ConversationManager,
    ConversationManagerConfig
)
from src.domain.models.conversation_state import ConversationState, DialogState, ConversationStatus
from src.domain.models.memory import ConversationMemory, MemoryConfig
from src.domain.models.message import Message, MessageRole
from src.domain.models.intent import DetectedIntent, Entity
from src.domain.models.rag import RAGResponse
from src.domain.models.product import Product
from src.infrastructure.conversation.in_memory_state_repository import InMemoryStateRepository
from src.infrastructure.conversation.in_memory_memory_repository import InMemoryMemoryRepository


class TestConversationManager:
    @pytest.fixture
    def state_repository(self):
        return InMemoryStateRepository()

    @pytest.fixture
    def memory_repository(self):
        return InMemoryMemoryRepository()

    @pytest.fixture
    def mock_intent_detector(self):
        detector = AsyncMock()
        detector.detect_intent = AsyncMock()
        return detector

    @pytest.fixture
    def mock_rag_pipeline(self):
        pipeline = AsyncMock()
        pipeline.generate_recommendation = AsyncMock()
        return pipeline

    @pytest.fixture
    def manager_config(self):
        memory_config = MemoryConfig(max_turns=5, max_context_tokens=1000)
        return ConversationManagerConfig(
            memory_config=memory_config,
            enable_state_persistence=True,
            auto_transition=True
        )

    @pytest.fixture
    def manager(
        self,
        state_repository,
        memory_repository,
        mock_intent_detector,
        mock_rag_pipeline,
        manager_config
    ):
        return ConversationManager(
            state_repository=state_repository,
            memory_repository=memory_repository,
            intent_detector=mock_intent_detector,
            rag_pipeline=mock_rag_pipeline,
            config=manager_config
        )

    @pytest.mark.asyncio
    async def test_start_conversation(self, manager, state_repository, memory_repository):
        user_id = uuid4()
        
        state = await manager.start_conversation(user_id)
        
        assert state.user_id == user_id
        assert state.current_state == DialogState.GREETING
        assert state.status == ConversationStatus.ACTIVE
        
        saved_state = await state_repository.get_state(state.conversation_id)
        assert saved_state is not None
        
        saved_memory = await memory_repository.get_memory(state.conversation_id)
        assert saved_memory is not None

    @pytest.mark.asyncio
    async def test_process_greeting_message(
        self,
        manager,
        mock_intent_detector
    ):
        user_id = uuid4()
        state = await manager.start_conversation(user_id)
        
        greeting_intent = DetectedIntent(
            intent_type="GREETING",
            confidence=0.95,
            entities=[]
        )
        mock_intent_detector.detect_intent.return_value = greeting_intent
        
        response, updated_state = await manager.process_message(
            state.conversation_id,
            "Hello"
        )
        
        assert "Hello" in response or "help" in response.lower()
        assert updated_state.current_state == DialogState.GREETING
        assert updated_state.message_count == 1

    @pytest.mark.asyncio
    async def test_process_thank_you_message(
        self,
        manager,
        mock_intent_detector
    ):
        user_id = uuid4()
        state = await manager.start_conversation(user_id)
        
        thank_you_intent = DetectedIntent(
            intent_type="THANK_YOU",
            confidence=0.98,
            entities=[]
        )
        mock_intent_detector.detect_intent.return_value = thank_you_intent
        
        response, updated_state = await manager.process_message(
            state.conversation_id,
            "Thank you"
        )
        
        assert "welcome" in response.lower()
        assert updated_state.status == ConversationStatus.COMPLETED
        assert updated_state.current_state == DialogState.CLOSING

    @pytest.mark.asyncio
    async def test_process_search_product_message(
        self,
        manager,
        mock_intent_detector,
        mock_rag_pipeline
    ):
        user_id = uuid4()
        state = await manager.start_conversation(user_id)
        
        search_intent = DetectedIntent(
            intent_type="SEARCH_PRODUCT",
            confidence=0.92,
            entities=[
                Entity(entity_type="CATEGORY", value="laptop", confidence=0.9)
            ]
        )
        mock_intent_detector.detect_intent.return_value = search_intent
        
        product = Product(
            id=uuid4(),
            name="Test Laptop",
            description="A great laptop",
            price=999.99,
            category="laptop",
            brand="TestBrand"
        )
        
        rag_response = RAGResponse(
            response_text="I found some great laptops for you!",
            recommended_products=[product],
            reasoning="Based on your search for laptops",
            confidence=0.88,
            sources_used=1
        )
        mock_rag_pipeline.generate_recommendation.return_value = rag_response
        
        response, updated_state = await manager.process_message(
            state.conversation_id,
            "I need a laptop"
        )
        
        assert response == "I found some great laptops for you!"
        assert updated_state.current_state == DialogState.SEARCHING
        assert "CATEGORY" in updated_state.context.collected_entities
        assert len(updated_state.context.search_history) == 1
        assert product.id in updated_state.context.recommended_products

    @pytest.mark.asyncio
    async def test_state_transition_on_intent_change(
        self,
        manager,
        mock_intent_detector,
        mock_rag_pipeline
    ):
        user_id = uuid4()
        state = await manager.start_conversation(user_id)
        
        recommendation_intent = DetectedIntent(
            intent_type="GET_RECOMMENDATION",
            confidence=0.91,
            entities=[]
        )
        mock_intent_detector.detect_intent.return_value = recommendation_intent
        
        rag_response = RAGResponse(
            response_text="Here are my recommendations",
            recommended_products=[],
            reasoning="Based on your preferences",
            confidence=0.85,
            sources_used=0
        )
        mock_rag_pipeline.generate_recommendation.return_value = rag_response
        
        response, updated_state = await manager.process_message(
            state.conversation_id,
            "What do you recommend?"
        )
        
        assert updated_state.current_state == DialogState.RECOMMENDING

    @pytest.mark.asyncio
    async def test_entity_collection_from_intent(
        self,
        manager,
        mock_intent_detector,
        mock_rag_pipeline
    ):
        user_id = uuid4()
        state = await manager.start_conversation(user_id)
        
        search_intent = DetectedIntent(
            intent_type="SEARCH_PRODUCT",
            confidence=0.93,
            entities=[
                Entity(entity_type="CATEGORY", value="headphones", confidence=0.9),
                Entity(entity_type="BRAND", value="Sony", confidence=0.85),
                Entity(entity_type="PRICE_RANGE", value="under $200", confidence=0.8)
            ]
        )
        mock_intent_detector.detect_intent.return_value = search_intent
        
        rag_response = RAGResponse(
            response_text="Found headphones",
            recommended_products=[],
            reasoning="Search results",
            confidence=0.8,
            sources_used=0
        )
        mock_rag_pipeline.generate_recommendation.return_value = rag_response
        
        response, updated_state = await manager.process_message(
            state.conversation_id,
            "I need Sony headphones under $200"
        )
        
        assert "CATEGORY" in updated_state.context.collected_entities
        assert "BRAND" in updated_state.context.collected_entities
        assert "PRICE_RANGE" in updated_state.context.collected_entities

    @pytest.mark.asyncio
    async def test_conversation_not_found_error(self, manager):
        non_existent_id = uuid4()
        
        with pytest.raises(ValueError, match="not found"):
            await manager.process_message(non_existent_id, "Hello")

    @pytest.mark.asyncio
    async def test_end_conversation(self, manager, state_repository):
        user_id = uuid4()
        state = await manager.start_conversation(user_id)
        
        await manager.end_conversation(state.conversation_id)
        
        updated_state = await state_repository.get_state(state.conversation_id)
        assert updated_state.status == ConversationStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_get_conversation_state(self, manager):
        user_id = uuid4()
        state = await manager.start_conversation(user_id)
        
        retrieved_state = await manager.get_conversation_state(state.conversation_id)
        
        assert retrieved_state is not None
        assert retrieved_state.conversation_id == state.conversation_id

    @pytest.mark.asyncio
    async def test_get_conversation_memory(self, manager):
        user_id = uuid4()
        state = await manager.start_conversation(user_id)
        
        retrieved_memory = await manager.get_conversation_memory(state.conversation_id)
        
        assert retrieved_memory is not None
        assert retrieved_memory.conversation_id == state.conversation_id

    @pytest.mark.asyncio
    async def test_memory_persistence_across_messages(
        self,
        manager,
        mock_intent_detector,
        memory_repository
    ):
        user_id = uuid4()
        state = await manager.start_conversation(user_id)
        
        greeting_intent = DetectedIntent(
            intent_type="GREETING",
            confidence=0.95,
            entities=[]
        )
        mock_intent_detector.detect_intent.return_value = greeting_intent
        
        await manager.process_message(state.conversation_id, "Hello")
        await manager.process_message(state.conversation_id, "Hi again")
        
        memory = await memory_repository.get_memory(state.conversation_id)
        
        assert memory.turn_count == 2
        assert len(memory.get_all_messages()) == 4

    @pytest.mark.asyncio
    async def test_clarification_handling(
        self,
        manager,
        mock_intent_detector
    ):
        user_id = uuid4()
        state = await manager.start_conversation(user_id)
        
        clarification_intent = DetectedIntent(
            intent_type="CLARIFICATION",
            confidence=0.87,
            entities=[]
        )
        mock_intent_detector.detect_intent.return_value = clarification_intent
        
        response, updated_state = await manager.process_message(
            state.conversation_id,
            "What do you mean?"
        )
        
        assert updated_state.current_state == DialogState.CLARIFYING
        assert "more" in response.lower() or "details" in response.lower()