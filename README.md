# InMind

AI-powered product recommendation system that analyzes chat conversations using NLP, RAG, and LLM to understand user needs and recommend products.

## Project Overview

InMind reads user chat conversations, extracts intent and entities using NLP, performs similarity search with RAG (Retrieval-Augmented Generation), and leverages local LLM (Ollama) to provide intelligent product recommendations with conversation memory and state management.

## Project Structure
```
in-mind/
├── docker-compose.yml             # Microservices orchestration
├── .env.example                   # Environment variables template
├── .gitignore
├── README.md
│
├── backend/                       # Backend service
│   ├── Dockerfile
│   ├── pyproject.toml
│   ├── src/
│   │   ├── __init__.py
│   │   ├── main.py                # FastAPI application entry point
│   │   │
│   │   ├── domain/                # Core business logic (zero dependencies)
│   │   │   ├── models/            # Business entities
│   │   │   │   ├── product.py
│   │   │   │   ├── user.py
│   │   │   │   ├── conversation.py
│   │   │   │   ├── message.py
│   │   │   │   ├── intent.py
│   │   │   │   ├── entity.py
│   │   │   │   ├── search_result.py
│   │   │   │   ├── text_chunk.py
│   │   │   │   ├── rag.py
│   │   │   │   ├── conversation_state.py        # ✅ NEW Phase 6
│   │   │   │   └── memory.py                     # ✅ NEW Phase 6
│   │   │   ├── value_objects/     # Type-safe IDs, IntentType, EntityType, MessageRole enums
│   │   │   └── repositories/      # Abstract interfaces (Protocols)
│   │   │       ├── embedding_repository.py
│   │   │       ├── vector_repository.py
│   │   │       ├── conversation_repository.py
│   │   │       └── conversation_state_repository.py  # ✅ NEW Phase 6
│   │   │
│   │   ├── application/           # Use cases and business rules
│   │   │   └── services/
│   │   │       ├── intent_detector.py           # ✅ IntentDetectorService
│   │   │       ├── text_chunker.py              # ✅ TextChunker
│   │   │       ├── product_ingestion.py         # ✅ ProductIngestionService
│   │   │       ├── prompt_template.py           # ✅ RAGPromptTemplates
│   │   │       ├── context_retrieval.py         # ✅ VectorSearchStrategy, HybridRetrievalStrategy
│   │   │       ├── rag_pipeline.py              # ✅ RAGPipeline orchestrator
│   │   │       └── conversation_manager.py      # ✅ NEW Phase 6
│   │   │
│   │   ├── infrastructure/        # External integrations
│   │   │   ├── config/
│   │   │   │   └── settings.py                  # ✅ Pydantic settings
│   │   │   ├── llm/
│   │   │   │   └── ollama_client.py             # ✅ OllamaClient with retry logic
│   │   │   ├── embedding/
│   │   │   │   └── ollama_embedder.py           # ✅ OllamaEmbeddingService
│   │   │   ├── vector_store/
│   │   │   │   └── chroma_repository.py         # ✅ ChromaVectorRepository
│   │   │   └── conversation/                    # ✅ NEW Phase 6
│   │   │       ├── in_memory_state_repository.py
│   │   │       └── in_memory_memory_repository.py
│   │   │
│   │   └── api/                   # API routes and endpoints (Phase 7)
│   │
│   └── tests/
│       ├── domain/
│       │   ├── test_conversation_state.py       # ✅ NEW 14 tests
│       │   └── test_memory.py                   # ✅ NEW 16 tests
│       ├── application/
│       │   ├── test_intent_detector.py          # ✅ 11 tests
│       │   ├── test_text_chunker.py             # ✅ 10 tests
│       │   ├── test_product_ingestion.py        # ✅ 10 tests
│       │   ├── test_rag_pipeline.py             # ✅ 11 tests
│       │   └── test_conversation_manager.py     # ✅ NEW 13 tests
│       └── infrastructure/
│           ├── test_ollama_embedder.py          # ✅ 8 tests
│           ├── test_chroma_repository.py        # ✅ 10 tests
│           ├── test_in_memory_state_repository.py    # ✅ NEW 12 tests
│           └── test_in_memory_memory_repository.py   # ✅ NEW 11 tests
│
└── frontend/                      # Frontend service (coming soon)
    └── README.md
```

