"""
向量儲存庫實作（使用 PostgreSQL + pgvector）

ABP 對比：
- ABP: public class VectorRepository : IVectorRepository, ITransientDependency
- ABP 使用 EF Core 進行 ORM 操作，配合 pgvector 擴展
- Python: 使用 SQLAlchemy + pgvector.sqlalchemy
"""
import re
from uuid import uuid4

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.domain.interfaces.vector_repository import IVectorRepository
from src.domain.models.search_result import DocumentChunk, SearchResult, SimilarDocument
from src.infrastructure.embeddings.base import IEmbeddingService
from src.infrastructure.persistence.models.document_chunk_model import DocumentChunkModel
from src.infrastructure.persistence.models.document_model import DocumentModel


class VectorRepository(IVectorRepository):
    """
    向量儲存庫實作

    ABP 對比：
    - ABP: public class VectorRepository : IVectorRepository
    - ABP 可能會注入 IRepository<DocumentChunk, Guid> 和 IEmbeddingService
    - Python: 直接注入 AsyncSession 和 IEmbeddingService

    職責：
    - 文本分塊（Chunking）
    - 向量嵌入生成
    - 向量相似度搜尋
    """

    def __init__(
        self,
        session: AsyncSession,
        embedding_service: IEmbeddingService,
    ):
        """
        初始化向量儲存庫

        ABP 對比（使用建構式注入）：
        public VectorRepository(
            IDbContextProvider<MyDbContext> dbContextProvider,
            IEmbeddingService embeddingService)
        """
        self._session = session
        self._embedding = embedding_service

    async def index_document(
        self,
        document_id: str,
        title: str,
        content: str,
        owner_id: str,
    ) -> list[str]:
        """
        將文件索引到向量儲存

        ABP 對比：
        public async Task<List<string>> IndexDocumentAsync(...)
        {
            // 1. 刪除舊的 chunks
            await _chunkRepo.DeleteManyAsync(x => x.DocumentId == documentId);

            // 2. 分塊並生成嵌入
            var chunks = ChunkText(content);
            var embeddings = await _embeddingService.GenerateEmbeddingsAsync(chunks);

            // 3. 儲存新的 chunks
            var entities = chunks.Zip(embeddings, (c, e) => new DocumentChunk { ... });
            await _chunkRepo.InsertManyAsync(entities);
        }
        """
        # 1. 刪除現有的 chunks（如果有的話）
        await self._session.execute(
            delete(DocumentChunkModel).where(
                DocumentChunkModel.document_id == document_id
            )
        )

        # 2. 分塊文本
        chunks = self._chunk_text(f"{title}\n\n{content}")
        if not chunks:
            return []

        # 3. 生成嵌入向量
        embeddings = self._embedding.embed(chunks)

        # 4. 建立 chunk 實體並儲存
        chunk_ids = []
        for index, (chunk_text, embedding) in enumerate(zip(chunks, embeddings)):
            chunk_id = str(uuid4())
            chunk_model = DocumentChunkModel(
                id=chunk_id,
                document_id=document_id,
                content=chunk_text,
                chunk_index=index,
                embedding=embedding,
            )
            self._session.add(chunk_model)
            chunk_ids.append(chunk_id)

        await self._session.flush()
        return chunk_ids

    async def delete_document(self, document_id: str) -> bool:
        """
        從向量儲存刪除文件的所有 chunks

        ABP 對比：
        public async Task<bool> DeleteDocumentAsync(Guid documentId)
        {
            var count = await _chunkRepo.DeleteManyAsync(x => x.DocumentId == documentId);
            return count > 0;
        }
        """
        result = await self._session.execute(
            delete(DocumentChunkModel).where(
                DocumentChunkModel.document_id == document_id
            )
        )
        return result.rowcount > 0

    async def search(
        self,
        query_embedding: list[float],
        owner_id: str,
        limit: int = 10,
        threshold: float = 0.0,
    ) -> list[SearchResult]:
        """
        語意搜尋（使用預先計算的嵌入向量）

        ABP 對比：
        public async Task<List<SearchResultDto>> SearchAsync(...)
        {
            // 使用 EF Core 的 Raw SQL 或自訂 pgvector 擴展
            var results = await _context.DocumentChunks
                .OrderBy(c => c.Embedding.CosineDistance(queryVector))
                .Take(limit)
                .ToListAsync();
        }

        pgvector 相似度計算：
        - cosine_distance: 1 - cosine_similarity（越小越相似）
        - 我們轉換為 score: 1 - distance（越大越相似）
        """
        # 使用 pgvector 的 cosine_distance 進行向量搜尋
        stmt = (
            select(
                DocumentChunkModel,
                DocumentModel.title,
                DocumentChunkModel.embedding.cosine_distance(query_embedding).label(
                    "distance"
                ),
            )
            .join(DocumentModel)
            .where(DocumentModel.owner_id == owner_id)
            .order_by("distance")
            .limit(limit * 2)  # 取多一些，因為要去重複
        )

        result = await self._session.execute(stmt)
        rows = result.all()

        # 轉換為 SearchResult 並去重複（同一文件可能有多個 chunk）
        seen_docs: set[str] = set()
        results: list[SearchResult] = []

        for chunk, title, distance in rows:
            if chunk.document_id in seen_docs:
                continue

            score = 1.0 - float(distance)  # 轉換為相似度分數
            if score < threshold:
                continue

            seen_docs.add(chunk.document_id)
            results.append(
                SearchResult(
                    document_id=chunk.document_id,
                    title=title,
                    content_preview=self._truncate(chunk.content, 200),
                    score=score,
                )
            )

            if len(results) >= limit:
                break

        return results

    async def find_similar(
        self,
        document_id: str,
        owner_id: str,
        limit: int = 5,
    ) -> list[SimilarDocument]:
        """
        找出相似文件

        ABP 對比：
        public async Task<List<SimilarDocumentDto>> FindSimilarAsync(...)
        {
            // 1. 取得文件的第一個 chunk 嵌入
            var sourceChunk = await _chunkRepo.FirstOrDefaultAsync(
                x => x.DocumentId == documentId);

            // 2. 搜尋相似的 chunks（排除自己）
            var similar = await _context.DocumentChunks
                .Where(c => c.DocumentId != documentId)
                .OrderBy(c => c.Embedding.CosineDistance(sourceChunk.Embedding))
                .Take(limit)
                .ToListAsync();
        }
        """
        # 1. 取得來源文件的第一個 chunk
        source_stmt = (
            select(DocumentChunkModel)
            .where(DocumentChunkModel.document_id == document_id)
            .order_by(DocumentChunkModel.chunk_index)
            .limit(1)
        )
        source_result = await self._session.execute(source_stmt)
        source_chunk = source_result.scalar_one_or_none()

        if not source_chunk:
            return []

        # 2. 搜尋相似的文件（排除自己）
        stmt = (
            select(
                DocumentChunkModel,
                DocumentModel.title,
                DocumentChunkModel.embedding.cosine_distance(
                    source_chunk.embedding
                ).label("distance"),
            )
            .join(DocumentModel)
            .where(
                DocumentModel.owner_id == owner_id,
                DocumentChunkModel.document_id != document_id,
            )
            .order_by("distance")
            .limit(limit * 2)
        )

        result = await self._session.execute(stmt)
        rows = result.all()

        # 去重複
        seen_docs: set[str] = set()
        results: list[SimilarDocument] = []

        for chunk, title, distance in rows:
            if chunk.document_id in seen_docs:
                continue

            seen_docs.add(chunk.document_id)
            results.append(
                SimilarDocument(
                    document_id=chunk.document_id,
                    title=title,
                    similarity_score=1.0 - float(distance),
                )
            )

            if len(results) >= limit:
                break

        return results

    async def get_document_chunks(
        self,
        document_id: str,
    ) -> list[DocumentChunk]:
        """
        取得文件的所有 chunks

        ABP 對比：
        public async Task<List<DocumentChunkDto>> GetDocumentChunksAsync(Guid documentId)
        {
            return await _chunkRepo.GetListAsync(x => x.DocumentId == documentId);
        }
        """
        stmt = (
            select(DocumentChunkModel)
            .where(DocumentChunkModel.document_id == document_id)
            .order_by(DocumentChunkModel.chunk_index)
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()

        return [
            DocumentChunk(
                chunk_id=m.id,
                document_id=m.document_id,
                content=m.content,
                chunk_index=m.chunk_index,
                embedding=m.embedding,
            )
            for m in models
        ]

    def _chunk_text(self, text: str) -> list[str]:
        """
        將文本分塊

        ABP 對比：
        private List<string> ChunkText(string text)
        {
            // ABP 可能會抽取到獨立的 ITextChunker 服務
            // 使用 Semantic Kernel 或自訂實作
        }

        策略：
        - 按句子邊界分割
        - 每塊約 chunk_size 字元
        - chunk_overlap 字元重疊（提高語意連貫性）
        """
        if not text or not text.strip():
            return []

        # 按句子分割（中英文句號、問號、驚嘆號）
        sentences = re.split(r"(?<=[。！？.!?])\s*", text)
        sentences = [s.strip() for s in sentences if s.strip()]

        if not sentences:
            return []

        chunks: list[str] = []
        current_chunk: list[str] = []
        current_length = 0

        for sentence in sentences:
            sentence_length = len(sentence)

            if current_length + sentence_length > settings.chunk_size:
                if current_chunk:
                    chunks.append(" ".join(current_chunk))

                    # 重疊：保留最後幾個句子
                    overlap_text = " ".join(current_chunk)
                    if len(overlap_text) > settings.chunk_overlap:
                        # 從後面取重疊部分
                        current_chunk = []
                        overlap_length = 0
                        for s in reversed(current_chunk):
                            if overlap_length + len(s) > settings.chunk_overlap:
                                break
                            current_chunk.insert(0, s)
                            overlap_length += len(s)
                        current_length = overlap_length
                    else:
                        current_chunk = []
                        current_length = 0

            current_chunk.append(sentence)
            current_length += sentence_length

        # 最後一塊
        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks

    def _truncate(self, text: str, max_length: int) -> str:
        """截斷文本並加省略號"""
        if len(text) <= max_length:
            return text
        return text[: max_length - 3] + "..."
