"""
文件分塊 ORM 模型（含向量嵌入）

ABP 對比：
- ABP: DocumentChunk : Entity<Guid>
- ABP 配合 pgvector 擴展使用自訂類型
- Python: 使用 pgvector.sqlalchemy 的 Vector 類型
"""

from typing import TYPE_CHECKING

from pgvector.sqlalchemy import Vector
from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.config import settings
from src.infrastructure.persistence.database import Base

if TYPE_CHECKING:
    from src.infrastructure.persistence.models.document_model import DocumentModel


class DocumentChunkModel(Base):
    """
    文件分塊資料表模型（含向量嵌入）

    ABP 對比：
    public class DocumentChunk : Entity<Guid>
    {
        public Guid DocumentId { get; set; }
        public string Content { get; set; }
        public int ChunkIndex { get; set; }
        public Vector Embedding { get; set; }  // pgvector 類型
        public virtual Document Document { get; set; }
    }

    pgvector 設定：
    - 使用 cosine 距離進行相似度搜尋
    - 向量維度由 embedding model 決定（預設 384 for all-MiniLM-L6-v2）
    """

    __tablename__ = "document_chunks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    document_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    embedding: Mapped[list[float]] = mapped_column(
        Vector(settings.embedding_dimension), nullable=True
    )

    # 關聯
    document: Mapped["DocumentModel"] = relationship(
        "DocumentModel", back_populates="chunks"
    )
