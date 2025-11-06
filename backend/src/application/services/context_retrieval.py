from typing import List, Protocol
from pydantic import BaseModel, Field

from src.domain.models.rag import RetrievedContext, RAGRequest
from src.domain.models.search_result import SearchResult
from src.domain.repositories.vector_repository import VectorRepository
from src.domain.repositories.embedding_repository import EmbeddingRepository


class ContextRetrievalStrategy(Protocol):
    async def retrieve_context(
        self, 
        query: str, 
        request: RAGRequest
    ) -> List[RetrievedContext]:
        ...


class RetrievalConfig(BaseModel):
    max_results: int = Field(default=10, ge=1, le=50)
    min_relevance: float = Field(default=0.5, ge=0.0, le=1.0)
    diversity_threshold: float = Field(default=0.8, ge=0.0, le=1.0)
    include_metadata: bool = Field(default=True)


class VectorSearchStrategy:
    def __init__(
        self,
        vector_repository: VectorRepository,
        embedding_service: EmbeddingRepository,
        config: RetrievalConfig
    ):
        self._vector_repository = vector_repository
        self._embedding_service = embedding_service
        self._config = config
    
    async def retrieve_context(
        self, 
        query: str, 
        request: RAGRequest
    ) -> List[RetrievedContext]:
        query_embedding = await self._embedding_service.embed_text(query)
        
        max_results = min(request.max_results, self._config.max_results)
        
        search_results = await self._vector_repository.search(
            query_embedding=query_embedding,
            top_k=max_results * 2,
            min_score=request.min_relevance
        )
        
        filtered_results = [
            result for result in search_results 
            if result.score >= request.min_relevance
        ]
        
        diverse_results = self._apply_diversity_filter(filtered_results)
        
        contexts = [
            self._convert_to_context(result)
            for result in diverse_results[:max_results]
        ]
        
        return contexts
    
    def _apply_diversity_filter(
        self, 
        results: List[SearchResult]
    ) -> List[SearchResult]:
        if not results or len(results) <= 1:
            return results
        
        diverse_results = [results[0]]
        
        for result in results[1:]:
            is_diverse = all(
                self._calculate_diversity(result, existing) >= self._config.diversity_threshold
                for existing in diverse_results
            )
            
            if is_diverse:
                diverse_results.append(result)
        
        return diverse_results
    
    def _calculate_diversity(
        self, 
        result1: SearchResult, 
        result2: SearchResult
    ) -> float:
        if result1.product.category != result2.product.category:
            return 1.0
        
        if result1.product.brand != result2.product.brand:
            return 0.9
        
        price_diff = abs(result1.product.price - result2.product.price)
        if price_diff > 100:
            return 0.8
        
        return 0.6
    
    def _convert_to_context(self, result: SearchResult) -> RetrievedContext:
        return RetrievedContext(
            product=result.product,
            relevance_score=result.score,
            chunk_text=None,
            chunk_position=None
        )


class HybridRetrievalStrategy:
    def __init__(
        self,
        vector_strategy: VectorSearchStrategy,
        config: RetrievalConfig
    ):
        self._vector_strategy = vector_strategy
        self._config = config
    
    async def retrieve_context(
        self, 
        query: str, 
        request: RAGRequest
    ) -> List[RetrievedContext]:
        vector_contexts = await self._vector_strategy.retrieve_context(
            query, 
            request
        )
        
        reranked_contexts = self._rerank_by_multiple_factors(vector_contexts)
        
        return reranked_contexts[:request.max_results]
    
    def _rerank_by_multiple_factors(
        self, 
        contexts: List[RetrievedContext]
    ) -> List[RetrievedContext]:
        scored_contexts = []
        
        for ctx in contexts:
            relevance_weight = 0.7
            price_weight = 0.2
            rating_weight = 0.1
            
            relevance_score = ctx.relevance_score * relevance_weight
            
            price_score = self._normalize_price_score(ctx.product.price) * price_weight
            
            rating_score = (ctx.product.rating / 5.0) * rating_weight
            
            final_score = relevance_score + price_score + rating_score
            
            scored_contexts.append((ctx, final_score))
        
        scored_contexts.sort(key=lambda x: x[1], reverse=True)
        
        return [ctx for ctx, _ in scored_contexts]
    
    def _normalize_price_score(self, price: float) -> float:
        if price <= 50:
            return 1.0
        elif price <= 200:
            return 0.8
        elif price <= 500:
            return 0.6
        else:
            return 0.4