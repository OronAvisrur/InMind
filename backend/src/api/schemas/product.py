from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ProductResponse(BaseModel):
    id: str = Field(description="Product identifier")
    name: str = Field(description="Product name")
    description: str = Field(description="Product description")
    price: float = Field(ge=0.0, description="Product price")
    category: str = Field(description="Product category")
    brand: str = Field(description="Product brand")
    rating: float = Field(ge=0.0, le=5.0, description="Product rating")
    features: list[str] = Field(description="Product features")
    stock_quantity: int = Field(ge=0, description="Available stock")
    created_at: datetime = Field(description="Product creation timestamp")


class ProductListResponse(BaseModel):
    products: list[ProductResponse] = Field(description="List of products")
    total: int = Field(description="Total number of products")
    page: int = Field(ge=1, description="Current page number")
    page_size: int = Field(ge=1, le=100, description="Items per page")


class ProductSearchRequest(BaseModel):
    query: Optional[str] = Field(default=None, description="Search query")
    category: Optional[str] = Field(default=None, description="Filter by category")
    brand: Optional[str] = Field(default=None, description="Filter by brand")
    min_price: Optional[float] = Field(default=None, ge=0.0, description="Minimum price")
    max_price: Optional[float] = Field(default=None, ge=0.0, description="Maximum price")
    min_rating: Optional[float] = Field(default=None, ge=0.0, le=5.0, description="Minimum rating")
    limit: int = Field(default=10, ge=1, le=50, description="Maximum results to return")


class ProductSearchResponse(BaseModel):
    products: list[ProductResponse] = Field(description="Matching products")
    query: Optional[str] = Field(description="Search query used")
    total_results: int = Field(description="Total matching products")
    timestamp: datetime = Field(description="Search timestamp")


class ProductIngestRequest(BaseModel):
    name: str = Field(min_length=1, max_length=200, description="Product name")
    description: str = Field(min_length=1, max_length=5000, description="Product description")
    price: float = Field(gt=0.0, description="Product price")
    category: str = Field(min_length=1, max_length=100, description="Product category")
    brand: str = Field(min_length=1, max_length=100, description="Product brand")
    rating: float = Field(ge=0.0, le=5.0, description="Product rating")
    features: list[str] = Field(min_length=1, description="Product features list")
    stock_quantity: int = Field(ge=0, description="Available stock quantity")


class ProductIngestResponse(BaseModel):
    product_id: str = Field(description="Created product identifier")
    status: str = Field(description="Ingestion status")
    message: str = Field(description="Status message")
    timestamp: datetime = Field(description="Ingestion timestamp")