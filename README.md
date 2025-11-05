# InMind

AI-powered product recommendation system that analyzes chat conversations using NLP, RAG, and LLM to understand user needs and recommend products.

## Project Overview

InMind reads user chat conversations, extracts intent and entities using NLP, performs similarity search with RAG (Retrieval-Augmented Generation), and leverages local LLM (Ollama) to provide intelligent product recommendations.

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
│   │   │   ├── models/            # Product, User, Conversation, Message, DetectedIntent, Entity
│   │   │   ├── value_objects/     # Type-safe IDs, IntentType, EntityType, MessageRole enums
│   │   │   └── repositories/      # Abstract interfaces (Protocols)
│   │   │
│   │   ├── application/           # Use cases and business rules
│   │   │   └── services/
│   │   │       └── intent_detector.py  # ✅ IntentDetectorService
│   │   │
│   │   ├── infrastructure/        # External integrations
│   │   │   ├── config/
│   │   │   │   └── settings.py    # ✅ Pydantic settings
│   │   │   └── llm/
│   │   │       └── ollama_client.py  # ✅ OllamaClient with retry logic
│   │   │
│   │   └── api/                   # API routes and endpoints (coming soon)
│   │
│   └── tests/
│       ├── domain/                # Domain model tests
│       └── application/
│           └── test_intent_detector.py  # ✅ 11 unit tests
│
└── frontend/                      # Frontend service (coming soon)
    └── README.md
```

## Architecture

**Microservices Architecture:**
- **Backend Service**: FastAPI application with NLP and RAG capabilities
- **Ollama Service**: Local LLM inference engine 
- **Frontend Service**: React/Next.js UI (coming soon)
- **ChromaDB Service**: Vector database for embeddings (coming soon)

**Clean Architecture with SOLID Principles:**
- **Domain Layer**: Pure business logic, framework-agnostic
- **Application Layer**: Use cases, orchestration, services
- **Infrastructure Layer**: Ollama, ChromaDB, external APIs
- **API Layer**: FastAPI endpoints, request/response schemas

**Key Design Patterns:**
- Repository Pattern for data access abstraction
- Strategy Pattern for interchangeable NLP/LLM components
- Dependency Injection via constructor injection
- Protocol (Interface) for Dependency Inversion Principle

## Tech Stack

- **Language**: Python 3.11+
- **Web Framework**: FastAPI
- **Validation**: Pydantic V2
- **LLM**: Ollama (local inference) 
- **Vector DB**: ChromaDB (for RAG) - Coming soon
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

# Pull LLM model (first time only)
docker exec -it inmind-ollama ollama pull llama2

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

# Run specific test file
pytest tests/application/test_intent_detector.py -v

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
2. **Intent Detection**: LLM analyzes message using few-shot prompting to extract:
   - Intent type (SEARCH_PRODUCT, GET_RECOMMENDATION, etc.)
   - Entities (product_name: "headphones", price_range: "under $200", feature: "wireless")
   - Confidence scores
3. **RAG Search**: System searches vector database for relevant products using embeddings 
4. **LLM Recommendation**: LLM generates personalized product recommendations based on context 
5. **Response**: System returns top product matches with explanations

## Project Status

- ✅ **Phase 1**: Project structure, FastAPI skeleton, Docker setup
- ✅ **Phase 2**: Domain models, value objects, repository protocols, comprehensive tests
- ✅ **Phase 3**: NLP module - Intent & Entity detection with Ollama
  - ✅ Step 1: Ollama infrastructure with Docker Compose
  - ✅ Step 2: IntentDetectorService with few-shot prompting
- 📋 **Phase 4**: Vector database & embeddings (ChromaDB)
- 📋 **Phase 5**: RAG system implementation
- 📋 **Phase 6**: Conversation engine with memory
- 📋 **Phase 7**: REST API endpoints
- 📋 **Phase 8**: Testing & deployment

## Features Implemented

### Ollama Client Infrastructure ✅
- OllamaClient with retry logic (exponential backoff, 3 attempts)
- Health checks and model discovery
- Context manager support
- Custom exceptions (OllamaConnectionError, OllamaTimeoutError)
- Support for both `generate()` and `chat()` methods

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

### Configuration Management ✅
- Pydantic-settings for type-safe configuration
- Environment variable support
- OllamaSettings (host, model, timeout, temperature)
- Application settings (app_name, debug, api_host, api_port)

## Domain Models

### Core Entities
- **Product**: Products to be recommended (features, price, category, etc.)
- **User**: User sessions and preferences
- **Conversation**: Multi-turn chat dialogues
- **Message**: Individual chat messages (user/assistant/system)
- **DetectedIntent**: Intent classification result from NLP analysis
- **Entity**: Extracted entities with confidence scores

### Value Objects
- **Identifiers**: Type-safe UUIDs for all entities
- **IntentType**: Enum for user intents
- **EntityType**: Enum for extracted entities
- **MessageRole**: USER, ASSISTANT, SYSTEM

## API Endpoints

### Current Endpoints
- `GET /` - API information and version
- `GET /health` - Backend service health check
- `GET /ollama/health` - Ollama service health check with model listing

### Coming Soon (Phase 7)
- `POST /api/v1/chat` - Send chat message and get recommendations
- `POST /api/v1/intents/detect` - Detect intent from text
- `GET /api/v1/products` - List products
- `GET /api/v1/products/{id}` - Get product details
- `POST /api/v1/products/search` - Search products with filters

## Environment Variables
```bash
# Ollama Configuration
OLLAMA_HOST=http://ollama:11434
OLLAMA_MODEL=llama2
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

## Troubleshooting

### Ollama service not responding
```bash
# Check if Ollama is running
docker-compose ps

# Check Ollama logs
docker-compose logs ollama

# Restart Ollama
docker-compose restart ollama

# Pull model again
docker exec -it inmind-ollama ollama pull llama2
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

### Tests failing
```bash
# Ensure all dependencies are installed
docker exec -it inmind-backend pip list

# Run tests with verbose output
docker exec -it inmind-backend pytest tests/ -v -s
```

## Contributing

1. Follow SOLID principles
2. Write self-documenting code (no comments/docstrings)
3. Add type hints everywhere
4. Write unit tests for all new services
5. Use Pydantic models for data validation
6. Follow clean architecture separation

## License

MIT

## Acknowledgments

- Ollama for local LLM inference
- FastAPI for the web framework
- Pydantic for data validation