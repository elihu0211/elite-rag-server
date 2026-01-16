"""
資料種子模組

ABP 對比：
- ABP: IDataSeedContributor 介面 + DataSeederContributor 基類
- ABP 在應用程式啟動時自動執行所有註冊的 DataSeedContributor
- Python: 使用 ABC 抽象類別達到相同效果
"""

from .base import IDataSeeder
from .admin_user_seeder import AdminUserSeeder
from .data_seeder import DataSeederManager

__all__ = ["IDataSeeder", "AdminUserSeeder", "DataSeederManager"]
