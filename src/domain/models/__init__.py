from .product import Product
from .user import User, UserPreferences
from .conversation import Conversation, Message
from .intent import DetectedIntent, IntentDetectionResult

__all__ = [
    "Product",
    "User",
    "UserPreferences",
    "Conversation",
    "Message",
    "DetectedIntent",
    "IntentDetectionResult",
]