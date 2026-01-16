"""
GraphQL DataLoaders 容器

ABP 對比：
- ABP 沒有直接對應，但概念類似 IRepository 的批次查詢
- DataLoader 用於解決 N+1 查詢問題
"""

from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from src.api.graphql.dataloaders.document_loader import DocumentLoader
from src.api.graphql.dataloaders.user_loader import UserLoader


@dataclass
class DataLoaders:
    _session: AsyncSession
    _document_loader: DocumentLoader | None = None
    _user_loader: UserLoader | None = None

    @property
    def document_loader(self) -> DocumentLoader:
        if self._document_loader is None:
            self._document_loader = DocumentLoader(self._session)
        return self._document_loader

    @property
    def user_loader(self) -> UserLoader:
        if self._user_loader is None:
            self._user_loader = UserLoader(self._session)
        return self._user_loader
