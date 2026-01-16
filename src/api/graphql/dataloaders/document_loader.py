from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.dataloader import DataLoader

from src.api.graphql.types.document import DocumentType
from src.infrastructure.persistence.models.document_model import DocumentModel


class DocumentLoader(DataLoader[str, DocumentType | None]):
    def __init__(self, session: AsyncSession):
        super().__init__(load_fn=self._load_documents)
        self._session = session

    async def _load_documents(
        self,
        keys: list[str],
    ) -> list[DocumentType | None]:
        query = select(DocumentModel).where(DocumentModel.id.in_(keys))
        result = await self._session.execute(query)
        documents = {doc.id: doc for doc in result.scalars().all()}

        return [
            DocumentType(
                id=documents[key].id,
                title=documents[key].title,
                content=documents[key].content,
                owner_id=documents[key].owner_id,
                created_at=documents[key].created_at,
                updated_at=documents[key].updated_at,
            )
            if key in documents
            else None
            for key in keys
        ]
