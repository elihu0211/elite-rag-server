"""
Domain Models

ABP 對比：
- ABP: 實體類別通常放在 Domain 層的 Entities 目錄
- ABP 使用 Entity<TKey> 或 AggregateRoot<TKey> 基底類別
- Python: 使用 dataclass 定義純資料模型
"""

from src.domain.models.document import Document
from src.domain.models.search_result import DocumentChunk, SearchResult, SimilarDocument
from src.domain.models.user import User

__all__ = [
    "Document",
    "User",
    "SearchResult",
    "SimilarDocument",
    "DocumentChunk",
]
