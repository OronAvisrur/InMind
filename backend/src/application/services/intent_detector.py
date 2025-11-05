from typing import Dict, Any
import json
from datetime import datetime

from src.domain.models import DetectedIntent
from src.domain.value_objects import IntentType, EntityType, Entity
from src.infrastructure.llm import OllamaClient, OllamaConnectionError, OllamaTimeoutError


class IntentDetectionError(Exception):
    pass


class IntentDetectorService:
    def __init__(self, ollama_client: OllamaClient):
        self.ollama = ollama_client
        self.system_prompt = self._build_system_prompt()
    
    def _build_system_prompt(self) -> str:
        return """You are an intent classification expert for an e-commerce product recommendation system.

Your task: Analyze user messages and return JSON with intent classification and extracted entities.

Available intents:
- SEARCH_PRODUCT: User wants to find specific products
- GET_RECOMMENDATION: User asks for product suggestions
- COMPARE_PRODUCTS: User wants to compare multiple products
- ASK_FEATURE: User inquires about product features
- ASK_PRICE: User asks about pricing
- CLARIFICATION: User needs more information
- GREETING: User greets the system
- THANK_YOU: User expresses gratitude
- UNKNOWN: Cannot determine intent

Available entities:
- PRODUCT_NAME: Specific product mentioned
- CATEGORY: Product category (electronics, clothing, etc.)
- BRAND: Brand name
- FEATURE: Product feature (wireless, waterproof, etc.)
- PRICE_RANGE: Price constraints
- COLOR: Color preference
- SIZE: Size specification
- QUANTITY: Number of items

Return JSON format:
{
  "intent": "INTENT_NAME",
  "confidence": 0.95,
  "entities": [
    {"type": "ENTITY_TYPE", "value": "extracted_value", "confidence": 0.9}
  ]
}

Examples:

User: "I need wireless headphones under $200"
{
  "intent": "SEARCH_PRODUCT",
  "confidence": 0.95,
  "entities": [
    {"type": "PRODUCT_NAME", "value": "headphones", "confidence": 0.9},
    {"type": "FEATURE", "value": "wireless", "confidence": 0.95},
    {"type": "PRICE_RANGE", "value": "under $200", "confidence": 0.9}
  ]
}

User: "Can you recommend a good laptop for programming?"
{
  "intent": "GET_RECOMMENDATION",
  "confidence": 0.9,
  "entities": [
    {"type": "PRODUCT_NAME", "value": "laptop", "confidence": 0.95},
    {"type": "FEATURE", "value": "for programming", "confidence": 0.8}
  ]
}

User: "What's the battery life of the Sony WH-1000XM5?"
{
  "intent": "ASK_FEATURE",
  "confidence": 0.95,
  "entities": [
    {"type": "FEATURE", "value": "battery life", "confidence": 0.95},
    {"type": "BRAND", "value": "Sony", "confidence": 0.9},
    {"type": "PRODUCT_NAME", "value": "WH-1000XM5", "confidence": 0.95}
  ]
}

User: "Compare iPhone 15 and Samsung Galaxy S24"
{
  "intent": "COMPARE_PRODUCTS",
  "confidence": 0.95,
  "entities": [
    {"type": "PRODUCT_NAME", "value": "iPhone 15", "confidence": 0.95},
    {"type": "BRAND", "value": "Apple", "confidence": 0.85},
    {"type": "PRODUCT_NAME", "value": "Samsung Galaxy S24", "confidence": 0.95},
    {"type": "BRAND", "value": "Samsung", "confidence": 0.9}
  ]
}

User: "Hi there!"
{
  "intent": "GREETING",
  "confidence": 0.95,
  "entities": []
}

Now analyze the user message and return only the JSON response."""
    
    def detect_intent(self, text: str) -> DetectedIntent:
        try:
            response = self.ollama.generate(
                prompt=f"User message: \"{text}\"\n\nAnalyze and return JSON:",
                system=self.system_prompt,
                temperature=0.1,
                format="json"
            )
            
            result = self._parse_response(response, text)
            return result
        
        except (OllamaConnectionError, OllamaTimeoutError) as e:
            raise IntentDetectionError(f"LLM service unavailable: {e}")
        except Exception as e:
            raise IntentDetectionError(f"Intent detection failed: {e}")
    
    def _parse_response(self, response: Dict[str, Any], original_text: str) -> DetectedIntent:
        try:
            response_text = response.get("response", "")
            parsed = json.loads(response_text)
            
            intent_str = parsed.get("intent", "UNKNOWN")
            try:
                intent_type = IntentType(intent_str)
            except ValueError:
                intent_type = IntentType.UNKNOWN
            
            confidence = float(parsed.get("confidence", 0.5))
            
            entities = []
            for entity_data in parsed.get("entities", []):
                entity_type_str = entity_data.get("type", "")
                try:
                    entity_type = EntityType(entity_type_str)
                    entity = Entity(
                        entity_type=entity_type,
                        value=entity_data.get("value", ""),
                        confidence=float(entity_data.get("confidence", 0.5))
                    )
                    entities.append(entity)
                except ValueError:
                    continue
            
            return DetectedIntent(
                intent_type=intent_type,
                confidence=confidence,
                entities=entities,
                raw_text=original_text
            )
        
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            raise IntentDetectionError(f"Failed to parse LLM response: {e}")