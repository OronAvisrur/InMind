from typing import List
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential
from pydantic import BaseModel, Field

class OllamaEmbeddingConfig(BaseModel):
    base_url: str = Field(default="http://ollama:11434")
    model: str = Field(default="nomic-embed-text")
    timeout: int = Field(default=30)

class OllamaEmbeddingError(Exception):
    pass

class OllamaEmbeddingService:
    def __init__(self, config: OllamaEmbeddingConfig):
        self._config = config
        self._client = httpx.AsyncClient(timeout=config.timeout)
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def embed_text(self, text: str) -> List[float]:
        try:
            response = await self._client.post(
                f"{self._config.base_url}/api/embeddings",
                json={
                    "model": self._config.model,
                    "prompt": text
                }
            )
            response.raise_for_status()
            data = response.json()
            return data["embedding"]
        except httpx.HTTPError as e:
            raise OllamaEmbeddingError(f"Failed to generate embedding: {str(e)}")
    
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        embeddings = []
        for text in texts:
            embedding = await self.embed_text(text)
            embeddings.append(embedding)
        return embeddings
    
    async def close(self) -> None:
        await self._client.aclose()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()