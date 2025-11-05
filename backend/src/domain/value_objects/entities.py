from enum import Enum
from typing import Dict, Any
from pydantic import BaseModel, Field, field_validator


class IntentType(str, Enum):
    SEARCH_PRODUCT = "search_product"
    GET_RECOMMENDATION = "get_recommendation"
    FILTER_PRODUCTS = "filter_products"
    COMPARE_PRODUCTS = "compare_products"
    ASK_DETAILS = "ask_details"
    GENERAL_QUERY = "general_query"
    GREETING = "greeting"
    UNKNOWN = "unknown"


class EntityType(str, Enum):
    PRODUCT_NAME = "product_name"
    CATEGORY = "category"
    PRICE_RANGE = "price_range"
    BRAND = "brand"
    FEATURE = "feature"
    COLOR = "color"
    SIZE = "size"


class Entity(BaseModel):
    type: EntityType
    value: str
    confidence: float = Field(ge=0.0, le=1.0)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("value")
    @classmethod
    def value_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Entity value cannot be empty")
        return v.strip()


class PriceRange(BaseModel):
    min_price: float = Field(ge=0.0)
    max_price: float = Field(ge=0.0)

    @field_validator("max_price")
    @classmethod
    def max_greater_than_min(cls, v: float, info) -> float:
        if "min_price" in info.data and v < info.data["min_price"]:
            raise ValueError("max_price must be greater than or equal to min_price")
        return v


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"