## Architecture

**Microservices Architecture:**
- **Backend Service**: FastAPI application with NLP, RAG, and conversation management
- **Ollama Service**: Local LLM inference engine 
- **ChromaDB**: Vector database for embeddings (integrated)
- **Frontend Service**: React/Next.js UI (coming soon)

**Clean Architecture with SOLID Principles:**
- **Domain Layer**: Pure business logic, framework-agnostic
- **Application Layer**: Use cases, orchestration, services
- **Infrastructure Layer**: Ollama, ChromaDB, external APIs
- **API Layer**: FastAPI endpoints, request/response schemas

**Key Design Patterns:**
- Repository Pattern for data access abstraction
- Strategy Pattern for interchangeable NLP/LLM components
- State Machine Pattern for dialog flow management
- Dependency Injection via constructor injection
- Protocol (Interface) for Dependency Inversion Principle

## Tech Stack

- **Language**: Python 3.11+
- **Web Framework**: FastAPI
- **Validation**: Pydantic V2
- **LLM**: Ollama (local inference) with gemma3:270m
- **Embeddings**: Ollama nomic-embed-text
- **Vector DB**: ChromaDB with cosine similarity
- **HTTP Client**: httpx with tenacity retry logic
- **Containerization**: Docker & Docker Compose

## Quick Start

### Prerequisites
- Docker & Docker Compose installed
- 8GB+ RAM recommended for LLM models
- Git

### Installation
```bash
# Clone the repository
git clone <your-repo-url>
cd in-mind

# Start all services
docker-compose up --build -d

# Pull LLM models (first time only)
docker exec -it inmind-ollama ollama pull gemma3:270m
docker exec -it inmind-ollama ollama pull nomic-embed-text

# Check services are running
docker-compose ps

# View logs
docker-compose logs -f backend
```

### Access the Application

- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Ollama API**: http://localhost:11434

### Test Endpoints
```bash
# Root endpoint
curl http://localhost:8000/

# Health check
curl http://localhost:8000/health

# Ollama health check
curl http://localhost:8000/ollama/health
```

## Development

### Running Tests
```bash
# Enter backend container
docker exec -it inmind-backend bash

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=term-missing

# Run specific test suites
pytest tests/application/ -v
pytest tests/infrastructure/ -v
pytest tests/domain/ -v

# Exit container
exit
```

### Code Quality
```bash
# Inside backend container
black src/ tests/
mypy src/
ruff check src/
```

### Development Workflow
```bash
# Start services in development mode (with hot reload)
docker-compose up

# Make changes to src/ files - server auto-reloads

# Restart services after dependency changes
docker-compose down
docker-compose up --build
```

## How It Works

1. **User Input**: User sends a chat message (e.g., "I need wireless headphones under $200")
2. **Conversation State**: System initializes or retrieves conversation state and memory
3. **Intent Detection**: LLM analyzes message using few-shot prompting to extract:
   - Intent type (SEARCH_PRODUCT, GET_RECOMMENDATION, etc.)
   - Entities (product_name: "headphones", price_range: "under $200", feature: "wireless")
   - Confidence scores
4. **State Transition**: Conversation manager transitions dialog state based on detected intent
5. **Entity Collection**: Extracted entities are stored in conversation context
6. **Embedding Generation**: User query is converted to vector embeddings using Ollama
7. **Vector Search**: ChromaDB performs similarity search to find relevant products
8. **Context Retrieval**: Retrieval strategy applies diversity filtering and multi-factor reranking
9. **RAG Pipeline**: Orchestrates retrieval and generation with chain-of-thought prompting
10. **Memory Management**: Turn history maintained with sliding window
11. **LLM Recommendation**: LLM generates personalized recommendations based on retrieved context and conversation history
12. **Response**: System returns recommendations with explanations, updates state, and stores turn in memory

