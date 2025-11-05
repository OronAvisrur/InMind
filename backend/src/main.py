from fastapi import FastAPI, HTTPException
from src.infrastructure.config.settings import get_settings, Settings
from functools import lru_cache
from typing import Dict, Any

@lru_cache()
def get_cached_settings() -> Settings:
    return get_settings()

settings = get_cached_settings()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="AI-powered product recommendation system using NLP, RAG, and local LLM"
)


@app.get("/")
def read_root() -> Dict[str, str]:
    return {
        "message": "InMind API",
        "version": "0.1.0",
        "status": "running"
    }


@app.get("/health")
def health_check() -> Dict[str, Any]:
    current_settings = get_cached_settings()
    return {
        "status": "healthy",
        "service": current_settings.app_name,
        "version": "0.1.0",
        "debug": current_settings.debug
    }


@app.get("/ollama/health")
def ollama_health() -> Dict[str, Any]:
    from src.infrastructure.llm import OllamaClient
    
    current_settings = get_cached_settings()
    
    try:
        client = OllamaClient(current_settings.ollama)
        is_healthy = client.health_check()
        
        if is_healthy:
            models = client.list_models()
            client.close()
            return {
                "status": "healthy",
                "ollama_host": current_settings.ollama.host,
                "available_models": models,
                "configured_model": current_settings.ollama.model
            }
        else:
            client.close()
            return {
                "status": "unhealthy",
                "ollama_host": current_settings.ollama.host,
                "error": "Ollama service not responding"
            }
    
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Ollama service unavailable: {str(e)}")