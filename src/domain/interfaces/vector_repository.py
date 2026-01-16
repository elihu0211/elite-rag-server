"""
向量儲存庫介面

ABP 對比：
- ABP 定義介面於 Domain 層，例如 IVectorRepository : IRepository
- 但 ABP 通常使用 Generic Repository：IRepository<T, TKey>
- 向量儲存較特殊，ABP 可能會建立 IVectorStoreService 於 Application 層
- Python 使用 ABC (Abstract Base Class) 定義介面，概念相同

設計說明：
- 此介面定義向量儲存的核心操作
- 實作層 (Infrastructure) 負責與 PostgreSQL/pgvector 交互
"""

from abc import ABC, abstractmethod

from src.domain.models.search_result import DocumentChunk, SearchResult, SimilarDocument


class IVectorRepository(ABC):
    """
    向量儲存庫介面

    ABP 對比：
    - ABP: public interface IVectorRepository : ITransientDependency
    - Python ABC 類似 C# interface，但 Python 無內建 DI 生命週期標記
    - ABP 使用 ITransientDependency/ISingletonDependency 標記生命週期
    - Python/FastAPI 在 DI 容器配置時決定生命週期
    """

    @abstractmethod
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
        - ABP: Task<List<string>> IndexDocumentAsync(...)
        - Python async def 對應 C# async Task
        - 回傳建立的 chunk IDs
        """
        ...

    @abstractmethod
    async def delete_document(self, document_id: str) -> bool:
        """
        從向量儲存刪除文件的所有 chunks

        ABP 對比：
        - ABP: Task<bool> DeleteDocumentAsync(Guid documentId)
        """
        ...

    @abstractmethod
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
        - ABP: Task<List<SearchResultDto>> SearchAsync(SearchInput input)
        - ABP 傾向用 Input Dto 封裝參數
        - Python 直接使用具名參數，更直觀
        """
        ...

    @abstractmethod
    async def find_similar(
        self,
        document_id: str,
        owner_id: str,
        limit: int = 5,
    ) -> list[SimilarDocument]:
        """
        找出相似文件

        ABP 對比：
        - ABP: Task<List<SimilarDocumentDto>> FindSimilarAsync(...)
        """
        ...

    @abstractmethod
    async def get_document_chunks(
        self,
        document_id: str,
    ) -> list[DocumentChunk]:
        """
        取得文件的所有 chunks（用於偵錯或顯示）
        """
        ...
