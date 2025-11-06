import pytest
from uuid import uuid4
from datetime import datetime, timedelta

from src.domain.models.conversation_state import (
    ConversationState,
    ConversationStatus,
    DialogState,
    ConversationContext
)


class TestConversationContext:
    def test_initialization(self):
        context = ConversationContext()
        
        assert context.collected_entities == {}
        assert context.search_history == []
        assert context.recommended_products == []
        assert context.user_preferences == {}
        assert context.clarification_needed is None


class TestConversationState:
    def test_initialization_with_defaults(self):
        conversation_id = uuid4()
        user_id = uuid4()
        
        state = ConversationState(
            conversation_id=conversation_id,
            user_id=user_id
        )
        
        assert state.conversation_id == conversation_id
        assert state.user_id == user_id
        assert state.current_state == DialogState.INITIAL
        assert state.status == ConversationStatus.ACTIVE
        assert state.message_count == 0
        assert isinstance(state.context, ConversationContext)

    def test_update_activity(self):
        state = ConversationState(
            conversation_id=uuid4(),
            user_id=uuid4()
        )
        
        original_updated = state.updated_at
        original_activity = state.last_activity_at
        
        state.update_activity()
        
        assert state.updated_at > original_updated
        assert state.last_activity_at > original_activity

    def test_increment_message_count(self):
        state = ConversationState(
            conversation_id=uuid4(),
            user_id=uuid4()
        )
        
        assert state.message_count == 0
        
        state.increment_message_count()
        assert state.message_count == 1
        
        state.increment_message_count()
        assert state.message_count == 2

    def test_transition_to(self):
        state = ConversationState(
            conversation_id=uuid4(),
            user_id=uuid4()
        )
        
        assert state.current_state == DialogState.INITIAL
        
        state.transition_to(DialogState.GREETING)
        assert state.current_state == DialogState.GREETING
        
        state.transition_to(DialogState.SEARCHING)
        assert state.current_state == DialogState.SEARCHING

    def test_add_entity(self):
        state = ConversationState(
            conversation_id=uuid4(),
            user_id=uuid4()
        )
        
        state.add_entity("CATEGORY", "laptop")
        assert "CATEGORY" in state.context.collected_entities
        assert "laptop" in state.context.collected_entities["CATEGORY"]
        
        state.add_entity("CATEGORY", "tablet")
        assert len(state.context.collected_entities["CATEGORY"]) == 2
        
        state.add_entity("CATEGORY", "laptop")
        assert len(state.context.collected_entities["CATEGORY"]) == 2

    def test_add_search_query(self):
        state = ConversationState(
            conversation_id=uuid4(),
            user_id=uuid4()
        )
        
        state.add_search_query("wireless headphones")
        assert len(state.context.search_history) == 1
        assert state.context.search_history[0] == "wireless headphones"
        
        state.add_search_query("under $200")
        assert len(state.context.search_history) == 2

    def test_add_recommended_product(self):
        state = ConversationState(
            conversation_id=uuid4(),
            user_id=uuid4()
        )
        
        product_id_1 = uuid4()
        product_id_2 = uuid4()
        
        state.add_recommended_product(product_id_1)
        assert len(state.context.recommended_products) == 1
        
        state.add_recommended_product(product_id_2)
        assert len(state.context.recommended_products) == 2
        
        state.add_recommended_product(product_id_1)
        assert len(state.context.recommended_products) == 2

    def test_mark_completed(self):
        state = ConversationState(
            conversation_id=uuid4(),
            user_id=uuid4()
        )
        
        state.mark_completed()
        
        assert state.status == ConversationStatus.COMPLETED
        assert state.current_state == DialogState.CLOSING

    def test_mark_abandoned(self):
        state = ConversationState(
            conversation_id=uuid4(),
            user_id=uuid4()
        )
        
        state.mark_abandoned()
        
        assert state.status == ConversationStatus.ABANDONED


class TestDialogState:
    def test_enum_values(self):
        assert DialogState.INITIAL == "initial"
        assert DialogState.GREETING == "greeting"
        assert DialogState.COLLECTING_INFO == "collecting_info"
        assert DialogState.SEARCHING == "searching"
        assert DialogState.RECOMMENDING == "recommending"
        assert DialogState.COMPARING == "comparing"
        assert DialogState.CLARIFYING == "clarifying"
        assert DialogState.CLOSING == "closing"


class TestConversationStatus:
    def test_enum_values(self):
        assert ConversationStatus.ACTIVE == "active"
        assert ConversationStatus.PAUSED == "paused"
        assert ConversationStatus.COMPLETED == "completed"
        assert ConversationStatus.ABANDONED == "abandoned"