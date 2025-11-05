import pytest
from src.domain.models import DetectedIntent, IntentDetectionResult
from src.domain.value_objects import IntentType, EntityType, Entity


class TestIntent:
    def test_create_detected_intent(self):
        entity = Entity(
            type=EntityType.PRODUCT_NAME,
            value="laptop",
            confidence=0.95,
        )
        
        intent = DetectedIntent(
            intent_type=IntentType.SEARCH_PRODUCT,
            confidence=0.98,
            entities=[entity],
            raw_query="I need a laptop",
        )
        
        assert intent.intent_type == IntentType.SEARCH_PRODUCT
        assert len(intent.entities) == 1
        assert intent.confidence == 0.98

    def test_get_entities_by_type(self):
        entities = [
            Entity(type=EntityType.PRODUCT_NAME, value="laptop", confidence=0.9),
            Entity(type=EntityType.BRAND, value="Dell", confidence=0.85),
            Entity(type=EntityType.PRODUCT_NAME, value="computer", confidence=0.7),
        ]
        
        intent = DetectedIntent(
            intent_type=IntentType.SEARCH_PRODUCT,
            confidence=0.95,
            entities=entities,
            raw_query="Dell laptop computer",
        )
        
        product_entities = intent.get_entities_by_type("product_name")
        assert len(product_entities) == 2
        assert product_entities[0].value == "laptop"

    def test_has_entity_type(self):
        entities = [
            Entity(type=EntityType.CATEGORY, value="Electronics", confidence=0.9),
            Entity(type=EntityType.BRAND, value="Sony", confidence=0.85),
        ]
        
        intent = DetectedIntent(
            intent_type=IntentType.FILTER_PRODUCTS,
            confidence=0.92,
            entities=entities,
            raw_query="Show me Sony electronics",
        )
        
        assert intent.has_entity_type("category") is True
        assert intent.has_entity_type("brand") is True
        assert intent.has_entity_type("price_range") is False

    def test_entity_validation_empty_value(self):
        with pytest.raises(ValueError):
            Entity(
                type=EntityType.PRODUCT_NAME,
                value="",
                confidence=0.9,
            )

    def test_entity_strips_whitespace(self):
        entity = Entity(
            type=EntityType.BRAND,
            value="  Apple  ",
            confidence=0.9,
        )
        assert entity.value == "Apple"

    def test_intent_detection_result(self):
        primary = DetectedIntent(
            intent_type=IntentType.SEARCH_PRODUCT,
            confidence=0.95,
            entities=[],
            raw_query="looking for headphones",
        )
        
        alternative = DetectedIntent(
            intent_type=IntentType.GET_RECOMMENDATION,
            confidence=0.75,
            entities=[],
            raw_query="looking for headphones",
        )
        
        result = IntentDetectionResult(
            primary_intent=primary,
            alternative_intents=[alternative],
            processing_time_ms=125.5,
        )
        
        assert result.primary_intent.intent_type == IntentType.SEARCH_PRODUCT
        assert len(result.alternative_intents) == 1
        assert result.processing_time_ms == 125.5

    def test_multiple_entity_types_extraction(self):
        entities = [
            Entity(type=EntityType.PRODUCT_NAME, value="headphones", confidence=0.95),
            Entity(type=EntityType.FEATURE, value="wireless", confidence=0.88),
            Entity(type=EntityType.COLOR, value="black", confidence=0.82),
            Entity(type=EntityType.BRAND, value="Sony", confidence=0.90),
        ]
        
        intent = DetectedIntent(
            intent_type=IntentType.SEARCH_PRODUCT,
            confidence=0.96,
            entities=entities,
            raw_query="I want wireless black Sony headphones",
        )
        
        assert len(intent.entities) == 4
        assert intent.get_entities_by_type("feature")[0].value == "wireless"
        assert intent.get_entities_by_type("color")[0].value == "black"