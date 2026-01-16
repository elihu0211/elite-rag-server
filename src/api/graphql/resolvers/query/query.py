"""
GraphQL Query 根類型

ABP/HotChocolate 對比：
- HotChocolate 使用 [ExtendObjectType] 擴展 Query
- Python Strawberry 使用多重繼承組合 Query
"""
import strawberry

from src.api.graphql.resolvers.query.document_query import DocumentQuery
from src.api.graphql.resolvers.query.search_query import SearchQuery


@strawberry.type
class Query(DocumentQuery, SearchQuery):
    @strawberry.field
    def health(self) -> str:
        return "ok"
