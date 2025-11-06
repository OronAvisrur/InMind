from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from src.infrastructure.config.settings import Settings
from src.api.dependencies import get_settings
from src.api.routes import health_router, chat_router, product_router, intent_router
from src.api.middleware import (
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler,
)


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="AI-powered product recommendation system using NLP, RAG, and local LLM",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

app.include_router(health_router)
app.include_router(chat_router)
app.include_router(product_router)
app.include_router(intent_router)


@app.get("/")
def read_root():
    return {
        "message": "InMind API",
        "version": "1.0.0",
        "status": "running",
        "documentation": "/docs"
    }
