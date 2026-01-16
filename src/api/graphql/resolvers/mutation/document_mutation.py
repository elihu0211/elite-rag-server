import strawberry
from strawberry.types import Info

from src.api.graphql.context import GraphQLContext
from src.api.graphql.permissions.auth import IsAuthenticated
from src.api.graphql.types.document import DocumentType
from src.api.graphql.types.inputs import CreateDocumentInput, UpdateDocumentInput


@strawberry.type
class DocumentMutation:
    @strawberry.mutation(permission_classes=[IsAuthenticated])
    async def create_document(
        self,
        info: Info[GraphQLContext, None],
        input: CreateDocumentInput,
    ) -> DocumentType:
        user = info.context.current_user
        if not user:
            raise Exception("Not authenticated")

        doc = await info.context.document_service.create_document(
            title=input.title,
            content=input.content,
            user_id=user.id,
        )
        return DocumentType.from_domain(doc)

    @strawberry.mutation(permission_classes=[IsAuthenticated])
    async def update_document(
        self,
        info: Info[GraphQLContext, None],
        input: UpdateDocumentInput,
    ) -> DocumentType:
        user = info.context.current_user
        if not user:
            raise Exception("Not authenticated")

        doc = await info.context.document_service.update_document(
            id=str(input.id),
            title=input.title,
            content=input.content,
            user_id=user.id,
        )
        return DocumentType.from_domain(doc)

    @strawberry.mutation(permission_classes=[IsAuthenticated])
    async def delete_document(
        self,
        info: Info[GraphQLContext, None],
        id: strawberry.ID,
    ) -> bool:
        user = info.context.current_user
        if not user:
            raise Exception("Not authenticated")

        return await info.context.document_service.delete_document(
            id=str(id),
            user_id=user.id,
        )
