import pytest
import json
from unittest.mock import Mock

from src.application.services.intent_detector import IntentDetectorService, IntentDetectionError
from src.domain.value_objects import IntentType, EntityType
from src.infrastructure.llm import OllamaClient, OllamaConnectionError


class TestIntentDetectorService:
    
    @pytest.fixture
    def mock_ollama_client(self) -> Mock:
        return Mock(spec=OllamaClient)
    
    @pytest.fixture
    def intent_detector(self, mock_ollama_client: Mock) -> IntentDetectorService:
        return IntentDetectorService(mock_ollama_client)
    
    def test_detect_search_product_intent(
        self,
        intent_detector: IntentDetectorService,
        mock_ollama_client: Mock
    ) -> None:
        user_message = "I need wireless headphones under $200"
        
        mock_response = {
            "response": json.dumps({
                "intent": "SEARCH_PRODUCT",
                "confidence": 0.95,
                "entities": [
                    {"type": "PRODUCT_NAME", "value": "headphones", "confidence": 0.9},
                    {"type": "FEATURE", "value": "wireless", "confidence": 0.95},
                    {"type": "PRICE_RANGE", "value": "under $200", "confidence": 0.9}
                ]
            })
        }
        mock_ollama_client.generate.return_value = mock_response
        
        result = intent_detector.detect_intent(user_message)
        
        assert result.intent_type == IntentType.SEARCH_PRODUCT
        assert result.confidence == 0.95
        assert result.raw_text == user_message
        assert len(result.entities) == 3
        
        product_entity = next(e for e in result.entities if e.entity_type == EntityType.PRODUCT_NAME)
        assert product_entity.value == "headphones"
        assert product_entity.confidence == 0.9
        
        feature_entity = next(e for e in result.entities if e.entity_type == EntityType.FEATURE)
        assert feature_entity.value == "wireless"
        
        price_entity = next(e for e in result.entities if e.entity_type == EntityType.PRICE_RANGE)
        assert price_entity.value == "under $200"
    
    def test_detect_recommendation_intent(
        self,
        intent_detector: IntentDetectorService,
        mock_ollama_client: Mock
    ) -> None:
        user_message = "Can you recommend a good laptop for programming?"
        
        mock_response = {
            "response": json.dumps({
                "intent": "GET_RECOMMENDATION",
                "confidence": 0.9,
                "entities": [
                    {"type": "PRODUCT_NAME", "value": "laptop", "confidence": 0.95},
                    {"type": "FEATURE", "value": "for programming", "confidence": 0.8}
                ]
            })
        }
        mock_ollama_client.generate.return_value = mock_response
        
        result = intent_detector.detect_intent(user_message)
        
        assert result.intent_type == IntentType.GET_RECOMMENDATION
        assert result.confidence == 0.9
        assert len(result.entities) == 2
    
    def test_detect_compare_products_intent(
        self,
        intent_detector: IntentDetectorService,
        mock_ollama_client: Mock
    ) -> None:
        user_message = "Compare iPhone 15 and Samsung Galaxy S24"
        
        mock_response = {
            "response": json.dumps({
                "intent": "COMPARE_PRODUCTS",
                "confidence": 0.95,
                "entities": [
                    {"type": "PRODUCT_NAME", "value": "iPhone 15", "confidence": 0.95},
                    {"type": "BRAND", "value": "Apple", "confidence": 0.85},
                    {"type": "PRODUCT_NAME", "value": "Samsung Galaxy S24", "confidence": 0.95},
                    {"type": "BRAND", "value": "Samsung", "confidence": 0.9}
                ]
            })
        }
        mock_ollama_client.generate.return_value = mock_response
        
        result = intent_detector.detect_intent(user_message)
        
        assert result.intent_type == IntentType.COMPARE_PRODUCTS
        assert len(result.entities) == 4
        
        brand_entities = [e for e in result.entities if e.entity_type == EntityType.BRAND]
        assert len(brand_entities) == 2
    
    def test_detect_greeting_intent(
        self,
        intent_detector: IntentDetectorService,
        mock_ollama_client: Mock
    ) -> None:
        user_message = "Hi there!"
        
        mock_response = {
            "response": json.dumps({
                "intent": "GREETING",
                "confidence": 0.95,
                "entities": []
            })
        }
        mock_ollama_client.generate.return_value = mock_response
        
        result = intent_detector.detect_intent(user_message)
        
        assert result.intent_type == IntentType.GREETING
        assert result.confidence == 0.95
        assert len(result.entities) == 0
    
    def test_detect_unknown_intent(
        self,
        intent_detector: IntentDetectorService,
        mock_ollama_client: Mock
    ) -> None:
        user_message = "asdfghjkl"
        
        mock_response = {
            "response": json.dumps({
                "intent": "UNKNOWN",
                "confidence": 0.3,
                "entities": []
            })
        }
        mock_ollama_client.generate.return_value = mock_response
        
        result = intent_detector.detect_intent(user_message)
        
        assert result.intent_type == IntentType.UNKNOWN
        assert result.confidence == 0.3
    
    def test_handles_invalid_intent_type(
        self,
        intent_detector: IntentDetectorService,
        mock_ollama_client: Mock
    ) -> None:
        mock_response = {
            "response": json.dumps({
                "intent": "INVALID_INTENT",
                "confidence": 0.8,
                "entities": []
            })
        }
        mock_ollama_client.generate.return_value = mock_response
        
        result = intent_detector.detect_intent("test message")
        
        assert result.intent_type == IntentType.UNKNOWN
    
    def test_handles_invalid_entity_type(
        self,
        intent_detector: IntentDetectorService,
        mock_ollama_client: Mock
    ) -> None:
        mock_response = {
            "response": json.dumps({
                "intent": "SEARCH_PRODUCT",
                "confidence": 0.9,
                "entities": [
                    {"type": "INVALID_TYPE", "value": "test", "confidence": 0.8},
                    {"type": "PRODUCT_NAME", "value": "laptop", "confidence": 0.9}
                ]
            })
        }
        mock_ollama_client.generate.return_value = mock_response
        
        result = intent_detector.detect_intent("test message")
        
        assert len(result.entities) == 1
        assert result.entities[0].entity_type == EntityType.PRODUCT_NAME
    
    def test_raises_error_on_ollama_connection_failure(
        self,
        intent_detector: IntentDetectorService,
        mock_ollama_client: Mock
    ) -> None:
        mock_ollama_client.generate.side_effect = OllamaConnectionError("Connection failed")
        
        with pytest.raises(IntentDetectionError) as exc_info:
            intent_detector.detect_intent("test message")
        
        assert "LLM service unavailable" in str(exc_info.value)
    
    def test_raises_error_on_invalid_json_response(
        self,
        intent_detector: IntentDetectorService,
        mock_ollama_client: Mock
    ) -> None:
        mock_response = {
            "response": "This is not valid JSON"
        }
        mock_ollama_client.generate.return_value = mock_response
        
        with pytest.raises(IntentDetectionError) as exc_info:
            intent_detector.detect_intent("test message")
        
        assert "Failed to parse LLM response" in str(exc_info.value)
    
    def test_uses_correct_temperature(
        self,
        intent_detector: IntentDetectorService,
        mock_ollama_client: Mock
    ) -> None:
        mock_response = {
            "response": json.dumps({
                "intent": "GREETING",
                "confidence": 0.95,
                "entities": []
            })
        }
        mock_ollama_client.generate.return_value = mock_response
        
        intent_detector.detect_intent("Hello")
        
        call_kwargs = mock_ollama_client.generate.call_args[1]
        assert call_kwargs["temperature"] == 0.1
        assert call_kwargs["format"] == "json"
    
    def test_preserves_raw_text(
        self,
        intent_detector: IntentDetectorService,
        mock_ollama_client: Mock
    ) -> None:
        original_message = "Show me gaming laptops with RTX 4090"
        
        mock_response = {
            "response": json.dumps({
                "intent": "SEARCH_PRODUCT",
                "confidence": 0.9,
                "entities": []
            })
        }
        mock_ollama_client.generate.return_value = mock_response
        
        result = intent_detector.detect_intent(original_message)
        
        assert result.raw_text == original_message