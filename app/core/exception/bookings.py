


from backend.app.core.exception.base import AppException



class BookingNotFoundException(AppException):
    def __init__(self):
        super().__init__(
            "Booking not found.",
            404,
            "BOOKING_NOT_FOUND",
        )


class BookingAlreadyCancelledException(AppException):
    def __init__(self):
        super().__init__(
            "Booking already cancelled.",
            409,
            "BOOKING_ALREADY_CANCELLED",
        )


class BookingAlreadyCompletedException(AppException):
    def __init__(self):
        super().__init__(
            "Booking already completed.",
            409,
            "BOOKING_ALREADY_COMPLETED",
        )


class InvalidBookingTimeException(AppException):
    def __init__(self):
        super().__init__(
            "Invalid booking time.",
            400,
            "INVALID_BOOKING_TIME",
        )


class BookingConflictException(AppException):
    def __init__(self):
        super().__init__(
            "Booking time overlaps with an existing booking.",
            409,
            "BOOKING_CONFLICT",
        )


class BookingLimitExceededException(AppException):
    def __init__(self):
        super().__init__(
            "Booking limit exceeded.",
            400,
            "BOOKING_LIMIT_EXCEEDED",
        )