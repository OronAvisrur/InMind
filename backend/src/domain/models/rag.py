from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

from src.domain.value_objects.identifiers import ProductId
from src.domain.models.product import Product


class RetrievedContext(BaseModel):
    product: Product
    relevance_score: float = Field(ge=0.0, le=1.0)
    chunk_text: Optional[str] = None
    chunk_position: Optional[int] = None


class RAGRequest(BaseModel):
    query: str = Field(min_length=1)
    max_results: int = Field(default=5, ge=1, le=20)
    min_relevance: float = Field(default=0.5, ge=0.0, le=1.0)
    include_reasoning: bool = Field(default=True)


class RAGResponse(BaseModel):
    query: str
    recommended_products: List[Product]
    reasoning: Optional[str] = None
    context_used: List[RetrievedContext]
    confidence_score: float = Field(ge=0.0, le=1.0)
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    model_used: str


class PromptContext(BaseModel):
    user_query: str
    retrieved_products: List[RetrievedContext]
    conversation_history: List[str] = Field(default_factory=list)
    system_constraints: Optional[str] = None