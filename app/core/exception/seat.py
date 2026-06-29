from app.core.exception.base import AppException

class SeatNotFoundException(AppException):
    def __init__(self):
        super().__init__(
            "Seat not found.",
            404,
            "SEAT_NOT_FOUND",
        )


class SeatAlreadyBookedException(AppException):
    def __init__(self):
        super().__init__(
            "Seat is already booked.",
            409,
            "SEAT_ALREADY_BOOKED",
        )


class SeatUnavailableException(AppException):
    def __init__(self):
        super().__init__(
            "Seat is currently unavailable.",
            409,
            "SEAT_UNAVAILABLE",
        )


class InvalidSeatStatusException(AppException):
    def __init__(self):
        super().__init__(
            "Invalid seat status.",
            400,
            "INVALID_SEAT_STATUS",
        )

class SeatTemporarilyLockedException(AppException):
    def __init__(self):
        super().__init__(
            "Seat are temporary locked",
            400,
            "SEAT_TEMP_LOCKED"
        )
    
class SeatAlreadyExistsException(AppException):
    def __init__(self):
        super().__init__(
            message="Seat already exists.",
            status_code=409,
            error_code="SEAT_ALREADY_EXISTS",
        )


class SeatHasActiveBookingsException(AppException):
    def __init__(self):
        super().__init__(
            message="Seat has active bookings and cannot be deleted.",
            status_code=400,
            error_code="SEAT_HAS_ACTIVE_BOOKINGS",
        )


class SeatTemporarilyLockedException(AppException):
    def __init__(self):
        super().__init__(
            message="Seat is temporarily locked.",
            status_code=409,
            error_code="SEAT_TEMPORARILY_LOCKED",
        )