## Project Status

- ✅ **Phase 1**: Project structure, FastAPI skeleton, Docker setup
- ✅ **Phase 2**: Domain models, value objects, repository protocols, comprehensive tests
- ✅ **Phase 3**: NLP module - Intent & Entity detection with Ollama
  - ✅ Ollama infrastructure with Docker Compose
  - ✅ IntentDetectorService with few-shot prompting
- ✅ **Phase 4**: Vector database & embeddings (ChromaDB) - **COMPLETE**
  - ✅ Step 1: Embedding service with Ollama (9 commits)
  - ✅ Step 2: Vector repository with ChromaDB (8 commits)
  - ✅ Step 3: Product ingestion pipeline (6 commits)
- ✅ **Phase 5**: RAG system implementation - **COMPLETE**
  - ✅ Step 1: RAG domain models (RetrievedContext, RAGRequest, RAGResponse)
  - ✅ Step 2: Prompt template system with few-shot examples
  - ✅ Step 3: Context retrieval strategies (Vector + Hybrid)
  - ✅ Step 4: RAG pipeline orchestrator
  - ✅ Step 5: Comprehensive unit tests (11 tests)
  - ✅ Step 6: Module exports
- ✅ **Phase 6**: Conversation engine with memory - **COMPLETE**
  - ✅ Step 1: Conversation state and memory domain models (14 commits)
  - ✅ Step 2: Conversation state repository protocols (2 commits)
  - ✅ Step 3: In-memory repository implementations (3 commits)
  - ✅ Step 4: Conversation manager orchestrator (2 commits)
  - ✅ Step 5: Comprehensive unit tests (66 tests total)
- 📋 **Phase 7**: REST API endpoints
- 📋 **Phase 8**: Testing & deployment

## Features Implemented

### Ollama Client Infrastructure ✅
- OllamaClient with retry logic (exponential backoff, 3 attempts)
- Health checks and model discovery
- Context manager support
- Custom exceptions (OllamaConnectionError, OllamaTimeoutError)
- Support for both `generate()` and `chat()` methods

### Embedding Service ✅
- OllamaEmbeddingService with async operations
- Support for single text and batch embedding generation
- Retry logic with exponential backoff (3 attempts)
- Context manager for resource cleanup
- Configurable embedding model (nomic-embed-text)
- EmbeddingRepository protocol for dependency inversion
- 8 comprehensive unit tests

### Vector Database ✅
- ChromaVectorRepository with persistent storage
- Cosine similarity search for product matching
- Metadata filtering support
- Product addition, deletion, and count operations
- SearchResult model with relevance scores (0.0-1.0)
- VectorRepository protocol for abstraction
- 10 comprehensive unit tests

### Text Chunking ✅
- TextChunker service for long descriptions
- Configurable chunk size and overlap
- Smart word boundary detection
- Position tracking for each chunk
- ChunkConfig for customization
- 10 comprehensive unit tests

### Product Ingestion Pipeline ✅
- ProductIngestionService orchestrating full pipeline
- Batch and single product ingestion
- Product search with embedding generation
- Product removal and count retrieval
- Metadata extraction and storage
- Dependency injection architecture
- 10 comprehensive unit tests

### Intent Detection Service ✅
- Few-shot prompting with 5 comprehensive examples
- Support for 9 intent types:
  - SEARCH_PRODUCT
  - GET_RECOMMENDATION
  - COMPARE_PRODUCTS
  - ASK_FEATURE
  - ASK_PRICE
  - CLARIFICATION
  - GREETING
  - THANK_YOU
  - UNKNOWN
