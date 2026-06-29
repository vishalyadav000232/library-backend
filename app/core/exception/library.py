from app.core.exception.base import AppException



class LibraryClosedException(AppException):
    def __init__(self):
        super().__init__(
            "Library is closed.",
            400,
            "LIBRARY_CLOSED",
        )


class MaintenanceModeException(AppException):
    def __init__(self):
        super().__init__(
            "Library is under maintenance.",
            503,
            "MAINTENANCE_MODE",
        )