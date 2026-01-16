"""
文件應用服務

ABP 對比：
- ABP: public class DocumentAppService : ApplicationService, IDocumentAppService
- ABP 使用 IRepository<Document, Guid> 自動注入
- ABP 使用 ILocalEventBus 發布 DocumentCreatedEvent 等事件
- Python: 直接呼叫 SearchService 進行向量索引
"""

from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.exceptions import AuthorizationError, NotFoundError
from src.domain.models.document import Document
from src.domain.interfaces.vector_repository import IVectorRepository
from src.infrastructure.persistence.repositories.document_repository import (
    DocumentRepository,
)


class DocumentService:
    """
    文件應用服務

    ABP 對比：
    - ABP: public class DocumentAppService : ApplicationService
    - ABP 會自動注入 IRepository、ILocalEventBus、ICurrentUser
    - Python: 手動注入依賴，在 Context 中組裝
    """

    def __init__(
        self,
        session: AsyncSession,
        vector_repository: IVectorRepository | None = None,
    ):
        """
        初始化文件服務

        ABP 對比（使用建構式注入）：
        public DocumentAppService(
            IRepository<Document, Guid> documentRepository,
            ILocalEventBus localEventBus,
            ICurrentUser currentUser)
        {
            _documentRepository = documentRepository;
            _localEventBus = localEventBus;
            _currentUser = currentUser;
        }

        注意：vector_repository 是可選的，便於向後相容
        """
        self._session = session
        self._doc_repo = DocumentRepository(session)
        self._vector_repo = vector_repository

    async def get_document(self, id: str, user_id: str) -> Document:
        document = await self._doc_repo.get_by_id(id)
        if not document:
            raise NotFoundError("Document not found")

        if document.owner_id != user_id:
            raise AuthorizationError("Not authorized to access this document")

        return document

    async def list_documents(
        self,
        user_id: str,
        limit: int = 10,
        offset: int = 0,
    ) -> list[Document]:
        return await self._doc_repo.get_by_owner_id(user_id, limit, offset)

    async def create_document(
        self,
        title: str,
        content: str,
        user_id: str,
    ) -> Document:
        """
        建立文件並索引向量

        ABP 對比：
        public async Task<DocumentDto> CreateAsync(CreateDocumentInput input)
        {
            var document = new Document(...);
            await _documentRepository.InsertAsync(document);

            // ABP 使用事件解耦向量索引
            await _localEventBus.PublishAsync(
                new DocumentCreatedEvent(document));

            return ObjectMapper.Map<DocumentDto>(document);
        }

        Python 版本：直接呼叫向量儲存庫，簡化架構
        """
        document = Document(
            id=str(uuid4()),
            title=title,
            content=content,
            owner_id=user_id,
        )
        saved_doc = await self._doc_repo.save(document)

        # 索引向量（如果啟用）
        if self._vector_repo:
            await self._vector_repo.index_document(
                document_id=saved_doc.id,
                title=saved_doc.title,
                content=saved_doc.content,
                owner_id=user_id,
            )

        return saved_doc

    async def update_document(
        self,
        id: str,
        title: str | None,
        content: str | None,
        user_id: str,
    ) -> Document:
        """
        更新文件並重新索引向量

        ABP 對比：
        public async Task<DocumentDto> UpdateAsync(Guid id, UpdateDocumentInput input)
        {
            var document = await _documentRepository.GetAsync(id);
            // ... 更新邏輯 ...

            // 發布事件觸發重新索引
            await _localEventBus.PublishAsync(
                new DocumentUpdatedEvent(document));

            return ObjectMapper.Map<DocumentDto>(document);
        }
        """
        document = await self._doc_repo.get_by_id(id)
        if not document:
            raise NotFoundError("Document not found")

        if document.owner_id != user_id:
            raise AuthorizationError("Not authorized to update this document")

        if title is not None:
            document.title = title
        if content is not None:
            document.content = content

        saved_doc = await self._doc_repo.save(document)

        # 重新索引向量（如果內容有變更）
        if self._vector_repo and (title is not None or content is not None):
            await self._vector_repo.index_document(
                document_id=saved_doc.id,
                title=saved_doc.title,
                content=saved_doc.content,
                owner_id=user_id,
            )

        return saved_doc

    async def delete_document(self, id: str, user_id: str) -> bool:
        """
        刪除文件和向量索引

        ABP 對比：
        public async Task DeleteAsync(Guid id)
        {
            var document = await _documentRepository.GetAsync(id);
            await _documentRepository.DeleteAsync(document);

            // 發布事件觸發清理索引
            await _localEventBus.PublishAsync(
                new DocumentDeletedEvent(id));
        }

        注意：由於使用 CASCADE 刪除，資料庫會自動刪除相關 chunks
        但這裡保留明確刪除以確保一致性
        """
        document = await self._doc_repo.get_by_id(id)
        if not document:
            raise NotFoundError("Document not found")

        if document.owner_id != user_id:
            raise AuthorizationError("Not authorized to delete this document")

        # 刪除向量索引（CASCADE 會自動處理，但明確刪除更安全）
        if self._vector_repo:
            await self._vector_repo.delete_document(id)

        return await self._doc_repo.delete(id)
