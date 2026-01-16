from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.dataloader import DataLoader

from src.api.graphql.types.user import UserType
from src.infrastructure.persistence.models.user_model import UserModel


class UserLoader(DataLoader[str, UserType | None]):
    def __init__(self, session: AsyncSession):
        super().__init__(load_fn=self._load_users)
        self._session = session

    async def _load_users(
        self,
        keys: list[str],
    ) -> list[UserType | None]:
        query = select(UserModel).where(UserModel.id.in_(keys))
        result = await self._session.execute(query)
        users = {user.id: user for user in result.scalars().all()}

        return [
            UserType(
                id=users[key].id,
                email=users[key].email,
                name=users[key].name,
                is_active=users[key].is_active,
                created_at=users[key].created_at,
                updated_at=users[key].updated_at,
            )
            if key in users
            else None
            for key in keys
        ]
