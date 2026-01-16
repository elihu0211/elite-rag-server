"""
使用者領域模型

ABP 對比：
- ABP: 通常使用 IdentityUser 或自訂的 AppUser : IdentityUser
- ABP Identity 模組提供完整的使用者管理功能
- Python: 使用簡單的 dataclass 定義
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class User:
    """
    使用者領域模型

    ABP 對比：
    public class AppUser : IdentityUser
    {
        public string Name { get; set; }
        public bool IsActive { get; set; }
    }

    注意：密碼雜湊儲存在 Repository 層，不在領域模型中
    """

    id: str | None
    email: str
    name: str
    is_active: bool = True
    created_at: datetime | None = None
    updated_at: datetime | None = None
