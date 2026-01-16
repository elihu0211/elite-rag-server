import strawberry
from strawberry.types import Info

from src.api.graphql.context import GraphQLContext
from src.api.graphql.types.auth import AuthPayload
from src.api.graphql.types.inputs import LoginInput, RegisterInput
from src.api.graphql.types.user import UserType


@strawberry.type
class AuthMutation:
    @strawberry.mutation
    async def register(
        self,
        info: Info[GraphQLContext, None],
        input: RegisterInput,
    ) -> AuthPayload:
        auth_service = info.context.auth_service

        user = await auth_service.register(
            email=input.email,
            password=input.password,
            name=input.name,
        )

        token = await auth_service.login(input.email, input.password)

        return AuthPayload(
            token=token,
            user=UserType.from_domain(user),
        )

    @strawberry.mutation
    async def login(
        self,
        info: Info[GraphQLContext, None],
        input: LoginInput,
    ) -> AuthPayload:
        """
        使用者登入

        ABP/HotChocolate 對比：
        [Mutation]
        public async Task<AuthPayload> Login(LoginInput input)
        {
            var token = await _authService.LoginAsync(input);
            var user = await _authService.GetCurrentUserAsync();
            return new AuthPayload { Token = token, User = user };
        }
        """
        auth_service = info.context.auth_service

        token = await auth_service.login(input.email, input.password)

        # 安全地驗證 token 並取得用戶
        verified_user = auth_service.verify_token(token)
        if verified_user is None:
            raise ValueError("Token verification failed")

        user = await auth_service.get_user_by_id(verified_user.id)
        if user is None:
            raise ValueError("User not found")

        return AuthPayload(
            token=token,
            user=UserType.from_domain(user),
        )
