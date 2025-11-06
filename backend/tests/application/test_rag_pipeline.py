import pytest
from unittest.mock import AsyncMock, Mock
from datetime import datetime

from src.domain.models.rag import RAGRequest, RAGResponse, RetrievedContext
from src.domain.models.product import Product
from src.domain.value_objects.identifiers import ProductId
from src.application.services.rag_pipeline import RAGPipeline, RAGPipelineConfig
from src.application.services.context_retrieval import VectorSearchStrategy


@pytest.fixture
def mock_retrieval_strategy():
    strategy = Mock(spec=VectorSearchStrategy)
    strategy.retrieve_context = AsyncMock()
    return strategy


@pytest.fixture
def mock_llm_client():
    client = Mock()
    client.generate = AsyncMock()
    return client


@pytest.fixture
def rag_config():
    return RAGPipelineConfig(
        model_name="llama2",
        temperature=0.1,
        max_tokens=1000,
        enable_reasoning=True,
        enable_self_consistency=False
    )


@pytest.fixture
def sample_product():
    return Product(
        id=ProductId.generate(),
        name="Sony WH-1000XM5",
        category="Headphones",
        price=399.99,
        description="Premium noise-canceling wireless headphones",
        features=["Active Noise Canceling", "30-hour battery", "Touch controls"],
        brand="Sony",
        stock=50,
        rating=4.8
    )


@pytest.fixture
def sample_contexts(sample_product):
    return [
        RetrievedContext(
            product=sample_product,
            relevance_score=0.95,
            chunk_text=None,
            chunk_position=None
        )
    ]


@pytest.fixture
def rag_pipeline(mock_retrieval_strategy, mock_llm_client, rag_config):
    return RAGPipeline(
        retrieval_strategy=mock_retrieval_strategy,
        llm_client=mock_llm_client,
        config=rag_config
    )


@pytest.mark.asyncio
async def test_process_query_success(
    rag_pipeline,
    mock_retrieval_strategy,
    mock_llm_client,
    sample_contexts
):
    request = RAGRequest(
        query="I need noise-canceling headphones",
        max_results=5,
        min_relevance=0.5,
        include_reasoning=True
    )
    
    mock_retrieval_strategy.retrieve_context.return_value = sample_contexts
    mock_llm_client.generate.return_value = "I recommend the Sony WH-1000XM5 because it offers excellent noise canceling."
    
    response = await rag_pipeline.process_query(request)
    
    assert isinstance(response, RAGResponse)
    assert response.query == request.query
    assert len(response.recommended_products) == 1
    assert response.recommended_products[0].name == "Sony WH-1000XM5"
    assert response.reasoning is not None
    assert response.confidence_score > 0.0
    assert response.model_used == "llama2"
    
    mock_retrieval_strategy.retrieve_context.assert_called_once()
    mock_llm_client.generate.assert_called_once()


@pytest.mark.asyncio
async def test_process_query_no_contexts(
    rag_pipeline,
    mock_retrieval_strategy,
    mock_llm_client
):
    request = RAGRequest(
        query="nonexistent product xyz123",
        max_results=5,
        min_relevance=0.5
    )
    
    mock_retrieval_strategy.retrieve_context.return_value = []
    
    response = await rag_pipeline.process_query(request)
    
    assert isinstance(response, RAGResponse)
    assert len(response.recommended_products) == 0
    assert response.confidence_score == 0.0
    assert "No products found" in response.reasoning
    
    mock_llm_client.generate.assert_not_called()


@pytest.mark.asyncio
async def test_process_query_without_reasoning(
    rag_pipeline,
    mock_retrieval_strategy,
    mock_llm_client,
    sample_contexts
):
    request = RAGRequest(
        query="wireless headphones",
        max_results=3,
        include_reasoning=False
    )
    
    mock_retrieval_strategy.retrieve_context.return_value = sample_contexts
    mock_llm_client.generate.return_value = "Some reasoning text"
    
    response = await rag_pipeline.process_query(request)
    
    assert response.reasoning is None
    assert len(response.recommended_products) == 1


