from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.interfaces.document_repository import IDocumentRepository
from src.domain.models.document import Document
from src.infrastructure.persistence.models.document_model import DocumentModel


class DocumentRepository(IDocumentRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, id: str) -> Document | None:
        query = select(DocumentModel).where(DocumentModel.id == id)
        result = await self._session.execute(query)
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def get_by_ids(self, ids: list[str]) -> list[Document]:
        query = select(DocumentModel).where(DocumentModel.id.in_(ids))
        result = await self._session.execute(query)
        models = result.scalars().all()
        return [self._to_domain(m) for m in models]

    async def get_by_owner_id(
        self,
        owner_id: str,
        limit: int = 10,
        offset: int = 0,
    ) -> list[Document]:
        query = (
            select(DocumentModel)
            .where(DocumentModel.owner_id == owner_id)
            .limit(limit)
            .offset(offset)
            .order_by(DocumentModel.created_at.desc())
        )
        result = await self._session.execute(query)
        models = result.scalars().all()
        return [self._to_domain(m) for m in models]

    async def save(self, document: Document) -> Document:
        existing = await self._session.get(DocumentModel, document.id)
        if existing:
            existing.title = document.title
            existing.content = document.content
            await self._session.flush()
            return self._to_domain(existing)

        model = DocumentModel(
            id=document.id or str(uuid4()),
            title=document.title,
            content=document.content,
            owner_id=document.owner_id,
        )
        self._session.add(model)
        await self._session.flush()
        return self._to_domain(model)

    async def delete(self, id: str) -> bool:
        model = await self._session.get(DocumentModel, id)
        if model:
            await self._session.delete(model)
            return True
        return False

    def _to_domain(self, model: DocumentModel) -> Document:
        return Document(
            id=model.id,
            title=model.title,
            content=model.content,
            owner_id=model.owner_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
