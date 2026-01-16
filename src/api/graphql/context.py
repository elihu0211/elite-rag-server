"""
GraphQL Context

ABP 對比：
- ABP: 使用 ICurrentUser、IServiceProvider 等內建機制
- ABP 的 DI 容器自動管理服務生命週期
- Python: 手動在 Context 中管理服務實例
"""
from functools import cached_property

from fastapi import Request, WebSocket
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.fastapi import BaseContext

from src.api.graphql.dataloaders.dataloaders import DataLoaders
from src.application.services.auth_service import AuthService
from src.application.services.document_service import DocumentService
from src.application.services.search_service import SearchService
from src.domain.models.user import User
from src.infrastructure.embeddings.base import IEmbeddingService
from src.infrastructure.embeddings.local_embeddings import get_embedding_service
from src.infrastructure.persistence.repositories.vector_repository import (
    VectorRepository,
)


class GraphQLContext(BaseContext):
    """
    GraphQL 請求 Context

    ABP 對比：
    - ABP: 每個請求自動建立 scope，服務由 DI 容器管理
    - ABP 使用 ICurrentUser 取得當前用戶
    - ABP 使用 IServiceProvider 解析服務
    - Python: 在 Context 中手動管理服務實例和生命週期
    """

    def __init__(
        self,
        request: Request | None = None,
        websocket: WebSocket | None = None,
        db_session: AsyncSession | None = None,
        connection_params: dict | None = None,
    ):
        """
        初始化 Context

        ABP 對比：
        - ABP 使用 Middleware 自動設置 Request Scope
        - Python: 每個請求手動建立 Context
        """
        self.request = request
        self.websocket = websocket
        self.db_session = db_session
        self.connection_params = connection_params
        self._current_user: User | None = None
        self._auth_service: AuthService | None = None

    @cached_property
    def dataloaders(self) -> DataLoaders:
        if self.db_session is None:
            raise RuntimeError("Database session not available")
        return DataLoaders(_session=self.db_session)

    @cached_property
    def auth_service(self) -> AuthService:
        if self._auth_service:
            return self._auth_service
        if self.db_session is None:
            raise RuntimeError("Database session not available")
        return AuthService(self.db_session)

    @cached_property
    def embedding_service(self) -> IEmbeddingService:
        """
        嵌入服務（Singleton）

        ABP 對比：
        - ABP: services.AddSingleton<IEmbeddingService, LocalEmbeddingService>()
        - Python: 使用 lru_cache 實現 Singleton
        """
        return get_embedding_service()

    @cached_property
    def vector_repository(self) -> VectorRepository:
        """
        向量儲存庫（Per-Request）

        ABP 對比：
        - ABP: services.AddTransient<IVectorRepository, VectorRepository>()
        - Python: 每個請求建立新實例，共用 session
        """
        if self.db_session is None:
            raise RuntimeError("Database session not available")
        return VectorRepository(self.db_session, self.embedding_service)

    @cached_property
    def search_service(self) -> SearchService:
        """
        搜尋服務（Per-Request）

        ABP 對比：
        - ABP: services.AddTransient<ISearchAppService, SearchAppService>()
        - Python: 每個請求建立新實例
        """
        return SearchService(self.embedding_service, self.vector_repository)

    @cached_property
    def document_service(self) -> DocumentService:
        """
        文件服務（Per-Request）

        ABP 對比：
        - ABP: services.AddTransient<IDocumentAppService, DocumentAppService>()
        - Python: 每個請求建立新實例，注入 vector_repository 用於自動索引
        """
        if self.db_session is None:
            raise RuntimeError("Database session not available")
        return DocumentService(self.db_session, self.vector_repository)

    @property
    def current_user(self) -> User | None:
        if self._current_user is not None:
            return self._current_user

        token = self._get_token()
        if not token:
            return None

        self._current_user = self.auth_service.verify_token(token)
        return self._current_user

    def _get_token(self) -> str | None:
        if self.request:
            auth_header = self.request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                return auth_header[7:]

        if self.connection_params:
            token = self.connection_params.get("authToken")
            if token and isinstance(token, str):
                if token.startswith("Bearer "):
                    return token[7:]
                return token

        return None
