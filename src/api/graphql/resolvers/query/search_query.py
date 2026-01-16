"""
搜尋 GraphQL Resolver

ABP/HotChocolate 對比：
- HotChocolate: [Query] public class SearchQuery
- HotChocolate 使用 [Authorize] attribute 做權限控制
- Python Strawberry: permission_classes=[IsAuthenticated]
"""

import strawberry
from strawberry.types import Info

from src.api.graphql.context import GraphQLContext
from src.api.graphql.permissions.auth import IsAuthenticated
from src.api.graphql.types.search import (
    FindSimilarInput,
    SearchDocumentsInput,
    SearchResultType,
    SimilarDocumentType,
)


@strawberry.type
class SearchQuery:
    """
    搜尋 Query Resolver

    ABP/HotChocolate 對比：
    [ExtendObjectType(typeof(Query))]
    public class SearchQuery
    {
        [Query]
        [Authorize]
        public async Task<List<SearchResultType>> SearchDocuments(...)
    }
    """

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def search_documents(
        self,
        info: Info[GraphQLContext, None],
        input: SearchDocumentsInput,
    ) -> list[SearchResultType]:
        """
        語意搜尋文件

        ABP/HotChocolate 對比：
        [Query]
        [Authorize]
        public async Task<List<SearchResultType>> SearchDocuments(
            [Service] ISearchAppService searchService,
            SearchDocumentsInput input)
        {
            return await searchService.SearchDocumentsAsync(input);
        }

        範例查詢：
        query {
            searchDocuments(input: { query: "Python API" }) {
                documentId
                title
                contentPreview
                score
            }
        }
        """
        user = info.context.current_user
        if not user:
            return []

        results = await info.context.search_service.search_documents(
            query=input.query,
            user_id=user.id,
            limit=input.limit,
            threshold=input.threshold,
        )

        return [
            SearchResultType(
                document_id=strawberry.ID(r.document_id),
                title=r.title,
                content_preview=r.content_preview,
                score=r.score,
            )
            for r in results
        ]

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def similar_documents(
        self,
        info: Info[GraphQLContext, None],
        input: FindSimilarInput,
    ) -> list[SimilarDocumentType]:
        """
        找出相似文件

        ABP/HotChocolate 對比：
        [Query]
        [Authorize]
        public async Task<List<SimilarDocumentType>> SimilarDocuments(
            [Service] ISearchAppService searchService,
            FindSimilarInput input)
        {
            return await searchService.FindSimilarDocumentsAsync(input);
        }

        範例查詢：
        query {
            similarDocuments(input: { documentId: "xxx-xxx" }) {
                documentId
                title
                similarityScore
            }
        }
        """
        user = info.context.current_user
        if not user:
            return []

        results = await info.context.search_service.find_similar_documents(
            document_id=str(input.document_id),
            user_id=user.id,
            limit=input.limit,
        )

        return [
            SimilarDocumentType(
                document_id=strawberry.ID(r.document_id),
                title=r.title,
                similarity_score=r.similarity_score,
            )
            for r in results
        ]
