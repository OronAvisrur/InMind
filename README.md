# InMind

AI-powered product recommendation system with conversational interface.

## Project Structure

```
inmind-project/
├── src/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── domain/              # Core business logic and entities
│   ├── application/         # Use cases and business rules
│   ├── infrastructure/      # External integrations (future: Ollama, ChromaDB)
│   └── api/                 # API routes and endpoints
├── tests/
├── pyproject.toml
├── Dockerfile
└── README.md
```

## Tech Stack

- Python 3.11+
- FastAPI
- Pydantic V2

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

```bash
poetry install
poetry run pytest
```

## Project Status

Phase 1: ✅ Basic project structure complete