
from app.core.exception.base import AppException

class DatabaseException(AppException):
    def __init__(self):
        super().__init__(
            "Database operation failed.",
            500,
            "DATABASE_ERROR",
        )


class DuplicateRecordException(AppException):
    def __init__(self):
        super().__init__(
            "Duplicate record.",
            409,
            "DUPLICATE_RECORD",
        )