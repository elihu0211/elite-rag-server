from datetime import datetime

import strawberry

from src.domain.models.user import User


@strawberry.type
class UserType:
    id: strawberry.ID
    email: str
    name: str
    is_active: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @classmethod
    def from_domain(cls, user: User) -> "UserType":
        return cls(
            id=strawberry.ID(user.id),
            email=user.email,
            name=user.name,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
