import pytest
from uuid import uuid4
from datetime import datetime, timedelta

from src.infrastructure.conversation.in_memory_state_repository import InMemoryStateRepository
from src.domain.models.conversation_state import (
    ConversationState,
    ConversationStatus,
    DialogState
)


class TestInMemoryStateRepository:
    @pytest.fixture
    def repository(self):
        return InMemoryStateRepository()

    @pytest.fixture
    def sample_state(self):
        return ConversationState(
            conversation_id=uuid4(),
            user_id=uuid4(),
            current_state=DialogState.GREETING
        )

    @pytest.mark.asyncio
    async def test_save_and_get_state(self, repository, sample_state):
        await repository.save_state(sample_state)
        
        retrieved = await repository.get_state(sample_state.conversation_id)
        
        assert retrieved is not None
        assert retrieved.conversation_id == sample_state.conversation_id
        assert retrieved.user_id == sample_state.user_id
        assert retrieved.current_state == DialogState.GREETING

    @pytest.mark.asyncio
    async def test_get_nonexistent_state(self, repository):
        non_existent_id = uuid4()
        
        retrieved = await repository.get_state(non_existent_id)
        
        assert retrieved is None

    @pytest.mark.asyncio
    async def test_update_existing_state(self, repository, sample_state):
        await repository.save_state(sample_state)
        
        sample_state.transition_to(DialogState.SEARCHING)
        sample_state.add_entity("CATEGORY", "laptop")
        
        await repository.save_state(sample_state)
        
        retrieved = await repository.get_state(sample_state.conversation_id)
        
        assert retrieved.current_state == DialogState.SEARCHING
        assert "CATEGORY" in retrieved.context.collected_entities

    @pytest.mark.asyncio
    async def test_delete_state(self, repository, sample_state):
        await repository.save_state(sample_state)
        
        assert await repository.get_state(sample_state.conversation_id) is not None
        
        await repository.delete_state(sample_state.conversation_id)
        
        assert await repository.get_state(sample_state.conversation_id) is None

    @pytest.mark.asyncio
    async def test_delete_nonexistent_state(self, repository):
        non_existent_id = uuid4()
        
        await repository.delete_state(non_existent_id)
        
        assert repository.count == 0

    @pytest.mark.asyncio
    async def test_get_active_conversations_by_user(self, repository):
        user_id = uuid4()
        
        state1 = ConversationState(
            conversation_id=uuid4(),
            user_id=user_id,
            status=ConversationStatus.ACTIVE
        )
        state2 = ConversationState(
            conversation_id=uuid4(),
            user_id=user_id,
            status=ConversationStatus.ACTIVE
        )
        state3 = ConversationState(
            conversation_id=uuid4(),
            user_id=user_id,
            status=ConversationStatus.COMPLETED
        )
        
        await repository.save_state(state1)
        await repository.save_state(state2)
        await repository.save_state(state3)
        
        active_conversations = await repository.get_active_conversations(user_id)
        
        assert len(active_conversations) == 2
        assert all(conv.status == ConversationStatus.ACTIVE for conv in active_conversations)

    @pytest.mark.asyncio
    async def test_get_active_conversations_filters_by_user(self, repository):
        user1_id = uuid4()
        user2_id = uuid4()
        
        state1 = ConversationState(
            conversation_id=uuid4(),
            user_id=user1_id,
            status=ConversationStatus.ACTIVE
        )
        state2 = ConversationState(
            conversation_id=uuid4(),
            user_id=user2_id,
            status=ConversationStatus.ACTIVE
        )
        
        await repository.save_state(state1)
        await repository.save_state(state2)
        
        user1_conversations = await repository.get_active_conversations(user1_id)
        
        assert len(user1_conversations) == 1
        assert user1_conversations[0].user_id == user1_id

    @pytest.mark.asyncio
    async def test_cleanup_abandoned_conversations(self, repository):
        old_time = datetime.utcnow() - timedelta(hours=25)
        recent_time = datetime.utcnow() - timedelta(hours=1)
        
        old_state = ConversationState(
            conversation_id=uuid4(),
            user_id=uuid4(),
            status=ConversationStatus.ACTIVE
        )
        old_state.last_activity_at = old_time
        
        recent_state = ConversationState(
            conversation_id=uuid4(),
            user_id=uuid4(),
            status=ConversationStatus.ACTIVE
        )
        recent_state.last_activity_at = recent_time
        
        await repository.save_state(old_state)
        await repository.save_state(recent_state)
        
        count = await repository.cleanup_abandoned(hours=24)
        
        assert count == 1
        
        old_retrieved = await repository.get_state(old_state.conversation_id)
        assert old_retrieved.status == ConversationStatus.ABANDONED
        
        recent_retrieved = await repository.get_state(recent_state.conversation_id)
        assert recent_retrieved.status == ConversationStatus.ACTIVE

    @pytest.mark.asyncio
    async def test_cleanup_does_not_affect_completed(self, repository):
        old_time = datetime.utcnow() - timedelta(hours=25)
        
        completed_state = ConversationState(
            conversation_id=uuid4(),
            user_id=uuid4(),
            status=ConversationStatus.COMPLETED
        )
        completed_state.last_activity_at = old_time
        
        await repository.save_state(completed_state)
        
        count = await repository.cleanup_abandoned(hours=24)
        
        assert count == 0

    @pytest.mark.asyncio
    async def test_clear(self, repository, sample_state):
        await repository.save_state(sample_state)
        
        assert repository.count == 1
        
        repository.clear()
        
        assert repository.count == 0

    @pytest.mark.asyncio
    async def test_count_property(self, repository):
        assert repository.count == 0
        
        state1 = ConversationState(conversation_id=uuid4(), user_id=uuid4())
        state2 = ConversationState(conversation_id=uuid4(), user_id=uuid4())
        
        await repository.save_state(state1)
        assert repository.count == 1
        
        await repository.save_state(state2)
        assert repository.count == 2
        
        await repository.delete_state(state1.conversation_id)
        assert repository.count == 1
