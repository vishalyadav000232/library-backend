from app.core.exception.base import AppException


class ShiftNotFoundException(AppException):
    def __init__(self):
        super().__init__(
            message="Shift not found.",
            status_code=404,
            error_code="SHIFT_NOT_FOUND",
        )


class ShiftAlreadyExistsException(AppException):
    def __init__(self):
        super().__init__(
            message="Shift already exists.",
            status_code=409,
            error_code="SHIFT_ALREADY_EXISTS",
        )


class InvalidShiftTimeException(AppException):
    def __init__(self):
        super().__init__(
            message="Start time must be before end time.",
            status_code=400,
            error_code="INVALID_SHIFT_TIME",
        )


class ShiftCacheException(AppException):
    def __init__(self):
        super().__init__(
            message="Shift cache operation failed.",
            status_code=500,
            error_code="SHIFT_CACHE_ERROR",
        )