@pytest.mark.asyncio
async def test_generate_with_self_consistency(
    mock_retrieval_strategy,
    mock_llm_client,
    sample_contexts
):
    config = RAGPipelineConfig(
        enable_self_consistency=True,
        consistency_samples=3
    )
    
    pipeline = RAGPipeline(
        retrieval_strategy=mock_retrieval_strategy,
        llm_client=mock_llm_client,
        config=config
    )
    
    request = RAGRequest(query="test query")
    
    mock_retrieval_strategy.retrieve_context.return_value = sample_contexts
    mock_llm_client.generate.side_effect = [
        "Short response",
        "This is a medium length response with more details",
        "Very long response with extensive details and comprehensive explanations"
    ]
    
    response = await pipeline.process_query(request)
    
    assert mock_llm_client.generate.call_count == 3
    assert response.reasoning is not None


@pytest.mark.asyncio
async def test_calculate_confidence_high_relevance(rag_pipeline, sample_contexts):
    confidence = rag_pipeline._calculate_confidence(
        sample_contexts,
        "Detailed reasoning with good explanation"
    )
    
    assert 0.8 <= confidence <= 1.0


@pytest.mark.asyncio
async def test_calculate_confidence_low_relevance(rag_pipeline):
    low_relevance_contexts = [
        RetrievedContext(
            product=Mock(),
            relevance_score=0.3,
            chunk_text=None,
            chunk_position=None
        )
    ]
    
    confidence = rag_pipeline._calculate_confidence(
        low_relevance_contexts,
        "Short reasoning"
    )
    
    assert confidence < 0.5


@pytest.mark.asyncio
async def test_calculate_confidence_empty_contexts(rag_pipeline):
    confidence = rag_pipeline._calculate_confidence([], None)
    assert confidence == 0.0


@pytest.mark.asyncio
async def test_compare_products(
    rag_pipeline,
    mock_llm_client,
    sample_contexts
):
    product_ids = ["id1", "id2"]
    mock_llm_client.generate.return_value = "Product 1 is better for X, Product 2 is better for Y"
    
    comparison = await rag_pipeline.compare_products(product_ids, sample_contexts)
    
    assert isinstance(comparison, str)
    assert len(comparison) > 0
    mock_llm_client.generate.assert_called_once()


@pytest.mark.asyncio
async def test_select_most_consistent_response(rag_pipeline):
    responses = [
        "Very short",
        "This is a medium length response",
        "Long response with many words and details"
    ]
    
    selected = rag_pipeline._select_most_consistent_response(responses)
    
    assert selected == "This is a medium length response"


@pytest.mark.asyncio
async def test_rag_pipeline_config_defaults():
    config = RAGPipelineConfig()
    
    assert config.model_name == "llama2"
    assert config.temperature == 0.1
    assert config.max_tokens == 1000
    assert config.enable_reasoning is True
    assert config.enable_self_consistency is False
    assert config.consistency_samples == 3


@pytest.mark.asyncio
async def test_process_query_integration_flow(
    rag_pipeline,
    mock_retrieval_strategy,
    mock_llm_client,
    sample_contexts
):
    request = RAGRequest(
        query="best wireless headphones under $400",
        max_results=3,
        min_relevance=0.7
    )
    
    mock_retrieval_strategy.retrieve_context.return_value = sample_contexts
    mock_llm_client.generate.return_value = "Based on your budget and requirements, the Sony WH-1000XM5 is perfect."
    
    response = await rag_pipeline.process_query(request)
    
    assert response.query == request.query
    assert len(response.context_used) == 1
    assert response.context_used[0].relevance_score == 0.95
    assert response.confidence_score > 0.5
    assert isinstance(response.generated_at, datetime)
