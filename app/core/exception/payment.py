


from app.core.exception.base import AppException


class PaymentNotFoundException(AppException):
    def __init__(self):
        super().__init__(
            "Payment not found.",
            404,
            "PAYMENT_NOT_FOUND",
        )


class PaymentFailedException(AppException):
    def __init__(self):
        super().__init__(
            "Payment failed.",
            400,
            "PAYMENT_FAILED",
        )


class PaymentAlreadyCompletedException(AppException):
    def __init__(self):
        super().__init__(
            "Payment already completed.",
            409,
            "PAYMENT_ALREADY_COMPLETED",
        )


class RefundFailedException(AppException):
    def __init__(self):
        super().__init__(
            "Refund failed.",
            400,
            "REFUND_FAILED",
        )
    
class PaymentProviderException(AppException):
    def __init__(self ):
        super().__init__(
            "Payment Provider not ready",
            400,
            "PAYMENT_PROVIDER_ERROR"
        )
class InvalidPaymentException(AppException):
    def __init__(self ):
        super().__init__(
            "Payment Provider not ready",
            400,
            "PAYMENT_PROVIDER_ERROR"
        )