import strawberry


@strawberry.input
class CreateDocumentInput:
    title: str
    content: str


@strawberry.input
class UpdateDocumentInput:
    id: strawberry.ID
    title: str | None = None
    content: str | None = None


@strawberry.input
class LoginInput:
    email: str
    password: str


@strawberry.input
class RegisterInput:
    email: str
    password: str
    name: str
