"""
搜尋結果領域模型

ABP 對比：
- ABP: 這些通常是 DTO (Data Transfer Object)
- ABP 將 DTO 放在 Application.Contracts 專案
- Python: 放在 Domain 層作為值物件 (Value Object)
"""

from dataclasses import dataclass


@dataclass
class SearchResult:
    """
    搜尋結果

    ABP 對比：
    public class SearchResultDto
    {
        public Guid DocumentId { get; set; }
        public string Title { get; set; }
        public string ContentPreview { get; set; }
        public double Score { get; set; }
    }
    """

    document_id: str
    title: str
    content_preview: str
    score: float


@dataclass
class SimilarDocument:
    """
    相似文件

    ABP 對比：
    public class SimilarDocumentDto
    {
        public Guid DocumentId { get; set; }
        public string Title { get; set; }
        public double SimilarityScore { get; set; }
    }
    """

    document_id: str
    title: str
    similarity_score: float


@dataclass
class DocumentChunk:
    """
    文件分塊

    ABP 對比：
    public class DocumentChunkDto
    {
        public Guid ChunkId { get; set; }
        public Guid DocumentId { get; set; }
        public string Content { get; set; }
        public int ChunkIndex { get; set; }
        public float[] Embedding { get; set; }
    }
    """

    chunk_id: str
    document_id: str
    content: str
    chunk_index: int
    embedding: list[float] | None = None
