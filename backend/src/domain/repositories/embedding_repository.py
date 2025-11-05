from typing import Protocol, List

class EmbeddingRepository(Protocol):
    async def embed_text(self, text: str) -> List[float]:
        ...
    
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        ...
    
    async def close(self) -> None:
        ...