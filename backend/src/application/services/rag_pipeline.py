🔷 Phase 5 Step 5d: Create RAG Pipeline Orchestrator
Add the main RAG pipeline that orchestrates retrieval and generation.
📝 Create ONE File
backend/src/application/services/rag_pipeline.py (NEW)
pythonfrom typing import List, Optional
from pydantic import BaseModel, Field

from src.domain.models.rag import RAGRequest, RAGResponse, RetrievedContext
from src.application.services.context_retrieval import ContextRetrievalStrategy
from src.application.services.prompt_template import RAGPromptTemplates
from src.infrastructure.llm.ollama_client import OllamaClient


class RAGPipelineConfig(BaseModel):
    model_name: str = Field(default="llama2")
    temperature: float = Field(default=0.1, ge=0.0, le=1.0)
    max_tokens: int = Field(default=1000, ge=100, le=4000)
    enable_reasoning: bool = Field(default=True)
    enable_self_consistency: bool = Field(default=False)
    consistency_samples: int = Field(default=3, ge=2, le=5)


class RAGPipeline:
    def __init__(
        self,
        retrieval_strategy: ContextRetrievalStrategy,
        llm_client: OllamaClient,
        config: RAGPipelineConfig
    ):
        self._retrieval_strategy = retrieval_strategy
        self._llm_client = llm_client
        self._config = config
        self._prompt_templates = RAGPromptTemplates()
    
    async def process_query(self, request: RAGRequest) -> RAGResponse:
        contexts = await self._retrieve_contexts(request)
        
        if not contexts:
            return self._create_empty_response(request)
        
        reasoning, recommended_products = await self._generate_recommendations(
            request.query,
            contexts,
            request.include_reasoning
        )
        
        confidence = self._calculate_confidence(contexts, reasoning)
        
        return RAGResponse(
            query=request.query,
            recommended_products=recommended_products,
            reasoning=reasoning if request.include_reasoning else None,
            context_used=contexts,
            confidence_score=confidence,
            model_used=self._config.model_name
        )
    
    async def _retrieve_contexts(self, request: RAGRequest) -> List[RetrievedContext]:
        contexts = await self._retrieval_strategy.retrieve_context(
            request.query,
            request
        )
        return contexts
    
    async def _generate_recommendations(
        self,
        query: str,
        contexts: List[RetrievedContext],
        include_reasoning: bool
    ) -> tuple[Optional[str], List]:
        template = self._prompt_templates.get_recommendation_template()
        
        products_context = self._prompt_templates.format_products_context(contexts)
        
        prompt = template.build_full_prompt(
            query=query,
            products_context=products_context
        )
        
        if self._config.enable_self_consistency:
            response = await self._generate_with_self_consistency(prompt)
        else:
            response = await self._llm_client.generate(
                prompt=prompt,
                model=self._config.model_name,
                temperature=self._config.temperature,
                max_tokens=self._config.max_tokens
            )
        
        reasoning = response if include_reasoning else None
        recommended_products = [ctx.product for ctx in contexts]
        
        return reasoning, recommended_products
    
    async def _generate_with_self_consistency(self, prompt: str) -> str:
        responses = []
        
        for _ in range(self._config.consistency_samples):
            response = await self._llm_client.generate(
                prompt=prompt,
                model=self._config.model_name,
                temperature=self._config.temperature + 0.2,
                max_tokens=self._config.max_tokens
            )
            responses.append(response)
        
        return self._select_most_consistent_response(responses)
    
    def _select_most_consistent_response(self, responses: List[str]) -> str:
        if len(responses) == 1:
            return responses[0]
        
        word_counts = []
        for response in responses:
            word_count = len(response.split())
            word_counts.append((response, word_count))
        
        word_counts.sort(key=lambda x: x[1])
        median_idx = len(word_counts) // 2
        
        return word_counts[median_idx][0]
    
    def _calculate_confidence(
        self,
        contexts: List[RetrievedContext],
        reasoning: Optional[str]
    ) -> float:
        if not contexts:
            return 0.0
        
        avg_relevance = sum(ctx.relevance_score for ctx in contexts) / len(contexts)
        
        context_count_factor = min(len(contexts) / 5.0, 1.0)
        
        reasoning_factor = 1.0
        if reasoning:
            reasoning_length = len(reasoning.split())
            if reasoning_length < 20:
                reasoning_factor = 0.7
            elif reasoning_length > 200:
                reasoning_factor = 0.9
        
        confidence = (
            avg_relevance * 0.6 +
            context_count_factor * 0.3 +
            reasoning_factor * 0.1
        )
        
        return min(confidence, 1.0)
    
    def _create_empty_response(self, request: RAGRequest) -> RAGResponse:
        return RAGResponse(
            query=request.query,
            recommended_products=[],
            reasoning="No products found matching your query. Please try different search terms or relax your filters.",
            context_used=[],
            confidence_score=0.0,
            model_used=self._config.model_name
        )
    
    async def compare_products(
        self,
        product_ids: List[str],
        contexts: List[RetrievedContext]
    ) -> str:
        template = self._prompt_templates.get_comparison_template()
        
        products_context = self._prompt_templates.format_products_context(contexts)
        
        prompt = template.build_full_prompt(
            products_context=products_context
        )
        
        response = await self._llm_client.generate(
            prompt=prompt,
            model=self._config.model_name,
            temperature=self._config.temperature,
            max_tokens=self._config.max_tokens
        )
        
        return response