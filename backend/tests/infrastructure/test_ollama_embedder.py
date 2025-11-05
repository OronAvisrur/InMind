import pytest
from unittest.mock import AsyncMock, patch
from httpx import Response
from src.infrastructure.embedding.ollama_embedder import (
    OllamaEmbeddingService,
    OllamaEmbeddingConfig,
    OllamaEmbeddingError
)

@pytest.fixture
def config():
    return OllamaEmbeddingConfig(
        base_url="http://localhost:11434",
        model="nomic-embed-text",
        timeout=30
    )

@pytest.fixture
def mock_embedding_response():
    return {
        "embedding": [0.1, 0.2, 0.3, 0.4, 0.5]
    }

@pytest.mark.asyncio
async def test_embed_text_success(config, mock_embedding_response):
    service = OllamaEmbeddingService(config)
    
    with patch.object(service._client, 'post') as mock_post:
        mock_response = AsyncMock(spec=Response)
        mock_response.raise_for_status = AsyncMock()
        mock_response.json.return_value = mock_embedding_response
        mock_post.return_value = mock_response
        
        result = await service.embed_text("test text")
        
        assert result == [0.1, 0.2, 0.3, 0.4, 0.5]
        assert len(result) == 5
        mock_post.assert_called_once()
    
    await service.close()

@pytest.mark.asyncio
async def test_embed_text_with_custom_model(mock_embedding_response):
    config = OllamaEmbeddingConfig(
        base_url="http://localhost:11434",
        model="custom-embed-model",
        timeout=30
    )
    service = OllamaEmbeddingService(config)
    
    with patch.object(service._client, 'post') as mock_post:
        mock_response = AsyncMock(spec=Response)
        mock_response.raise_for_status = AsyncMock()
        mock_response.json.return_value = mock_embedding_response
        mock_post.return_value = mock_response
        
        await service.embed_text("test")
        
        call_args = mock_post.call_args
        assert call_args[1]['json']['model'] == "custom-embed-model"
    
    await service.close()

@pytest.mark.asyncio
async def test_embed_batch_success(config):
    service = OllamaEmbeddingService(config)
    texts = ["text1", "text2", "text3"]
    
    with patch.object(service, 'embed_text') as mock_embed:
        mock_embed.side_effect = [
            [0.1, 0.2],
            [0.3, 0.4],
            [0.5, 0.6]
        ]
        
        result = await service.embed_batch(texts)
        
        assert len(result) == 3
        assert result[0] == [0.1, 0.2]
        assert result[1] == [0.3, 0.4]
        assert result[2] == [0.5, 0.6]
        assert mock_embed.call_count == 3
    
    await service.close()

@pytest.mark.asyncio
async def test_embed_text_http_error(config):
    service = OllamaEmbeddingService(config)
    
    with patch.object(service._client, 'post') as mock_post:
        mock_post.side_effect = Exception("Connection failed")
        
        with pytest.raises(OllamaEmbeddingError):
            await service.embed_text("test")
    
    await service.close()

@pytest.mark.asyncio
async def test_context_manager():
    config = OllamaEmbeddingConfig()
    
    async with OllamaEmbeddingService(config) as service:
        assert service._client is not None
    
    assert service._client.is_closed

@pytest.mark.asyncio
async def test_embed_empty_string(config, mock_embedding_response):
    service = OllamaEmbeddingService(config)
    
    with patch.object(service._client, 'post') as mock_post:
        mock_response = AsyncMock(spec=Response)
        mock_response.raise_for_status = AsyncMock()
        mock_response.json.return_value = mock_embedding_response
        mock_post.return_value = mock_response
        
        result = await service.embed_text("")
        assert isinstance(result, list)
    
    await service.close()

@pytest.mark.asyncio
async def test_embed_batch_empty_list(config):
    service = OllamaEmbeddingService(config)
    
    result = await service.embed_batch([])
    
    assert result == []
    await service.close()