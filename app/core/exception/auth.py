from app.core.exception.base import AppException







class InvalidCredentialsException(AppException):
    def __init__(self):
        super().__init__(
            "Invalid email or password.",
            401,
            "INVALID_CREDENTIALS",
        )


class InvalidTokenException(AppException):
    def __init__(self):
        super().__init__(
            "Invalid access token.",
            401,
            "INVALID_TOKEN",
        )


class TokenExpiredException(AppException):
    def __init__(self):
        super().__init__(
            "Access token has expired.",
            401,
            "TOKEN_EXPIRED",
        )


class UnauthorizedException(AppException):
    def __init__(self):
        super().__init__(
            "Authentication required.",
            401,
            "UNAUTHORIZED",
        )


class ForbiddenException(AppException):
    def __init__(self):
        super().__init__(
            "You are not allowed to perform this action.",
            403,
            "FORBIDDEN",
        )