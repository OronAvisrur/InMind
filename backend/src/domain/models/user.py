from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from ..value_objects import UserIdentifier


class UserPreferences(BaseModel):
    favorite_categories: List[str] = Field(default_factory=list)
    price_sensitivity: str = Field(default="medium")
    preferred_brands: List[str] = Field(default_factory=list)
    disliked_features: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class User(BaseModel):
    id: UserIdentifier = Field(default_factory=UserIdentifier)
    session_id: str = Field(min_length=1)
    preferences: UserPreferences = Field(default_factory=UserPreferences)
    interaction_history: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_active: datetime = Field(default_factory=datetime.utcnow)

    def update_activity(self) -> None:
        self.last_active = datetime.utcnow()

    def add_interaction(self, interaction: str) -> None:
        self.interaction_history.append(interaction)
        self.update_activity()