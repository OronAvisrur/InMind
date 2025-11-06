from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
import httpx
from src.api.schemas import HealthResponse, OllamaHealthResponse, ErrorResponse
from src.api.dependencies import get_settings
from src.infrastructure.config.settings import Settings


router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="healthy",
        service="InMind Backend",
        timestamp=datetime.utcnow()
    )


@router.get("/ollama", response_model=OllamaHealthResponse)
async def ollama_health_check(settings: Settings = Depends(get_settings)):
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{settings.ollama_host}/api/tags")
            response.raise_for_status()
            data = response.json()
            models = [model["name"] for model in data.get("models", [])]
            
            return OllamaHealthResponse(
                status="healthy",
                models=models,
                timestamp=datetime.utcnow()
            )
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Ollama service unavailable: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to check Ollama health: {str(e)}"
        )
