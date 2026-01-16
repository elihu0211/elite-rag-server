"""
使用者 ORM 模型

ABP 對比：
- ABP: IdentityUser 或自訂的 AppUser : IdentityUser
- ABP 使用 EF Core 的 Fluent API 或 Data Annotations
- Python: 使用 SQLAlchemy 的 Mapped 類型提示
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.persistence.database import Base

if TYPE_CHECKING:
    from src.infrastructure.persistence.models.document_model import DocumentModel


class UserModel(Base):
    """
    使用者資料表模型

    ABP 對比：
    public class AppUser : IdentityUser
    {
        public string Name { get; set; }
        public bool IsActive { get; set; }
        public virtual ICollection<Document> Documents { get; set; }
    }
    """

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # 關聯
    documents: Mapped[list["DocumentModel"]] = relationship(
        "DocumentModel", back_populates="owner"
    )
