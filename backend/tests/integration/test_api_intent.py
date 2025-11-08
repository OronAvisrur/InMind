🔷 Phase 8 Step 2: Integration Test for Intent Detection API
💭 Architecture Decision:

Test the intent detection endpoint with real request/response flow
Mock the OllamaClient to avoid external dependencies
Verify request validation, response structure, and error handling
Test different intent scenarios and entity extraction


📝 Create ONE File
backend/tests/integration/test_api_intent.py (NEW)
pythonimport pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


@pytest.fixture
def mock_ollama_client():
    with patch("src.api.dependencies.OllamaClient") as mock:
        mock_instance = MagicMock()
        mock_instance.generate = AsyncMock()
        mock.return_value = mock_instance
        yield mock_instance


class TestIntentDetectionEndpoint:
    def test_detect_intent_with_valid_request(self, mock_ollama_client):
        mock_ollama_client.generate.return_value = '''
        {
            "intent": "SEARCH_PRODUCT",
            "confidence": 0.95,
            "entities": [
                {
                    "type": "PRODUCT_NAME",
                    "value": "laptop",
                    "confidence": 0.9
                },
                {
                    "type": "PRICE_RANGE",
                    "value": "under $1000",
                    "confidence": 0.85
                }
            ]
        }
        '''
        
        response = client.post(
            "/api/v1/intents/detect",
            json={"text": "I need a laptop under $1000"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["intent"] == "SEARCH_PRODUCT"
        assert data["confidence"] >= 0.8
        assert len(data["entities"]) == 2
        assert data["entities"][0]["type"] == "PRODUCT_NAME"
        assert data["entities"][0]["value"] == "laptop"
    
    def test_detect_intent_with_empty_text_fails(self):
        response = client.post(
            "/api/v1/intents/detect",
            json={"text": ""}
        )
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
    
    def test_detect_intent_with_missing_text_fails(self):
        response = client.post(
            "/api/v1/intents/detect",
            json={}
        )
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
    
    def test_detect_intent_with_whitespace_only_fails(self):
        response = client.post(
            "/api/v1/intents/detect",
            json={"text": "   "}
        )
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
    
    def test_detect_intent_returns_proper_structure(self, mock_ollama_client):
        mock_ollama_client.generate.return_value = '''
        {
            "intent": "GET_RECOMMENDATION",
            "confidence": 0.88,
            "entities": []
        }
        '''
        
        response = client.post(
            "/api/v1/intents/detect",
            json={"text": "What do you recommend?"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "intent" in data
        assert "confidence" in data
        assert "entities" in data
        assert "text" in data
        assert isinstance(data["entities"], list)
    
    def test_detect_intent_with_invalid_json_body_fails(self):
        response = client.post(
            "/api/v1/intents/detect",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422
    
    def test_detect_intent_with_multiple_entities(self, mock_ollama_client):
        mock_ollama_client.generate.return_value = '''
        {
            "intent": "SEARCH_PRODUCT",
            "confidence": 0.92,
            "entities": [
                {"type": "PRODUCT_NAME", "value": "headphones", "confidence": 0.95},
                {"type": "BRAND", "value": "Sony", "confidence": 0.88},
                {"type": "FEATURE", "value": "wireless", "confidence": 0.90},
                {"type": "COLOR", "value": "black", "confidence": 0.85}
            ]
        }
        '''
        
        response = client.post(
            "/api/v1/intents/detect",
            json={"text": "I want Sony wireless black headphones"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["entities"]) == 4
        assert all("type" in entity for entity in data["entities"])
        assert all("value" in entity for entity in data["entities"])
        assert all("confidence" in entity for entity in data["entities"])
    
    def test_detect_intent_with_no_entities(self, mock_ollama_client):
        mock_ollama_client.generate.return_value = '''
        {
            "intent": "GREETING",
            "confidence": 0.99,
            "entities": []
        }
        '''
        
        response = client.post(
            "/api/v1/intents/detect",
            json={"text": "Hello!"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["intent"] == "GREETING"
        assert len(data["entities"]) == 0
    
    def test_detect_intent_preserves_original_text(self, mock_ollama_client):
        mock_ollama_client.generate.return_value = '''
        {
            "intent": "SEARCH_PRODUCT",
            "confidence": 0.85,
            "entities": []
        }
        '''
        
        original_text = "Show me affordable laptops"
        response = client.post(
            "/api/v1/intents/detect",
            json={"text": original_text}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["text"] == original_text