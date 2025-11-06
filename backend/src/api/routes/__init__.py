from src.api.routes.health import router as health_router
from src.api.routes.chat import router as chat_router
from src.api.routes.product import router as product_router
from src.api.routes.intent import router as intent_router


__all__ = [
    "health_router",
    "chat_router",
    "product_router",
    "intent_router",
]