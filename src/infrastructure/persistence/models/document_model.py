"""
文件 ORM 模型

ABP 對比：
- ABP: Document : FullAuditedAggregateRoot<Guid>
- ABP 使用 EF Core 配置關聯和索引
- Python: 使用 SQLAlchemy 的 relationship 和 ForeignKey
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.persistence.database import Base

if TYPE_CHECKING:
    from src.infrastructure.persistence.models.document_chunk_model import (
        DocumentChunkModel,
    )
    from src.infrastructure.persistence.models.user_model import UserModel


class DocumentModel(Base):
    """
    文件資料表模型

    ABP 對比：
    public class Document : FullAuditedAggregateRoot<Guid>
    {
        public string Title { get; set; }
        public string Content { get; set; }
        public Guid OwnerId { get; set; }
        public virtual AppUser Owner { get; set; }
        public virtual ICollection<DocumentChunk> Chunks { get; set; }
    }
    """

    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    owner_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # 關聯
    owner: Mapped["UserModel"] = relationship("UserModel", back_populates="documents")
    chunks: Mapped[list["DocumentChunkModel"]] = relationship(
        "DocumentChunkModel", back_populates="document", cascade="all, delete-orphan"
    )
