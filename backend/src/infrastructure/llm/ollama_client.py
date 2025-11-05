from typing import Dict, Any, Optional, List
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import json

from src.infrastructure.config.settings import OllamaSettings


class OllamaConnectionError(Exception):
    pass


class OllamaTimeoutError(Exception):
    pass


class OllamaClient:
    def __init__(self, settings: OllamaSettings):
        self.settings = settings
        self.base_url = settings.host
        self.model = settings.model
        self.timeout = settings.timeout
        self.client = httpx.Client(timeout=self.timeout)
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.ConnectError))
    )
    def generate(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        system: Optional[str] = None,
        format: Optional[str] = None
    ) -> Dict[str, Any]:
        temp = temperature if temperature is not None else self.settings.temperature
        
        payload: Dict[str, Any] = {
            "model": self.model,
            "prompt": prompt,
            "temperature": temp,
            "stream": False
        }
        
        if system:
            payload["system"] = system
        
        if format:
            payload["format"] = format
        
        try:
            response = self.client.post(
                f"{self.base_url}/api/generate",
                json=payload
            )
            response.raise_for_status()
            return response.json()
        
        except httpx.TimeoutException as e:
            raise OllamaTimeoutError(f"Ollama request timed out: {e}")
        except httpx.ConnectError as e:
            raise OllamaConnectionError(f"Cannot connect to Ollama: {e}")
        except httpx.HTTPStatusError as e:
            raise OllamaConnectionError(f"Ollama HTTP error: {e}")
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        format: Optional[str] = None
    ) -> Dict[str, Any]:
        temp = temperature if temperature is not None else self.settings.temperature
        
        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temp,
            "stream": False
        }
        
        if format:
            payload["format"] = format
        
        try:
            response = self.client.post(
                f"{self.base_url}/api/chat",
                json=payload
            )
            response.raise_for_status()
            return response.json()
        
        except httpx.TimeoutException as e:
            raise OllamaTimeoutError(f"Ollama chat request timed out: {e}")
        except httpx.ConnectError as e:
            raise OllamaConnectionError(f"Cannot connect to Ollama: {e}")
        except httpx.HTTPStatusError as e:
            raise OllamaConnectionError(f"Ollama HTTP error: {e}")
    
    def health_check(self) -> bool:
        try:
            response = self.client.get(f"{self.base_url}/api/tags")
            return response.status_code == 200
        except Exception:
            return False
    
    def list_models(self) -> List[str]:
        try:
            response = self.client.get(f"{self.base_url}/api/tags")
            response.raise_for_status()
            data = response.json()
            return [model["name"] for model in data.get("models", [])]
        except Exception as e:
            raise OllamaConnectionError(f"Failed to list models: {e}")
    
    def close(self):
        self.client.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()