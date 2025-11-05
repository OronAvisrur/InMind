from typing import Protocol, Optional, List
from ..models import User
from ..value_objects import UserIdentifier


class UserRepository(Protocol):
    async def create(self, user: User) -> User:
        ...

    async def get_by_id(self, user_id: UserIdentifier) -> Optional[User]:
        ...

    async def get_by_session_id(self, session_id: str) -> Optional[User]:
        ...

    async def update(self, user: User) -> User:
        ...

    async def delete(self, user_id: UserIdentifier) -> bool:
        ...

    async def list_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        ...