- Entity extraction with 8 entity types:
  - PRODUCT_NAME
  - CATEGORY
  - BRAND
  - FEATURE
  - PRICE_RANGE
  - COLOR
  - SIZE
  - QUANTITY
- Structured JSON output with confidence scores
- Comprehensive error handling
- 11 unit tests with 100% pass rate

### RAG System ✅
- **RAG Domain Models**:
  - RetrievedContext: Product results with relevance scores
  - RAGRequest: Query parameters with filters
  - RAGResponse: Recommendations with reasoning and confidence
  - PromptContext: LLM prompt assembly
- **Prompt Template System**:
  - Flexible template manager with system/user prompts
  - Few-shot examples for recommendation generation
  - Product comparison templates
  - Context formatting helpers
- **Context Retrieval Strategies**:
  - VectorSearchStrategy with diversity filtering
  - HybridRetrievalStrategy with multi-factor reranking
  - Category/brand/price-based diversity scoring
  - Relevance, price, and rating weight balancing
- **RAG Pipeline Orchestrator**:
  - Full retrieval + generation workflow
  - Chain-of-thought prompting
  - Optional self-consistency sampling (multiple inference passes)
  - Confidence score calculation
  - Product comparison support
  - Empty result handling with fallbacks
- **11 comprehensive unit tests**

### Conversation Engine ✅
- **Conversation State Management**:
  - ConversationState model with dialog state machine
  - 8 dialog states: INITIAL, GREETING, COLLECTING_INFO, SEARCHING, RECOMMENDING, COMPARING, CLARIFYING, CLOSING
  - 4 conversation statuses: ACTIVE, PAUSED, COMPLETED, ABANDONED
  - ConversationContext for entity collection and search history
  - Automatic activity tracking and state transitions
  - 14 unit tests for state models
- **Conversation Memory**:
  - ConversationMemory with sliding window history
  - ConversationTurn tracking with user/assistant exchanges
  - Context window extraction with token estimation
  - Configurable max_turns for memory management
  - Processing time tracking per turn
  - 16 unit tests for memory models
- **Repository Implementations**:
  - InMemoryStateRepository for conversation state persistence
  - InMemoryMemoryRepository for turn history storage
  - Active conversation filtering by user
  - Automatic cleanup of abandoned conversations
  - 23 unit tests for repositories
- **Conversation Manager Orchestrator**:
  - Full conversation flow orchestration
  - Integration of intent detection + RAG pipeline
  - Automatic state transitions based on intent
  - Entity collection from detected intents
  - Memory management with context window
  - Multi-turn conversation support
  - Greeting, clarification, and closing dialog handlers
  - Filter building from collected entities
  - 13 unit tests with mocks

### Configuration Management ✅
- Pydantic-settings for type-safe configuration
- Environment variable support
- OllamaSettings (host, model, embedding_model, timeout, temperature)
- Application settings (app_name, debug, api_host, api_port)

## Domain Models

### Core Entities
- **Product**: Products to be recommended (features, price, category, etc.)
- **User**: User sessions and preferences
- **Conversation**: Multi-turn chat dialogues
- **Message**: Individual chat messages (user/assistant/system)
- **DetectedIntent**: Intent classification result from NLP analysis
- **Entity**: Extracted entities with confidence scores
- **SearchResult**: Vector search results with products and relevance scores
- **RetrievedContext**: RAG context with products and relevance
- **RAGRequest**: User query with retrieval parameters
- **RAGResponse**: Recommendations with reasoning and confidence
- **ConversationState**: Dialog state and status tracking (NEW Phase 6)
- **ConversationMemory**: Turn history with sliding window (NEW Phase 6)
- **ConversationTurn**: Single user-assistant exchange (NEW Phase 6)

### Value Objects
- **Identifiers**: Type-safe UUIDs for all entities
- **IntentType**: Enum for user intents
- **EntityType**: Enum for extracted entities
- **MessageRole**: USER, ASSISTANT, SYSTEM
- **TextChunk**: Text chunks with position metadata
- **DialogState**: Enum for conversation flow states (NEW Phase 6)
- **ConversationStatus**: Enum for conversation lifecycle (NEW Phase 6)

