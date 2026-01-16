import strawberry
from strawberry.types import Info

from src.api.graphql.context import GraphQLContext
from src.api.graphql.permissions.auth import IsAuthenticated
from src.api.graphql.types.document import DocumentType


@strawberry.type
class DocumentQuery:
    @strawberry.field(permission_classes=[IsAuthenticated])
    async def document(
        self,
        info: Info[GraphQLContext, None],
        id: strawberry.ID,
    ) -> DocumentType | None:
        return await info.context.dataloaders.document_loader.load(str(id))

    @strawberry.field(permission_classes=[IsAuthenticated])
    async def documents(
        self,
        info: Info[GraphQLContext, None],
        limit: int = 10,
        offset: int = 0,
    ) -> list[DocumentType]:
        user = info.context.current_user
        if not user:
            return []

        docs = await info.context.document_service.list_documents(
            user_id=user.id,
            limit=limit,
            offset=offset,
        )
        return [DocumentType.from_domain(doc) for doc in docs]
