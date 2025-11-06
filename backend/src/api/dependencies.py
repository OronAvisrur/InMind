from functools import lru_cache
from src.infrastructure.config.settings import Settings
from src.infrastructure.llm.ollama_client import OllamaClient, OllamaConfig
from src.infrastructure.embedding.ollama_embedder import OllamaEmbeddingService, OllamaEmbeddingConfig
from src.infrastructure.vector_store.chroma_repository import ChromaVectorRepository, ChromaConfig
from src.infrastructure.conversation.in_memory_state_repository import InMemoryStateRepository
from src.infrastructure.conversation.in_memory_memory_repository import InMemoryMemoryRepository
from src.application.services.intent_detector import IntentDetectorService
from src.application.services.text_chunker import TextChunker, ChunkingConfig
from src.application.services.product_ingestion import ProductIngestionService
from src.application.services.prompt_template import RAGPromptTemplates
from src.application.services.context_retrieval import HybridRetrievalStrategy
from src.application.services.rag_pipeline import RAGPipeline
from src.application.services.conversation_manager import ConversationManager


@lru_cache()
def get_settings() -> Settings:
    return Settings()


def get_ollama_client() -> OllamaClient:
    settings = get_settings()
    config = OllamaConfig(
        base_url=settings.ollama_host,
        model=settings.ollama_model,
        timeout=settings.ollama_timeout,
        temperature=settings.ollama_temperature
    )
    return OllamaClient(config)


def get_embedding_service() -> OllamaEmbeddingService:
    settings = get_settings()
    config = OllamaEmbeddingConfig(
        base_url=settings.ollama_host,
        model=settings.ollama_embedding_model,
        timeout=settings.ollama_timeout
    )
    return OllamaEmbeddingService(config)


def get_vector_repository() -> ChromaVectorRepository:
    config = ChromaConfig(
        collection_name="products",
        persist_directory="./data/chroma"
    )
    embedding_service = get_embedding_service()
    return ChromaVectorRepository(config, embedding_service)


def get_state_repository() -> InMemoryStateRepository:
    return InMemoryStateRepository()


def get_memory_repository() -> InMemoryMemoryRepository:
    return InMemoryMemoryRepository()


def get_intent_detector() -> IntentDetectorService:
    ollama_client = get_ollama_client()
    return IntentDetectorService(ollama_client)


def get_text_chunker() -> TextChunker:
    config = ChunkingConfig(
        chunk_size=500,
        chunk_overlap=50,
        min_chunk_size=100
    )
    return TextChunker(config)


def get_product_ingestion_service() -> ProductIngestionService:
    vector_repo = get_vector_repository()
    text_chunker = get_text_chunker()
    return ProductIngestionService(vector_repo, text_chunker)


def get_rag_pipeline() -> RAGPipeline:
    vector_repo = get_vector_repository()
    ollama_client = get_ollama_client()
    retrieval_strategy = HybridRetrievalStrategy(vector_repo)
    prompt_templates = RAGPromptTemplates()
    return RAGPipeline(retrieval_strategy, ollama_client, prompt_templates)


def get_conversation_manager() -> ConversationManager:
    intent_detector = get_intent_detector()
    rag_pipeline = get_rag_pipeline()
    state_repo = get_state_repository()
    memory_repo = get_memory_repository()
    return ConversationManager(intent_detector, rag_pipeline, state_repo, memory_repo)
