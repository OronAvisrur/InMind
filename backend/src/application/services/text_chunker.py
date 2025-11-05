from typing import List
from pydantic import BaseModel, Field

class ChunkConfig(BaseModel):
    chunk_size: int = Field(default=200, gt=0)
    chunk_overlap: int = Field(default=50, ge=0)

class TextChunk(BaseModel):
    text: str
    start_index: int
    end_index: int

class TextChunker:
    def __init__(self, config: ChunkConfig):
        self._config = config
    
    def chunk_text(self, text: str) -> List[TextChunk]:
        if not text or len(text) <= self._config.chunk_size:
            return [TextChunk(text=text, start_index=0, end_index=len(text))]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = min(start + self._config.chunk_size, len(text))
            
            if end < len(text):
                last_space = text.rfind(' ', start, end)
                if last_space > start:
                    end = last_space
            
            chunk_text = text[start:end].strip()
            if chunk_text:
                chunks.append(TextChunk(
                    text=chunk_text,
                    start_index=start,
                    end_index=end
                ))
            
            start = end - self._config.chunk_overlap
            if start >= len(text):
                break
        
        return chunks