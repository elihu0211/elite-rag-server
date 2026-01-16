from abc import ABC, abstractmethod

from src.domain.models.user import User


class IUserRepository(ABC):
    @abstractmethod
    async def get_by_id(self, id: str) -> User | None: ...

    @abstractmethod
    async def get_by_ids(self, ids: list[str]) -> list[User]: ...

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None: ...

    @abstractmethod
    async def save(self, user: User, hashed_password: str) -> User: ...

    @abstractmethod
    async def delete(self, id: str) -> bool: ...
