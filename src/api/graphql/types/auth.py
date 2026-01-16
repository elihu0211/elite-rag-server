import strawberry

from src.api.graphql.types.user import UserType


@strawberry.type
class AuthPayload:
    token: str
    user: UserType
