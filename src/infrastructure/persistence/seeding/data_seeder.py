"""
資料種子管理器

ABP 對比：
- ABP: IDataSeeder 介面 + DataSeeder 實作
  public interface IDataSeeder
  {
      Task SeedAsync(DataSeedContext context);
  }
- DataSeeder 會收集所有 IDataSeedContributor 並依序執行
"""

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from .base import IDataSeeder
from .admin_user_seeder import AdminUserSeeder

logger = logging.getLogger(__name__)


class DataSeederManager:
    """
    資料種子管理器

    ABP 對比：
    - ABP: DataSeeder 類別
    - 負責收集並執行所有 IDataSeedContributor
    - 在應用程式啟動時調用
    """

    def __init__(self):
        # 註冊所有種子貢獻者
        # ABP 對比：ABP 透過 DI 容器自動收集所有 IDataSeedContributor
        self._seeders: list[IDataSeeder] = [
            AdminUserSeeder(),
            # 未來可以在這裡添加更多種子：
            # RolesSeeder(),
            # PermissionsSeeder(),
            # SampleDocumentsSeeder(),
        ]

    async def seed_async(self, session: AsyncSession) -> None:
        """
        執行所有種子資料

        ABP 對比：DataSeeder.SeedAsync()
        """
        logger.info("Starting data seeding...")

        # 依照 order 排序後執行
        sorted_seeders = sorted(self._seeders, key=lambda s: s.order)

        for seeder in sorted_seeders:
            seeder_name = seeder.__class__.__name__
            logger.info(f"Running seeder: {seeder_name}")
            try:
                await seeder.seed_async(session)
            except Exception as e:
                logger.error(f"Seeder {seeder_name} failed: {e}")
                raise

        logger.info("Data seeding completed")
