# InMind

AI-powered product recommendation system that analyzes chat conversations using NLP, RAG, and LLM to understand user needs and recommend products.

## Project Overview

InMind reads user chat conversations, extracts intent and entities using NLP, performs similarity search with RAG (Retrieval-Augmented Generation), and leverages local LLM (Ollama) to provide intelligent product recommendations.

## Project Structure
```
inmind-project/
├── src/
│   ├── __init__.py
│   ├── main.py                    # FastAPI application entry point
│   ├── domain/                    # Core business logic (zero dependencies)
│   │   ├── models/                # Product, User, Conversation, Intent entities
│   │   ├── value_objects/         # Identifiers, IntentType, EntityType, enums
│   │   └── repositories/          # Abstract interfaces (Protocols)
│   ├── application/               # Use cases and business rules
│   │   └── services/              # IntentDetector, RAG pipeline (coming soon)
│   ├── infrastructure/            # External integrations
│   │   └── persistence/           # ChromaDB, Ollama implementations (coming soon)
│   └── api/                       # API routes and endpoints
│       ├── routes/
│       └── schemas/
├── tests/
│   └── domain/                    # Domain model tests
├── pyproject.toml
├── Dockerfile
└── README.md
```

## Architecture

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
- **Vector DB**: ChromaDB (for RAG)
- **NLP**: LangChain + custom intent detection
- **Containerization**: Docker & Docker Compose

## Quick Start

**Without Docker:**
```bash
pip install poetry
poetry install
poetry run uvicorn src.main:app --reload --port 8000
```

**With Docker:**
```bash
docker build -t inmind .
docker run -p 8000:8000 inmind
```

Access the application at http://localhost:8000

## Development

**Install dependencies:**
```bash
poetry install
```

**Run tests:**
```bash
poetry run pytest
poetry run pytest --cov=src/domain --cov-report=term-missing
```

**Code quality:**
```bash
poetry run black src/ tests/
poetry run mypy src/
poetry run ruff check src/
```

## How It Works

1. **User Input**: User sends a chat message (e.g., "I need wireless headphones under $200")
2. **Intent Detection**: LLM analyzes message to extract intent (SEARCH_PRODUCT) and entities (product_name: "headphones", price_range: "$200", feature: "wireless")
3. **RAG Search**: System searches vector database for relevant products using embeddings
4. **LLM Recommendation**: LLM generates personalized product recommendations based on context
5. **Response**: System returns top product matches with explanations

## Project Status

- ✅ **Phase 1**: Project structure, FastAPI skeleton, Docker setup
- ✅ **Phase 2**: Domain models, value objects, repository protocols, comprehensive tests
- 🚧 **Phase 3**: NLP module (Intent & Entity detection with Ollama) - *In Progress*
- 📋 **Phase 4**: Vector database & embeddings (ChromaDB)
- 📋 **Phase 5**: RAG system implementation
- 📋 **Phase 6**: Conversation engine with memory
- 📋 **Phase 7**: REST API endpoints
- 📋 **Phase 8**: Testing & deployment

## Domain Models

### Core Entities
- **Product**: Represents products to be recommended (with features, price, category, etc.)
- **User**: Tracks user sessions, preferences learned from conversations
- **Conversation**: Manages multi-turn chat dialogues
- **Message**: Individual chat messages (user/assistant/system)
- **DetectedIntent**: Intent classification result from NLP analysis
- **Entity**: Extracted entities from user messages (product names, brands, features, etc.)

### Value Objects
- **Identifiers**: Type-safe UUIDs for all entities
- **IntentType**: Enum for user intents (SEARCH_PRODUCT, GET_RECOMMENDATION, etc.)
- **EntityType**: Enum for extracted entities (PRODUCT_NAME, CATEGORY, PRICE_RANGE, etc.)
- **MessageRole**: USER, ASSISTANT, SYSTEM

## API Endpoints (Current)

- `GET /` - Returns "InMind"
- `GET /health` - Health check endpoint

## Contributing

Follow SOLID principles and write self-documenting code (no comments/docstrings).

## License

MIT