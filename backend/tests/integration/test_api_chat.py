import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
from uuid import uuid4
from datetime import datetime
from src.main import app
from src.domain.models.conversation_state import DialogState, ConversationStatus

client = TestClient(app)


@pytest.fixture
def mock_conversation_manager():
    with patch("src.api.dependencies.ConversationManager") as mock:
        mock_instance = MagicMock()
        mock_instance.start_conversation = AsyncMock()
        mock_instance.process_message = AsyncMock()
        mock_instance.get_conversation_state = AsyncMock()
        mock_instance.end_conversation = AsyncMock()
        mock.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_state_repository():
    with patch("src.api.dependencies.InMemoryConversationStateRepository") as mock:
        mock_instance = MagicMock()
        mock_instance.get = AsyncMock()
        mock.return_value = mock_instance
        yield mock_instance


class TestConversationStartEndpoint:
    def test_start_conversation_success(self, mock_conversation_manager):
        conversation_id = str(uuid4())
        mock_conversation_manager.start_conversation.return_value = MagicMock(
            conversation_id=conversation_id,
            user_id="test-user-123",
            status=ConversationStatus.ACTIVE,
            current_state=DialogState.GREETING,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        response = client.post(
            "/api/v1/conversations/start",
            json={"user_id": "test-user-123"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["conversation_id"] == conversation_id
        assert data["user_id"] == "test-user-123"
        assert data["status"] == "ACTIVE"
        assert data["current_state"] == "GREETING"
    
    def test_start_conversation_with_empty_user_id_fails(self):
        response = client.post(
            "/api/v1/conversations/start",
            json={"user_id": ""}
        )
        
        assert response.status_code == 422
    
    def test_start_conversation_with_missing_user_id_fails(self):
        response = client.post(
            "/api/v1/conversations/start",
            json={}
        )
        
        assert response.status_code == 422
    
    def test_start_conversation_creates_new_id(self, mock_conversation_manager):
        conversation_id_1 = str(uuid4())
        conversation_id_2 = str(uuid4())
        
        mock_conversation_manager.start_conversation.side_effect = [
            MagicMock(
                conversation_id=conversation_id_1,
                user_id="user1",
                status=ConversationStatus.ACTIVE,
                current_state=DialogState.GREETING,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            ),
            MagicMock(
                conversation_id=conversation_id_2,
                user_id="user2",
                status=ConversationStatus.ACTIVE,
                current_state=DialogState.GREETING,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
        ]
        
        response1 = client.post(
            "/api/v1/conversations/start",
            json={"user_id": "user1"}
        )
        response2 = client.post(
            "/api/v1/conversations/start",
            json={"user_id": "user2"}
        )
        
        assert response1.json()["conversation_id"] != response2.json()["conversation_id"]


class TestConversationMessageEndpoint:
    def test_send_message_success(self, mock_conversation_manager):
        conversation_id = str(uuid4())
        mock_conversation_manager.process_message.return_value = MagicMock(
            response="I found some great laptops for you!",
            intent="SEARCH_PRODUCT",
            entities=[{"type": "PRODUCT_NAME", "value": "laptop"}],
            current_state=DialogState.COLLECTING_REQUIREMENTS
        )
        
        response = client.post(
            f"/api/v1/conversations/{conversation_id}/message",
            json={"message": "I need a laptop"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["response"] == "I found some great laptops for you!"
        assert data["intent"] == "SEARCH_PRODUCT"
        assert len(data["entities"]) == 1
        assert data["current_state"] == "COLLECTING_REQUIREMENTS"
    
    def test_send_message_with_empty_message_fails(self):
        conversation_id = str(uuid4())
        response = client.post(
            f"/api/v1/conversations/{conversation_id}/message",
            json={"message": ""}
        )
        
        assert response.status_code == 422
    
    def test_send_message_with_whitespace_only_fails(self):
        conversation_id = str(uuid4())
        response = client.post(
            f"/api/v1/conversations/{conversation_id}/message",
            json={"message": "   "}
        )
        
        assert response.status_code == 422
    
    def test_send_message_with_invalid_conversation_id_fails(self):
        response = client.post(
            "/api/v1/conversations/invalid-uuid/message",
            json={"message": "Hello"}
        )
        
        assert response.status_code == 422
    
    def test_send_message_preserves_conversation_context(self, mock_conversation_manager):
        conversation_id = str(uuid4())
        
        mock_conversation_manager.process_message.side_effect = [
            MagicMock(
                response="What kind of laptop are you looking for?",
                intent="GREETING",
                entities=[],
                current_state=DialogState.COLLECTING_REQUIREMENTS
            ),
            MagicMock(
                response="Here are some gaming laptops under $1500",
                intent="SEARCH_PRODUCT",
                entities=[
                    {"type": "PRODUCT_NAME", "value": "laptop"},
                    {"type": "CATEGORY", "value": "gaming"},
                    {"type": "PRICE_RANGE", "value": "under $1500"}
                ],
                current_state=DialogState.PROVIDING_RECOMMENDATIONS
            )
        ]
        
        response1 = client.post(
            f"/api/v1/conversations/{conversation_id}/message",
            json={"message": "Hi"}
        )
        response2 = client.post(
            f"/api/v1/conversations/{conversation_id}/message",
            json={"message": "I want a gaming laptop under $1500"}
        )
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert response2.json()["current_state"] == "PROVIDING_RECOMMENDATIONS"


class TestConversationGetEndpoint:
    def test_get_conversation_state_success(self, mock_conversation_manager):
        conversation_id = str(uuid4())
        mock_conversation_manager.get_conversation_state.return_value = MagicMock(
            conversation_id=conversation_id,
            user_id="test-user-123",
            status=ConversationStatus.ACTIVE,
            current_state=DialogState.COLLECTING_REQUIREMENTS,
            turn_count=3,
            collected_entities={"product_name": "laptop", "price_range": "under $1000"},
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        response = client.get(f"/api/v1/conversations/{conversation_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["conversation_id"] == conversation_id
        assert data["user_id"] == "test-user-123"
        assert data["status"] == "ACTIVE"
        assert data["turn_count"] == 3
    
    def test_get_conversation_not_found(self, mock_conversation_manager):
        conversation_id = str(uuid4())
        mock_conversation_manager.get_conversation_state.return_value = None
        
        response = client.get(f"/api/v1/conversations/{conversation_id}")
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
    
    def test_get_conversation_with_invalid_id_fails(self):
        response = client.get("/api/v1/conversations/invalid-uuid")
        
        assert response.status_code == 422


class TestConversationEndEndpoint:
    def test_end_conversation_success(self, mock_conversation_manager):
        conversation_id = str(uuid4())
        mock_conversation_manager.end_conversation.return_value = MagicMock(
            conversation_id=conversation_id,
            user_id="test-user-123",
            status=ConversationStatus.COMPLETED,
            current_state=DialogState.ENDING,
            turn_count=5,
            collected_entities={},
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        response = client.post(f"/api/v1/conversations/{conversation_id}/end")
        
        assert response.status_code == 200
        data = response.json()
        assert data["conversation_id"] == conversation_id
        assert data["status"] == "COMPLETED"
        assert data["message"] == "Conversation ended successfully"
    
    def test_end_conversation_not_found(self, mock_conversation_manager):
        conversation_id = str(uuid4())
        mock_conversation_manager.end_conversation.return_value = None
        
        response = client.post(f"/api/v1/conversations/{conversation_id}/end")
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
    
    def test_end_conversation_with_invalid_id_fails(self):
        response = client.post("/api/v1/conversations/invalid-uuid/end")
        
        assert response.status_code == 422
    
    def test_end_conversation_changes_status(self, mock_conversation_manager):
        conversation_id = str(uuid4())
        
        mock_conversation_manager.start_conversation.return_value = MagicMock(
            conversation_id=conversation_id,
            user_id="test-user",
            status=ConversationStatus.ACTIVE,
            current_state=DialogState.GREETING,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        mock_conversation_manager.end_conversation.return_value = MagicMock(
            conversation_id=conversation_id,
            user_id="test-user",
            status=ConversationStatus.COMPLETED,
            current_state=DialogState.ENDING,
            turn_count=1,
            collected_entities={},
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        start_response = client.post(
            "/api/v1/conversations/start",
            json={"user_id": "test-user"}
        )
        end_response = client.post(f"/api/v1/conversations/{conversation_id}/end")
        
        assert start_response.json()["status"] == "ACTIVE"
        assert end_response.json()["status"] == "COMPLETED"