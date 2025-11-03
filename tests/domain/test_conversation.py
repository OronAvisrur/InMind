import pytest
from src.domain.models import Conversation, Message
from src.domain.value_objects import UserIdentifier, MessageRole, ConversationIdentifier


class TestConversation:
    def test_create_conversation(self):
        user_id = UserIdentifier()
        conv = Conversation(user_id=user_id)
        assert conv.user_id == user_id
        assert len(conv.messages) == 0
        assert conv.is_active is True

    def test_add_message_to_conversation(self):
        user_id = UserIdentifier()
        conv = Conversation(user_id=user_id)
        message = conv.add_message(MessageRole.USER, "I need a new laptop")
        
        assert len(conv.messages) == 1
        assert message.role == MessageRole.USER
        assert message.content == "I need a new laptop"

    def test_conversation_with_multiple_messages(self):
        user_id = UserIdentifier()
        conv = Conversation(user_id=user_id)
        
        conv.add_message(MessageRole.USER, "I want wireless headphones")
        conv.add_message(MessageRole.ASSISTANT, "What's your budget?")
        conv.add_message(MessageRole.USER, "Around $200")
        
        assert len(conv.messages) == 3
        assert conv.messages[0].role == MessageRole.USER
        assert conv.messages[1].role == MessageRole.ASSISTANT
        assert conv.messages[2].content == "Around $200"

    def test_get_recent_messages(self):
        user_id = UserIdentifier()
        conv = Conversation(user_id=user_id)
        
        for i in range(15):
            conv.add_message(MessageRole.USER, f"Message {i}")
        
        recent = conv.get_recent_messages(limit=5)
        assert len(recent) == 5
        assert recent[-1].content == "Message 14"
        assert recent[0].content == "Message 10"

    def test_clear_messages(self):
        user_id = UserIdentifier()
        conv = Conversation(user_id=user_id)
        
        conv.add_message(MessageRole.USER, "Hello")
        conv.add_message(MessageRole.ASSISTANT, "Hi there!")
        assert len(conv.messages) == 2
        
        conv.clear_messages()
        assert len(conv.messages) == 0

    def test_message_has_timestamp(self):
        user_id = UserIdentifier()
        conv = Conversation(user_id=user_id)
        message = conv.add_message(MessageRole.USER, "Test message")
        
        assert message.timestamp is not None

    def test_conversation_updates_timestamp_on_message(self):
        user_id = UserIdentifier()
        conv = Conversation(user_id=user_id)
        original_time = conv.updated_at
        
        conv.add_message(MessageRole.USER, "New message")
        assert conv.updated_at >= original_time