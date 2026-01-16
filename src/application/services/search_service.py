"""
搜尋應用服務

ABP 對比：
- ABP: public class SearchAppService : ApplicationService, ISearchAppService
- ABP 使用 ILocalEventBus 發布事件，解耦文件索引
- ABP 使用 IMapper 做 DTO 轉換
- Python: 直接組合 EmbeddingService 和 VectorRepository
"""

from src.domain.interfaces.vector_repository import IVectorRepository
from src.domain.models.search_result import SearchResult, SimilarDocument
from src.infrastructure.embeddings.base import IEmbeddingService
from src.config import settings


class SearchService:
    """
    搜尋應用服務

    ABP 對比：
    - ABP: public class SearchAppService : ApplicationService
    - ABP 會繼承 ApplicationService 取得 CurrentUser、Logger 等功能
    - ABP 使用 [Authorize] attribute 做權限控制
    - Python: 在 GraphQL Resolver 層處理權限

    職責：
    - 協調嵌入服務和向量儲存庫
    - 處理搜尋業務邏輯
    """

    def __init__(
        self,
        embedding_service: IEmbeddingService,
        vector_repository: IVectorRepository,
    ):
        """
        初始化搜尋服務

        ABP 對比（使用建構式注入）：
        public SearchAppService(
            IEmbeddingService embeddingService,
            IVectorRepository vectorRepository,
            ICurrentUser currentUser)
        {
            _embeddingService = embeddingService;
            _vectorRepository = vectorRepository;
            _currentUser = currentUser;
        }
        """
        self._embedding = embedding_service
        self._vector_repo = vector_repository

    async def search_documents(
        self,
        query: str,
        user_id: str,
        limit: int | None = None,
        threshold: float | None = None,
    ) -> list[SearchResult]:
        """
        語意搜尋文件

        ABP 對比：
        [Authorize]
        public async Task<List<SearchResultDto>> SearchDocumentsAsync(
            SearchDocumentsInput input)
        {
            // ABP 自動從 CurrentUser 取得用戶 ID
            var userId = CurrentUser.GetId();

            // 1. 生成查詢向量
            var queryEmbedding = await _embeddingService
                .GenerateEmbeddingAsync(input.Query);

            // 2. 執行向量搜尋
            var results = await _vectorRepository.SearchAsync(
                queryEmbedding, userId, input.Limit, input.Threshold);

            // 3. 使用 IMapper 轉換為 DTO
            return ObjectMapper.Map<List<SearchResultDto>>(results);
        }

        流程：
        1. 將查詢文本轉為嵌入向量
        2. 在向量資料庫中搜尋相似文件
        3. 返回排序後的搜尋結果
        """
        # 使用預設值
        limit = limit or settings.default_search_limit
        threshold = threshold or settings.similarity_threshold

        # 1. 生成查詢向量
        query_embedding = self._embedding.embed_single(query)

        # 2. 執行向量搜尋
        results = await self._vector_repo.search(
            query_embedding=query_embedding,
            owner_id=user_id,
            limit=limit,
            threshold=threshold,
        )

        return results

    async def find_similar_documents(
        self,
        document_id: str,
        user_id: str,
        limit: int = 5,
    ) -> list[SimilarDocument]:
        """
        找出相似文件

        ABP 對比：
        [Authorize]
        public async Task<List<SimilarDocumentDto>> FindSimilarDocumentsAsync(
            FindSimilarInput input)
        {
            // 驗證文件存在且屬於當前用戶
            var document = await _documentRepo.GetAsync(input.DocumentId);
            if (document.OwnerId != CurrentUser.GetId())
                throw new AbpAuthorizationException();

            return await _vectorRepository.FindSimilarAsync(
                input.DocumentId, CurrentUser.GetId(), input.Limit);
        }
        """
        return await self._vector_repo.find_similar(
            document_id=document_id,
            owner_id=user_id,
            limit=limit,
        )

    async def index_document(
        self,
        document_id: str,
        title: str,
        content: str,
        owner_id: str,
    ) -> list[str]:
        """
        索引文件到向量儲存

        ABP 對比：
        - ABP 通常使用 Domain Event 來解耦：
          當文件建立時發布 DocumentCreatedEvent
          DocumentCreatedEventHandler 負責索引

        public class DocumentCreatedEventHandler :
            ILocalEventHandler<DocumentCreatedEvent>
        {
            public async Task HandleEventAsync(DocumentCreatedEvent eventData)
            {
                await _vectorRepository.IndexDocumentAsync(
                    eventData.DocumentId,
                    eventData.Title,
                    eventData.Content,
                    eventData.OwnerId);
            }
        }

        Python 版本：直接在服務中呼叫，簡化架構
        """
        return await self._vector_repo.index_document(
            document_id=document_id,
            title=title,
            content=content,
            owner_id=owner_id,
        )

    async def delete_document_index(self, document_id: str) -> bool:
        """
        從向量儲存刪除文件索引

        ABP 對比：
        - 同樣可用 Domain Event 解耦
        - DocumentDeletedEventHandler 處理清理邏輯
        """
        return await self._vector_repo.delete_document(document_id)
