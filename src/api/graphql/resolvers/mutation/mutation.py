"""
GraphQL Mutation 根類型

ABP/HotChocolate 對比：
- HotChocolate 使用 [ExtendObjectType] 擴展 Mutation
- Python Strawberry 使用多重繼承組合 Mutation
"""
import strawberry

from src.api.graphql.resolvers.mutation.auth_mutation import AuthMutation
from src.api.graphql.resolvers.mutation.document_mutation import DocumentMutation


@strawberry.type
class Mutation(AuthMutation, DocumentMutation):
    pass
