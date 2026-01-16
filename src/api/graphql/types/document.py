from datetime import datetime

import strawberry

from src.domain.models.document import Document


@strawberry.type
class DocumentType:
    id: strawberry.ID
    title: str
    content: str
    owner_id: str
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @classmethod
    def from_domain(cls, document: Document) -> "DocumentType":
        return cls(
            id=strawberry.ID(document.id),
            title=document.title,
            content=document.content,
            owner_id=document.owner_id,
            created_at=document.created_at,
            updated_at=document.updated_at,
        )
