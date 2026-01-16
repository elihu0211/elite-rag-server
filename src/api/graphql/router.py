"""
GraphQL Router 設定

ABP/HotChocolate 對比：
- HotChocolate: services.AddGraphQLServer().AddQueryType<Query>()
- Python Strawberry: GraphQLRouter 整合 FastAPI
"""

from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.fastapi import GraphQLRouter

from src.api.graphql.context import GraphQLContext
from src.api.graphql.schema import schema
from src.infrastructure.persistence.database import get_async_session


async def get_context(
    request: Request,
    db_session: Annotated[AsyncSession, Depends(get_async_session)],
) -> GraphQLContext:
    """
    建立 GraphQL Context

    ABP 對比：
    - ABP 使用 IHttpContextAccessor 和 DI 自動注入
    - Python 使用 Annotated + Depends 實現依賴注入
    """
    return GraphQLContext(
        request=request,
        db_session=db_session,
    )


graphql_router = GraphQLRouter(
    schema=schema,
    context_getter=get_context,
)
