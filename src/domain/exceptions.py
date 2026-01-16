from typing import Any


class ApplicationError(Exception):
    message: str = "An error occurred"
    code: str = "APPLICATION_ERROR"

    def __init__(
        self,
        message: str | None = None,
        code: str | None = None,
        details: dict[str, Any] | None = None,
    ):
        self.message = message or self.__class__.message
        self.code = code or self.__class__.code
        self.details = details or {}
        super().__init__(self.message)


class NotFoundError(ApplicationError):
    message = "Resource not found"
    code = "NOT_FOUND"


class ValidationError(ApplicationError):
    message = "Validation failed"
    code = "VALIDATION_ERROR"


class AuthenticationError(ApplicationError):
    message = "Authentication failed"
    code = "UNAUTHENTICATED"


class AuthorizationError(ApplicationError):
    message = "Permission denied"
    code = "FORBIDDEN"
