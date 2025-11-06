from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class HealthResponse(BaseModel):
    status: str = Field(description="Service health status")
    service: str = Field(description="Service name")
    timestamp: datetime = Field(description="Current timestamp")
    
    
class OllamaHealthResponse(BaseModel):
    status: str = Field(description="Ollama service status")
    models: list[str] = Field(description="Available models")
    timestamp: datetime = Field(description="Current timestamp")


class ErrorResponse(BaseModel):
    error: str = Field(description="Error type")
    message: str = Field(description="Error message")
    details: Optional[dict] = Field(default=None, description="Additional error details")
    timestamp: datetime = Field(description="Error timestamp")


class SuccessResponse(BaseModel):
    success: bool = Field(description="Operation success status")
    message: str = Field(description="Success message")
    data: Optional[dict] = Field(default=None, description="Response data")