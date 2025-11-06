import pytest
from uuid import uuid4
from datetime import datetime

from src.domain.models.memory import (
    ConversationMemory,
    ConversationTurn,
    MemoryConfig
)
from src.domain.models.message import Message, MessageRole


class TestConversationTurn:
    def test_initialization(self):
        user_msg = Message(
            conversation_id=uuid4(),
            role=MessageRole.USER,
            content="Hello"
        )
        assistant_msg = Message(
            conversation_id=uuid4(),
            role=MessageRole.ASSISTANT,
            content="Hi there"
        )
        
        turn = ConversationTurn(
            turn_number=1,
            user_message=user_msg,
            assistant_message=assistant_msg,
            processing_time_ms=150.5
        )
        
        assert turn.turn_number == 1
        assert turn.user_message == user_msg
        assert turn.assistant_message == assistant_msg
        assert turn.processing_time_ms == 150.5
        assert isinstance(turn.timestamp, datetime)


class TestConversationMemory:
    def test_initialization_with_defaults(self):
        conversation_id = uuid4()
        
        memory = ConversationMemory(conversation_id=conversation_id)
        
        assert memory.conversation_id == conversation_id
        assert memory.turns == []
        assert memory.max_turns == 10
        assert isinstance(memory.created_at, datetime)

    def test_add_turn_with_both_messages(self):
        memory = ConversationMemory(conversation_id=uuid4())
        
        user_msg = Message(
            conversation_id=memory.conversation_id,
            role=MessageRole.USER,
            content="Test message"
        )
        assistant_msg = Message(
            conversation_id=memory.conversation_id,
            role=MessageRole.ASSISTANT,
            content="Response"
        )
        
        memory.add_turn(user_msg, assistant_msg, 100.0)
        
        assert len(memory.turns) == 1
        assert memory.turns[0].turn_number == 1
        assert memory.turns[0].user_message == user_msg
        assert memory.turns[0].assistant_message == assistant_msg

    def test_add_turn_user_only(self):
        memory = ConversationMemory(conversation_id=uuid4())
        
        user_msg = Message(
            conversation_id=memory.conversation_id,
            role=MessageRole.USER,
            content="Question"
        )
        
        memory.add_turn(user_msg)
        
        assert len(memory.turns) == 1
        assert memory.turns[0].assistant_message is None

    def test_enforce_max_turns(self):
        memory = ConversationMemory(conversation_id=uuid4(), max_turns=3)
        
        for i in range(5):
            user_msg = Message(
                conversation_id=memory.conversation_id,
                role=MessageRole.USER,
                content=f"Message {i}"
            )
            memory.add_turn(user_msg)
        
        assert len(memory.turns) == 3
        assert memory.turns[0].user_message.content == "Message 2"
        assert memory.turns[-1].user_message.content == "Message 4"

    def test_get_recent_turns(self):
        memory = ConversationMemory(conversation_id=uuid4())
        
        for i in range(5):
            user_msg = Message(
                conversation_id=memory.conversation_id,
                role=MessageRole.USER,
                content=f"Message {i}"
            )
            memory.add_turn(user_msg)
        
        recent = memory.get_recent_turns(3)
        
        assert len(recent) == 3
        assert recent[0].user_message.content == "Message 2"
        assert recent[-1].user_message.content == "Message 4"

    def test_get_recent_turns_more_than_available(self):
        memory = ConversationMemory(conversation_id=uuid4())
        
        user_msg = Message(
            conversation_id=memory.conversation_id,
            role=MessageRole.USER,
            content="Only one"
        )
        memory.add_turn(user_msg)
        
        recent = memory.get_recent_turns(10)
        
        assert len(recent) == 1

    def test_get_all_messages(self):
        memory = ConversationMemory(conversation_id=uuid4())
        
        user_msg_1 = Message(
            conversation_id=memory.conversation_id,
            role=MessageRole.USER,
            content="First"
        )
        assistant_msg_1 = Message(
            conversation_id=memory.conversation_id,
            role=MessageRole.ASSISTANT,
            content="Response 1"
        )
        memory.add_turn(user_msg_1, assistant_msg_1)
        
        user_msg_2 = Message(
            conversation_id=memory.conversation_id,
            role=MessageRole.USER,
            content="Second"
        )
        memory.add_turn(user_msg_2)
        
        messages = memory.get_all_messages()
        
        assert len(messages) == 3
        assert messages[0] == user_msg_1
        assert messages[1] == assistant_msg_1
        assert messages[2] == user_msg_2

    def test_get_context_window_token_limit(self):
        memory = ConversationMemory(conversation_id=uuid4())
        
        for i in range(10):
            user_msg = Message(
                conversation_id=memory.conversation_id,
                role=MessageRole.USER,
                content=" ".join(["word"] * 100)
            )
            memory.add_turn(user_msg)
        
        context = memory.get_context_window(max_tokens=200)
        
        assert len(context) < 10
        assert len(context) > 0

    def test_clear_history(self):
        memory = ConversationMemory(conversation_id=uuid4())
        
        user_msg = Message(
            conversation_id=memory.conversation_id,
            role=MessageRole.USER,
            content="Test"
        )
        memory.add_turn(user_msg)
        
        assert len(memory.turns) == 1
        
        memory.clear_history()
        
        assert len(memory.turns) == 0

    def test_turn_count_property(self):
        memory = ConversationMemory(conversation_id=uuid4())
        
        assert memory.turn_count == 0
        
        for i in range(3):
            user_msg = Message(
                conversation_id=memory.conversation_id,
                role=MessageRole.USER,
                content=f"Message {i}"
            )
            memory.add_turn(user_msg)
        
        assert memory.turn_count == 3

    def test_total_messages_property(self):
        memory = ConversationMemory(conversation_id=uuid4())
        
        user_msg_1 = Message(
            conversation_id=memory.conversation_id,
            role=MessageRole.USER,
            content="First"
        )
        assistant_msg_1 = Message(
            conversation_id=memory.conversation_id,
            role=MessageRole.ASSISTANT,
            content="Response"
        )
        memory.add_turn(user_msg_1, assistant_msg_1)
        
        user_msg_2 = Message(
            conversation_id=memory.conversation_id,
            role=MessageRole.USER,
            content="Second"
        )
        memory.add_turn(user_msg_2)
        
        assert memory.total_messages == 3


class TestMemoryConfig:
    def test_default_values(self):
        config = MemoryConfig()
        
        assert config.max_turns == 10
        assert config.max_context_tokens == 2000
        assert config.enable_summarization is False
        assert config.summarization_threshold == 20

    def test_custom_values(self):
        config = MemoryConfig(
            max_turns=20,
            max_context_tokens=4000,
            enable_summarization=True,
            summarization_threshold=30
        )
        
        assert config.max_turns == 20
        assert config.max_context_tokens == 4000
        assert config.enable_summarization is True
        assert config.summarization_threshold == 30

    def test_validation_constraints(self):
        with pytest.raises(Exception):
            MemoryConfig(max_turns=0)
        
        with pytest.raises(Exception):
            MemoryConfig(max_turns=100)
        
        with pytest.raises(Exception):
            MemoryConfig(max_context_tokens=50)
