from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.interfaces.user_repository import IUserRepository
from src.domain.models.user import User
from src.infrastructure.persistence.models.user_model import UserModel


class UserRepository(IUserRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, id: str) -> User | None:
        query = select(UserModel).where(UserModel.id == id)
        result = await self._session.execute(query)
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def get_by_ids(self, ids: list[str]) -> list[User]:
        query = select(UserModel).where(UserModel.id.in_(ids))
        result = await self._session.execute(query)
        models = result.scalars().all()
        return [self._to_domain(m) for m in models]

    async def get_by_email(self, email: str) -> User | None:
        query = select(UserModel).where(UserModel.email == email)
        result = await self._session.execute(query)
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def get_hashed_password(self, email: str) -> str | None:
        query = select(UserModel.hashed_password).where(UserModel.email == email)
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def save(self, user: User, hashed_password: str) -> User:
        existing = await self._session.get(UserModel, user.id)
        if existing:
            existing.email = user.email
            existing.name = user.name
            existing.is_active = user.is_active
            await self._session.flush()
            return self._to_domain(existing)

        model = UserModel(
            id=user.id or str(uuid4()),
            email=user.email,
            name=user.name,
            hashed_password=hashed_password,
            is_active=user.is_active,
        )
        self._session.add(model)
        await self._session.flush()
        return self._to_domain(model)

    async def delete(self, id: str) -> bool:
        model = await self._session.get(UserModel, id)
        if model:
            await self._session.delete(model)
            return True
        return False

    def _to_domain(self, model: UserModel) -> User:
        return User(
            id=model.id,
            email=model.email,
            name=model.name,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
