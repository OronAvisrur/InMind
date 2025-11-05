import pytest
from unittest.mock import Mock, patch, MagicMock
from src.infrastructure.vector_store.chroma_repository import (
    ChromaVectorRepository,
    ChromaConfig
)
from src.domain.models.product import Product
from src.domain.models.search_result import SearchResult

@pytest.fixture
def config():
    return ChromaConfig(
        persist_directory="./test_data/chroma",
        collection_name="test_products"
    )

@pytest.fixture
def mock_collection():
    collection = Mock()
    collection.count.return_value = 0
    return collection

@pytest.fixture
def mock_chroma_client(mock_collection):
    with patch('src.infrastructure.vector_store.chroma_repository.chromadb.Client') as mock_client:
        client_instance = Mock()
        client_instance.get_or_create_collection.return_value = mock_collection
        mock_client.return_value = client_instance
        yield mock_client

@pytest.fixture
def sample_products():
    return [
        Product(
            id="prod-1",
            name="Wireless Headphones",
            description="High quality wireless headphones with noise cancellation",
            category="Electronics",
            price=199.99,
            brand="AudioTech",
            features=["wireless", "noise-cancelling", "bluetooth"]
        ),
        Product(
            id="prod-2",
            name="Running Shoes",
            description="Comfortable running shoes for daily training",
            category="Sports",
            price=89.99,
            brand="SportX",
            features=["lightweight", "breathable"]
        )
    ]

@pytest.mark.asyncio
async def test_add_products_success(config, mock_chroma_client, mock_collection, sample_products):
    repo = ChromaVectorRepository(config)
    
    await repo.add_products(sample_products)
    
    mock_collection.add.assert_called_once()
    call_args = mock_collection.add.call_args[1]
    
    assert len(call_args["ids"]) == 2
    assert call_args["ids"][0] == "prod-1"
    assert call_args["ids"][1] == "prod-2"
    assert len(call_args["documents"]) == 2
    assert len(call_args["metadatas"]) == 2

@pytest.mark.asyncio
async def test_add_products_empty_list(config, mock_chroma_client, mock_collection):
    repo = ChromaVectorRepository(config)
    
    await repo.add_products([])
    
    mock_collection.add.assert_not_called()

@pytest.mark.asyncio
async def test_search_success(config, mock_chroma_client, mock_collection):
    mock_collection.query.return_value = {
        "ids": [["prod-1"]],
        "documents": [["High quality wireless headphones"]],
        "metadatas": [[{
            "name": "Wireless Headphones",
            "category": "Electronics",
            "price": 199.99,
            "brand": "AudioTech",
            "features": "wireless,noise-cancelling"
        }]],
        "distances": [[0.15]]
    }
    
    repo = ChromaVectorRepository(config)
    query_embedding = [0.1, 0.2, 0.3]
    
    results = await repo.search(query_embedding, top_k=5)
    
    assert len(results) == 1
    assert isinstance(results[0], SearchResult)
    assert results[0].product.name == "Wireless Headphones"
    assert results[0].score == 0.85
    assert results[0].chunk_text == "High quality wireless headphones"

@pytest.mark.asyncio
async def test_search_with_filters(config, mock_chroma_client, mock_collection):
    mock_collection.query.return_value = {
        "ids": [["prod-1"]],
        "documents": [["Product description"]],
        "metadatas": [[{"name": "Product", "category": "Electronics", "price": 99.99, "brand": "", "features": ""}]],
        "distances": [[0.2]]
    }
    
    repo = ChromaVectorRepository(config)
    query_embedding = [0.1, 0.2, 0.3]
    filters = {"category": "Electronics"}
    
    results = await repo.search(query_embedding, top_k=3, filters=filters)
    
    mock_collection.query.assert_called_once()
    call_args = mock_collection.query.call_args[1]
    assert call_args["where"] == filters
    assert call_args["n_results"] == 3

@pytest.mark.asyncio
async def test_search_empty_results(config, mock_chroma_client, mock_collection):
    mock_collection.query.return_value = {
        "ids": [[]],
        "documents": [[]],
        "metadatas": [[]],
        "distances": [[]]
    }
    
    repo = ChromaVectorRepository(config)
    query_embedding = [0.1, 0.2, 0.3]
    
    results = await repo.search(query_embedding)
    
    assert len(results) == 0

@pytest.mark.asyncio
async def test_delete_product(config, mock_chroma_client, mock_collection):
    repo = ChromaVectorRepository(config)
    
    await repo.delete_product("prod-1")
    
    mock_collection.delete.assert_called_once_with(ids=["prod-1"])

@pytest.mark.asyncio
async def test_get_product_count(config, mock_chroma_client, mock_collection):
    mock_collection.count.return_value = 42
    
    repo = ChromaVectorRepository(config)
    
    count = await repo.get_product_count()
    
    assert count == 42
    mock_collection.count.assert_called_once()

@pytest.mark.asyncio
async def test_search_score_normalization(config, mock_chroma_client, mock_collection):
    mock_collection.query.return_value = {
        "ids": [["prod-1"]],
        "documents": [["Test product"]],
        "metadatas": [[{"name": "Test", "category": "Test", "price": 10.0, "brand": "", "features": ""}]],
        "distances": [[1.5]]
    }
    
    repo = ChromaVectorRepository(config)
    results = await repo.search([0.1, 0.2, 0.3])
    
    assert results[0].score >= 0.0
    assert results[0].score <= 1.0
