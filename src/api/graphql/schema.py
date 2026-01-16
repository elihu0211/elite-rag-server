import strawberry

from src.api.graphql.resolvers.query.query import Query
from src.api.graphql.resolvers.mutation.mutation import Mutation


schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
)
