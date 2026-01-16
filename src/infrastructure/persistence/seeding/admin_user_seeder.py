"""
管理員用戶種子資料

ABP 對比：
- ABP: IdentityDataSeedContributor 用於建立預設管理員
- ABP 通常在 DbMigrator 或應用程式啟動時執行
"""

import logging
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.infrastructure.auth.password_hasher import PasswordHasher
from src.infrastructure.persistence.models.user_model import UserModel

from .base import IDataSeeder

logger = logging.getLogger(__name__)


class AdminUserSeeder(IDataSeeder):
    """
    管理員用戶種子資料

    ABP 對比：
    - ABP: IdentityDataSeedContributor
    - 建立預設管理員帳號，確保系統可以登入
    """

    @property
    def order(self) -> int:
        return 1  # 最先執行

    async def seed_async(self, session: AsyncSession) -> None:
        """建立預設管理員帳號"""
        admin_email = settings.seed_admin_email
        admin_password = settings.seed_admin_password
        admin_name = settings.seed_admin_name

        # 檢查管理員是否已存在
        query = select(UserModel).where(UserModel.email == admin_email)
        result = await session.execute(query)
        existing = result.scalar_one_or_none()

        if existing:
            logger.info(f"Admin user '{admin_email}' already exists, skipping seed")
            return

        # 建立管理員帳號
        hashed_password = PasswordHasher.hash(admin_password)
        admin_user = UserModel(
            id=str(uuid4()),
            email=admin_email,
            name=admin_name,
            hashed_password=hashed_password,
            is_active=True,
        )
        session.add(admin_user)
        await session.flush()

        logger.info(f"Admin user '{admin_email}' created successfully")
