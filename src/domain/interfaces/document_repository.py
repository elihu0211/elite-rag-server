from abc import ABC, abstractmethod

from src.domain.models.document import Document


class IDocumentRepository(ABC):
    @abstractmethod
    async def get_by_id(self, id: str) -> Document | None: ...

    @abstractmethod
    async def get_by_ids(self, ids: list[str]) -> list[Document]: ...

    @abstractmethod
    async def get_by_owner_id(
        self,
        owner_id: str,
        limit: int = 10,
        offset: int = 0,
    ) -> list[Document]: ...

    @abstractmethod
    async def save(self, document: Document) -> Document: ...

    @abstractmethod
    async def delete(self, id: str) -> bool: ...