## API Endpoints

### Current Endpoints
- `GET /` - API information and version
- `GET /health` - Backend service health check
- `GET /ollama/health` - Ollama service health check with model listing

### Coming Soon (Phase 7)
- `POST /api/v1/chat` - Send chat message and get recommendations
- `POST /api/v1/conversations/start` - Start new conversation
- `GET /api/v1/conversations/{id}` - Get conversation state
- `POST /api/v1/conversations/{id}/end` - End conversation
- `POST /api/v1/intents/detect` - Detect intent from text
- `GET /api/v1/products` - List products
- `GET /api/v1/products/{id}` - Get product details
- `POST /api/v1/products/search` - Search products with filters
- `POST /api/v1/products/ingest` - Ingest products into vector database

## Environment Variables
```bash
# Ollama Configuration
OLLAMA_HOST=http://ollama:11434
OLLAMA_MODEL=gemma3:270m
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
OLLAMA_TIMEOUT=60
OLLAMA_MAX_RETRIES=3
OLLAMA_TEMPERATURE=0.1

# Application
APP_NAME=InMind
DEBUG=false
API_HOST=0.0.0.0
API_PORT=8000
```

## Docker Services

### Backend Service
- FastAPI application
- Port: 8000
- Hot reload enabled in development
- Depends on Ollama service

### Ollama Service
- Local LLM inference
- Port: 11434
- Persistent volume for models
- Privileged mode for GPU access
- Models: gemma3:270m, nomic-embed-text

## Test Coverage

**Total Tests: 126**
- Domain Models: 40 tests (30 new in Phase 6)
- Application Services: 45 tests (13 new in Phase 6)
- Infrastructure: 41 tests (23 new in Phase 6)

**Test Breakdown:**
- Conversation State Models: 14 tests
- Conversation Memory Models: 16 tests
- In-Memory State Repository: 12 tests
- In-Memory Memory Repository: 11 tests
- Conversation Manager: 13 tests
- Intent Detection: 11 tests
- Text Chunking: 10 tests
- Product Ingestion: 10 tests
- Embedding Service: 8 tests
- Vector Repository: 10 tests
- RAG Pipeline: 11 tests

All tests passing with comprehensive coverage of:
- Business logic
- Service integration
- Error handling
- Edge cases
- Async operations
- State transitions
- Memory management

## Troubleshooting

### Ollama service not responding
```bash
# Check if Ollama is running
docker-compose ps

# Check Ollama logs
docker-compose logs ollama

# Restart Ollama
docker-compose restart ollama

# Pull models again
docker exec -it inmind-ollama ollama pull gemma3:270m
docker exec -it inmind-ollama ollama pull nomic-embed-text
```

### Backend service errors
```bash
# Check backend logs
docker-compose logs backend

# Restart backend
docker-compose restart backend

# Rebuild backend
docker-compose up --build backend
```

### ChromaDB persistence issues
```bash
# Check if data directory exists
ls -la data/chroma

# Ensure proper permissions
chmod -R 755 data/

# Restart services
docker-compose restart backend
```

### Tests failing
```bash
# Ensure all dependencies are installed
docker exec -it inmind-backend pip list

# Run tests with verbose output
docker exec -it inmind-backend pytest tests/ -v -s

# Run specific test suite
docker exec -it inmind-backend pytest tests/infrastructure/ -v
```

## Contributing

1. Follow SOLID principles
2. Write self-documenting code (no comments/docstrings)
3. Add type hints everywhere
4. Write unit tests for all new services
5. Use Pydantic models for data validation
6. Follow clean architecture separation
7. One file per commit for better tracking

## License

MIT

## Acknowledgments

- Ollama for local LLM inference
- ChromaDB for vector database
- FastAPI for the web framework
- Pydantic for data validation