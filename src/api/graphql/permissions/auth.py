from typing import Any

from strawberry.permission import BasePermission
from strawberry.types import Info

from src.api.graphql.context import GraphQLContext


class IsAuthenticated(BasePermission):
    message = "User is not authenticated"
    error_extensions = {"code": "UNAUTHENTICATED"}

    def has_permission(
        self,
        source: Any,
        info: Info[GraphQLContext, None],
        **kwargs: Any,
    ) -> bool:
        return info.context.current_user is not None
