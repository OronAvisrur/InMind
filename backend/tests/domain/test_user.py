import pytest
from src.domain.models import User, UserPreferences
from src.domain.value_objects import UserIdentifier


class TestUser:
    def test_create_user(self):
        user = User(session_id="test-session-123")
        assert user.session_id == "test-session-123"
        assert isinstance(user.id, UserIdentifier)

    def test_user_update_activity(self):
        user = User(session_id="test-session")
        original_time = user.last_active
        user.update_activity()
        assert user.last_active >= original_time

    def test_user_add_interaction(self):
        user = User(session_id="test-session")
        user.add_interaction("Searched for laptops")
        assert len(user.interaction_history) == 1
        assert user.interaction_history[0] == "Searched for laptops"

    def test_user_multiple_interactions(self):
        user = User(session_id="test-session")
        user.add_interaction("Asked about headphones")
        user.add_interaction("Mentioned budget of $200")
        user.add_interaction("Prefers wireless")
        
        assert len(user.interaction_history) == 3
        assert "budget of $200" in user.interaction_history[1]

    def test_user_preferences_defaults(self):
        user = User(session_id="test-session")
        assert user.preferences.price_sensitivity == "medium"
        assert user.preferences.favorite_categories == []
        assert user.preferences.preferred_brands == []

    def test_user_with_custom_preferences(self):
        preferences = UserPreferences(
            favorite_categories=["Electronics", "Gaming"],
            price_sensitivity="low",
            preferred_brands=["Sony", "Samsung"],
        )
        user = User(session_id="test-session", preferences=preferences)
        
        assert user.preferences.favorite_categories == ["Electronics", "Gaming"]
        assert user.preferences.price_sensitivity == "low"
        assert len(user.preferences.preferred_brands) == 2