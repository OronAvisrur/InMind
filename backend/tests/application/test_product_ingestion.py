import pytest
from unittest.mock import AsyncMock, Mock
from src.application.services.product_ingestion import ProductIngestionService
from src.domain.models.product import Product
from src.domain.models.search_result import SearchResult

@pytest.fixture
def mock_embedding_service():
    service = Mock()
    service.embed_text = AsyncMock(return_value=[0.1, 0.2, 0.3, 0.4, 0.5])
    return service

@pytest.fixture
def mock_vector_repository():
    repo = Mock()
    repo.add_products = AsyncMock()
    repo.delete_product = AsyncMock()
    repo.get_product_count = AsyncMock(return_value=0)
    repo.search = AsyncMock(return_value=[])
    return repo

@pytest.fixture
def ingestion_service(mock_embedding_service, mock_vector_repository):
    return ProductIngestionService(
        embedding_service=mock_embedding_service,
        vector_repository=mock_vector_repository
    )

@pytest.fixture
def sample_products():
    return [
        Product(
            id="prod-1",
            name="Laptop",
            description="High performance laptop",
            category="Electronics",
            price=999.99
        ),
        Product(
            id="prod-2",
            name="Mouse",
            description="Wireless mouse",
            category="Electronics",
            price=29.99
        )
    ]

@pytest.mark.asyncio
async def test_ingest_products_success(ingestion_service, mock_vector_repository, sample_products):
    count = await ingestion_service.ingest_products(sample_products)
    
    assert count == 2
    mock_vector_repository.add_products.assert_called_once_with(sample_products)

@pytest.mark.asyncio
async def test_ingest_products_empty_list(ingestion_service, mock_vector_repository):
    count = await ingestion_service.ingest_products([])
    
    assert count == 0
    mock_vector_repository.add_products.assert_not_called()

@pytest.mark.asyncio
async def test_ingest_single_product(ingestion_service, mock_vector_repository, sample_products):
    product = sample_products[0]
    
    await ingestion_service.ingest_product(product)
    
    mock_vector_repository.add_products.assert_called_once_with([product])

@pytest.mark.asyncio
async def test_remove_product(ingestion_service, mock_vector_repository):
    product_id = "prod-1"
    
    await ingestion_service.remove_product(product_id)
    
    mock_vector_repository.delete_product.assert_called_once_with(product_id)

@pytest.mark.asyncio
async def test_get_total_products(ingestion_service, mock_vector_repository):
    mock_vector_repository.get_product_count.return_value = 42
    
    count = await ingestion_service.get_total_products()
    
    assert count == 42
    mock_vector_repository.get_product_count.assert_called_once()

@pytest.mark.asyncio
async def test_search_products_success(ingestion_service, mock_embedding_service, mock_vector_repository):
    mock_search_result = SearchResult(
        product=Product(
            id="prod-1",
            name="Laptop",
            description="High performance laptop",
            category="Electronics",
            price=999.99
        ),
        score=0.95,
        chunk_text="High performance laptop"
    )
    mock_vector_repository.search.return_value = [mock_search_result]
    
    results = await ingestion_service.search_products("laptop", top_k=5)
    
    assert len(results) == 1
    assert results[0].product.name == "Laptop"
    mock_embedding_service.embed_text.assert_called_once_with("laptop")
    mock_vector_repository.search.assert_called_once()

@pytest.mark.asyncio
async def test_search_products_with_filters(ingestion_service, mock_embedding_service, mock_vector_repository):
    filters = {"category": "Electronics"}
    
    await ingestion_service.search_products("laptop", top_k=10, filters=filters)
    
    call_args = mock_vector_repository.search.call_args[1]
    assert call_args["top_k"] == 10
    assert call_args["filters"] == filters

@pytest.mark.asyncio
async def test_search_products_empty_results(ingestion_service, mock_embedding_service, mock_vector_repository):
    mock_vector_repository.search.return_value = []
    
    results = await ingestion_service.search_products("nonexistent")
    
    assert len(results) == 0
    mock_embedding_service.embed_text.assert_called_once()

@pytest.mark.asyncio
async def test_search_uses_embedding_service(ingestion_service, mock_embedding_service, mock_vector_repository):
    query_text = "wireless headphones"
    expected_embedding = [0.1, 0.2, 0.3, 0.4, 0.5]
    mock_embedding_service.embed_text.return_value = expected_embedding
    
    await ingestion_service.search_products(query_text)
    
    mock_embedding_service.embed_text.assert_called_once_with(query_text)
    call_args = mock_vector_repository.search.call_args[1]
    assert call_args["query_embedding"] == expected_embedding

@pytest.mark.asyncio
async def test_dependency_injection(mock_embedding_service, mock_vector_repository):
    service = ProductIngestionService(
        embedding_service=mock_embedding_service,
        vector_repository=mock_vector_repository
    )
    
    assert service._embedding_service == mock_embedding_service
    assert service._vector_repository == mock_vector_repository