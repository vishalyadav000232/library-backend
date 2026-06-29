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