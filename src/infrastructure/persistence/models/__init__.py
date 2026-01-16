"""
SQLAlchemy ORM Models

ABP 對比：
- ABP: 使用 EF Core 的 DbContext 和 Entity 配置
- ABP 實體繼承自 Entity<TKey> 或 AggregateRoot<TKey>
- Python: 使用 SQLAlchemy 的 DeclarativeBase 和 Mapped 類型提示
"""

from src.infrastructure.persistence.models.document_chunk_model import (
    DocumentChunkModel,
)
from src.infrastructure.persistence.models.document_model import DocumentModel
from src.infrastructure.persistence.models.user_model import UserModel

__all__ = [
    "UserModel",
    "DocumentModel",
    "DocumentChunkModel",
]
