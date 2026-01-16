from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.exceptions import AuthenticationError, ValidationError
from src.domain.models.user import User
from src.infrastructure.auth.jwt_handler import JWTHandler
from src.infrastructure.auth.password_hasher import PasswordHasher
from src.infrastructure.persistence.repositories.user_repository import UserRepository


class AuthService:
    def __init__(self, session: AsyncSession):
        self._session = session
        self._user_repo = UserRepository(session)

    async def register(self, email: str, password: str, name: str) -> User:
        existing = await self._user_repo.get_by_email(email)
        if existing:
            raise ValidationError("Email already registered")

        hashed_password = PasswordHasher.hash(password)
        user = User(
            id=str(uuid4()),
            email=email,
            name=name,
        )
        return await self._user_repo.save(user, hashed_password)

    async def login(self, email: str, password: str) -> str:
        user = await self._user_repo.get_by_email(email)
        if not user:
            raise AuthenticationError("Invalid email or password")

        hashed_password = await self._user_repo.get_hashed_password(email)
        if not hashed_password or not PasswordHasher.verify(password, hashed_password):
            raise AuthenticationError("Invalid email or password")

        if not user.is_active:
            raise AuthenticationError("User account is disabled")

        return JWTHandler.create_token({"sub": user.id, "email": user.email})

    def verify_token(self, token: str) -> User | None:
        payload = JWTHandler.decode_token(token)
        if not payload:
            return None

        return User(
            id=payload["sub"],
            email=payload["email"],
            name="",
        )

    async def get_user_by_id(self, user_id: str) -> User | None:
        return await self._user_repo.get_by_id(user_id)
