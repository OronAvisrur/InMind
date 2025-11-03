from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from ..value_objects import ProductIdentifier


class Product(BaseModel):
    id: ProductIdentifier = Field(default_factory=ProductIdentifier)
    name: str = Field(min_length=1, max_length=500)
    description: str = Field(min_length=1)
    category: str = Field(min_length=1, max_length=200)
    price: float = Field(gt=0.0)
    brand: Optional[str] = Field(None, max_length=200)
    features: List[str] = Field(default_factory=list)
    specifications: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)
    image_urls: List[str] = Field(default_factory=list)
    stock_quantity: int = Field(ge=0, default=0)
    is_available: bool = Field(default=True)
    rating: Optional[float] = Field(None, ge=0.0, le=5.0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @field_validator("name", "description", "category")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        return v.strip()

    @field_validator("tags", "features")
    @classmethod
    def clean_list_items(cls, v: List[str]) -> List[str]:
        return [item.strip() for item in v if item.strip()]

    def to_document(self) -> str:
        features_text = " ".join(self.features)
        tags_text = " ".join(self.tags)
        specs_text = " ".join(f"{k}: {v}" for k, v in self.specifications.items())
        
        return f"""
        Product: {self.name}
        Brand: {self.brand or 'N/A'}
        Category: {self.category}
        Price: ${self.price}
        Description: {self.description}
        Features: {features_text}
        Tags: {tags_text}
        Specifications: {specs_text}
        """.strip()

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Wireless Headphones Pro",
                "description": "Premium noise-cancelling wireless headphones",
                "category": "Electronics",
                "price": 299.99,
                "brand": "AudioTech",
                "features": ["Noise Cancellation", "30-hour battery", "Bluetooth 5.0"],
                "tags": ["wireless", "premium", "audio"],
            }
        }