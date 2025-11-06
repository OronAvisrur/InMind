import pytest
from uuid import uuid4

from src.infrastructure.conversation.in_memory_memory_repository import InMemoryMemoryRepository
from src.domain.models.memory import ConversationMemory
from src.domain.models.message import Message, MessageRole


class TestInMemoryMemoryRepository:
    @pytest.fixture
    def repository(self):
        return InMemoryMemoryRepository()

    @pytest.fixture
    def sample_memory(self):
        conversation_id = uuid4()
        memory = ConversationMemory(conversation_id=conversation_id, max_turns=5)
        
        for i in range(3):
            user_msg = Message(
                conversation_id=conversation_id,
                role=MessageRole.USER,
                content=f"User message {i}"
            )
            assistant_msg = Message(
                conversation_id=conversation_id,
                role=MessageRole.ASSISTANT,
                content=f"Assistant response {i}"
            )
            memory.add_turn(user_msg, assistant_msg)
        
        return memory

    @pytest.mark.asyncio
    async def test_save_and_get_memory(self, repository, sample_memory):
        await repository.save_memory(sample_memory)
        
        retrieved = await repository.get_memory(sample_memory.conversation_id)
        
        assert retrieved is not None
        assert retrieved.conversation_id == sample_memory.conversation_id
        assert len(retrieved.turns) == 3

    @pytest.mark.asyncio
    async def test_get_nonexistent_memory(self, repository):
        non_existent_id = uuid4()
        
        retrieved = await repository.get_memory(non_existent_id)
        
        assert retrieved is None

    @pytest.mark.asyncio
    async def test_update_existing_memory(self, repository, sample_memory):
        await repository.save_memory(sample_memory)
        
        user_msg = Message(
            conversation_id=sample_memory.conversation_id,
            role=MessageRole.USER,
            content="New message"
        )
        sample_memory.add_turn(user_msg)
        
        await repository.save_memory(sample_memory)
        
        retrieved = await repository.get_memory(sample_memory.conversation_id)
        
        assert len(retrieved.turns) == 4
        assert retrieved.turns[-1].user_message.content == "New message"

    @pytest.mark.asyncio
    async def test_delete_memory(self, repository, sample_memory):
        await repository.save_memory(sample_memory)
        
        assert await repository.get_memory(sample_memory.conversation_id) is not None
        
        await repository.delete_memory(sample_memory.conversation_id)
        
        assert await repository.get_memory(sample_memory.conversation_id) is None

    @pytest.mark.asyncio
    async def test_delete_nonexistent_memory(self, repository):
        non_existent_id = uuid4()
        
        await repository.delete_memory(non_existent_id)
        
        assert repository.count == 0

    @pytest.mark.asyncio
    async def test_clear_old_turns(self, repository, sample_memory):
        await repository.save_memory(sample_memory)
        
        assert len(sample_memory.turns) == 3
        
        await repository.clear_old_turns(sample_memory.conversation_id, keep_last=2)
        
        retrieved = await repository.get_memory(sample_memory.conversation_id)
        
        assert len(retrieved.turns) == 2
        assert retrieved.turns[0].user_message.content == "User message 1"
        assert retrieved.turns[1].user_message.content == "User message 2"

    @pytest.mark.asyncio
    async def test_clear_old_turns_keep_more_than_exists(self, repository, sample_memory):
        await repository.save_memory(sample_memory)
        
        original_length = len(sample_memory.turns)
        
        await repository.clear_old_turns(sample_memory.conversation_id, keep_last=10)
        
        retrieved = await repository.get_memory(sample_memory.conversation_id)
        
        assert len(retrieved.turns) == original_length

    @pytest.mark.asyncio
    async def test_clear_old_turns_nonexistent_memory(self, repository):
        non_existent_id = uuid4()
        
        await repository.clear_old_turns(non_existent_id, keep_last=5)
        
        assert repository.count == 0

    @pytest.mark.asyncio
    async def test_clear(self, repository, sample_memory):
        await repository.save_memory(sample_memory)
        
        assert repository.count == 1
        
        repository.clear()
        
        assert repository.count == 0

    @pytest.mark.asyncio
    async def test_count_property(self, repository):
        assert repository.count == 0
        
        memory1 = ConversationMemory(conversation_id=uuid4())
        memory2 = ConversationMemory(conversation_id=uuid4())
        
        await repository.save_memory(memory1)
        assert repository.count == 1
        
        await repository.save_memory(memory2)
        assert repository.count == 2
        
        await repository.delete_memory(memory1.conversation_id)
        assert repository.count == 1

    @pytest.mark.asyncio
    async def test_multiple_conversations_isolated(self, repository):
        conv1_id = uuid4()
        conv2_id = uuid4()
        
        memory1 = ConversationMemory(conversation_id=conv1_id)
        memory2 = ConversationMemory(conversation_id=conv2_id)
        
        user_msg1 = Message(
            conversation_id=conv1_id,
            role=MessageRole.USER,
            content="Conversation 1"
        )
        memory1.add_turn(user_msg1)
        
        user_msg2 = Message(
            conversation_id=conv2_id,
            role=MessageRole.USER,
            content="Conversation 2"
        )
        memory2.add_turn(user_msg2)
        
        await repository.save_memory(memory1)
        await repository.save_memory(memory2)
        
        retrieved1 = await repository.get_memory(conv1_id)
        retrieved2 = await repository.get_memory(conv2_id)
        
        assert len(retrieved1.turns) == 1
        assert len(retrieved2.turns) == 1
        assert retrieved1.turns[0].user_message.content == "Conversation 1"
        assert retrieved2.turns[0].user_message.content == "Conversation 2"
