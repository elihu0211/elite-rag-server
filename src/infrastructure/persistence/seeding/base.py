"""
資料種子基類

ABP 對比：
- ABP: IDataSeedContributor 介面
  public interface IDataSeedContributor
  {
      Task SeedAsync(DataSeedContext context);
  }
- Python: 使用 ABC 抽象類別
"""

from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession


class IDataSeeder(ABC):
    """
    資料種子介面

    ABP 對比：IDataSeedContributor
    所有種子類別都應實作此介面
    """

    @property
    @abstractmethod
    def order(self) -> int:
        """
        種子執行順序，數字越小越先執行

        ABP 對比：ABP 沒有內建排序，通常透過依賴注入順序或手動控制
        """
        pass

    @abstractmethod
    async def seed_async(self, session: AsyncSession) -> None:
        """
        執行種子資料植入

        Args:
            session: 資料庫會話
        """
        pass
