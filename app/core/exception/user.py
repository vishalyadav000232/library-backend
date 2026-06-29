

from app.core.exception.base import AppException


class UserNotFoundException(AppException):
    def __init__(self):
        super().__init__(
            "User not found.",
            404,
            "USER_NOT_FOUND",
        )


class EmailAlreadyExistsException(AppException):
    def __init__(self):
        super().__init__(
            "Email already registered.",
            409,
            "EMAIL_ALREADY_EXISTS",
        )


class AccountDisabledException(AppException):
    def __init__(self):
        super().__init__(
            "Account is disabled.",
            403,
            "ACCOUNT_DISABLED",
        )
    
class UserCacheException(AppException):
    def __init__(self):
        super().__init__(
            message="User cache operation failed.",
            status_code=500,
            error_code="USER_CACHE_ERROR",
        )