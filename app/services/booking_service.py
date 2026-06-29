import hashlib
import hmac
import logging
import os
import uuid
from abc import ABC, abstractmethod

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.exception.bookings import (
    BookingConflictException,
    BookingNotFoundException,
    InvalidBookingTimeException,
    InvalidBookingStatusException,
)
from app.core.exception.database import DatabaseException
from app.core.exception.payment import (
    InvalidPaymentException,
    PaymentAlreadyCompletedException,
    PaymentNotFoundException,
    PaymentProviderException,
)
from app.core.exception.seat import (
    SeatNotFoundException,
    SeatTemporarilyLockedException,
)
from app.models.booking import Booking
from app.models.payment import Payment, PaymentStatus
from app.payments.client import client
from app.redis.bookings_lock import lock_seat, unlock_seat
from app.repository.booking_repository import BookingRepositoryBase
from app.repository.seat_repository import SeatRepository
from app.schemas.booking import BookingReport
from app.utils.booking_utils import normalize_date
from app.websockets.manger import manager


logger = logging.getLogger(__name__)


class BookingServiceBase(ABC):

    @abstractmethod
    async def create_booking(self, db: Session, booking_data, user_id):
        pass

    @abstractmethod
    def get_all_bookings(self, db: Session):
        pass

    @abstractmethod
    def get_booking_by_id(self, db: Session, booking_id):
        pass

    @abstractmethod
    def cancel_booking(self, db: Session, booking_id):
        pass

    @abstractmethod
    def my_bookings(self, db: Session, user_id):
        pass

    @abstractmethod
    def get_booking_report(self, db: Session):
        pass


class BookingService(BookingServiceBase):

    def __init__(self, repo: BookingRepositoryBase):
        self.repo = repo
        self.seat_repo = SeatRepository()

    async def create_booking(self, db: Session, booking_data, user_id):
        start_date = normalize_date(booking_data.start_date)
        end_date = normalize_date(booking_data.end_date)

        logger.info(
            "Creating booking. user_id=%s seat_id=%s shift_id=%s start_date=%s end_date=%s",
            user_id,
            booking_data.seat_id,
            booking_data.shift_id,
            start_date,
            end_date,
        )

        if end_date < start_date:
            logger.warning(
                "Invalid booking time. user_id=%s start_date=%s end_date=%s",
                user_id,
                start_date,
                end_date,
            )
            raise InvalidBookingTimeException()

        locked = lock_seat(
            booking_data.seat_id,
            booking_data.shift_id,
            start_date,
        )

        if not locked:
            logger.warning(
                "Seat temporarily locked. seat_id=%s shift_id=%s start_date=%s",
                booking_data.seat_id,
                booking_data.shift_id,
                start_date,
            )
            raise SeatTemporarilyLockedException()

        try:
            is_available = self.repo.is_seat_available(
                db,
                booking_data.seat_id,
                booking_data.shift_id,
                start_date,
            )

            if not is_available:
                logger.warning(
                    "Booking conflict. seat_id=%s shift_id=%s start_date=%s",
                    booking_data.seat_id,
                    booking_data.shift_id,
                    start_date,
                )

                unlock_seat(
                    booking_data.seat_id,
                    booking_data.shift_id,
                    start_date,
                )

                raise BookingConflictException()

            booking = Booking(
                id=uuid.uuid4(),
                user_id=user_id,
                seat_id=booking_data.seat_id,
                shift_id=booking_data.shift_id,
                start_date=start_date,
                end_date=end_date,
                status="PENDING",
            )

            saved_booking = self.repo.create(db, booking)

            logger.info(
                "Booking created successfully. booking_id=%s user_id=%s",
                saved_booking.id,
                user_id,
            )

            await manager.broadcast(
                {
                    "type": "SEAT_UPDATE",
                    "seat_id": str(booking_data.seat_id),
                    "status": "LOCKED",
                }
            )

            return saved_booking

        except BookingConflictException:
            raise

        except IntegrityError:
            db.rollback()

            unlock_seat(
                booking_data.seat_id,
                booking_data.shift_id,
                start_date,
            )

            logger.exception(
                "Race condition while booking seat. seat_id=%s shift_id=%s start_date=%s",
                booking_data.seat_id,
                booking_data.shift_id,
                start_date,
            )

            raise BookingConflictException()

        except SQLAlchemyError:
            db.rollback()

            unlock_seat(
                booking_data.seat_id,
                booking_data.shift_id,
                start_date,
            )

            logger.exception("Database error while creating booking.")
            raise DatabaseException()

    def get_all_bookings(self, db: Session):
        try:
            logger.info("Fetching all bookings")
            return self.repo.get_all_bookings(db)

        except SQLAlchemyError:
            logger.exception("Database error while fetching all bookings.")
            raise DatabaseException()

    def get_booking_by_id(self, db: Session, booking_id):
        try:
            logger.info("Fetching booking. booking_id=%s", booking_id)

            booking = self.repo.get_booking_by_id(db, booking_id)

            if not booking:
                logger.warning("Booking not found. booking_id=%s", booking_id)
                raise BookingNotFoundException()

            return booking

        except BookingNotFoundException:
            raise

        except SQLAlchemyError:
            logger.exception(
                "Database error while fetching booking. booking_id=%s",
                booking_id,
            )
            raise DatabaseException()

    def cancel_booking(self, db: Session, booking_id):
        try:
            logger.info("Cancelling booking. booking_id=%s", booking_id)

            booking = self.repo.get_booking_by_id(db, booking_id)

            if not booking:
                logger.warning("Cancel failed. Booking not found. booking_id=%s", booking_id)
                raise BookingNotFoundException()

            if booking.status != "ACTIVE":
                logger.warning(
                    "Cancel failed. Invalid booking status. booking_id=%s status=%s",
                    booking_id,
                    booking.status,
                )
                raise InvalidBookingStatusException()

            cancelled_booking = self.repo.update_booking_status(
                db,
                booking,
                "CANCELLED",
            )

            unlock_seat(
                booking.seat_id,
                booking.shift_id,
                booking.start_date,
            )

            logger.info("Booking cancelled successfully. booking_id=%s", booking_id)

            return cancelled_booking

        except (BookingNotFoundException, InvalidBookingStatusException):
            raise

        except SQLAlchemyError:
            db.rollback()
            logger.exception(
                "Database error while cancelling booking. booking_id=%s",
                booking_id,
            )
            raise DatabaseException()

    def my_bookings(self, db: Session, user_id):
        try:
            logger.info("Fetching user bookings. user_id=%s", user_id)
            return self.repo.my_booking(db, user_id)

        except SQLAlchemyError:
            logger.exception(
                "Database error while fetching user bookings. user_id=%s",
                user_id,
            )
            raise DatabaseException()

    def get_booking_report(self, db: Session):
        try:
            logger.info("Generating booking report")

            rows = self.repo.get_full_booking_data(db)

            result = []

            for booking, user, seat, payment, shift in rows:
                result.append(
                    BookingReport(
                        booking_id=booking.id,
                        booking_date=booking.start_date,
                        status=booking.status,
                        user={
                            "id": user.id,
                            "name": user.name,
                            "email": user.email,
                        },
                        seat={
                            "seat_number": seat.seat_number,
                            "floor": seat.floor,
                            "amount": seat.price,
                        },
                        payment={
                            "amount": payment.amount if payment else None,
                            "status": payment.status if payment else "pending",
                        },
                        shift={
                            "name": shift.name,
                            "start_time": shift.start_time,
                            "end_time": shift.end_time,
                        },
                    )
                )

            logger.info("Booking report generated. count=%s", len(result))

            return result

        except SQLAlchemyError:
            logger.exception("Database error while generating booking report.")
            raise DatabaseException()

    async def confirm_booking_after_payment(self, db: Session, booking_id):
        try:
            logger.info("Confirming booking after payment. booking_id=%s", booking_id)

            booking = self.repo.get_booking_by_id(db, booking_id)

            if not booking:
                logger.warning(
                    "Confirm booking failed. Booking not found. booking_id=%s",
                    booking_id,
                )
                raise BookingNotFoundException()

            booking.status = "CONFIRMED"

            db.commit()
            db.refresh(booking)

            unlock_seat(
                booking.seat_id,
                booking.shift_id,
                booking.start_date,
            )

            await manager.broadcast(
                {
                    "type": "SEAT_UPDATE",
                    "seat_id": str(booking.seat_id),
                    "status": "BOOKED",
                }
            )

            logger.info("Booking confirmed successfully. booking_id=%s", booking_id)

            return booking

        except BookingNotFoundException:
            raise

        except SQLAlchemyError:
            db.rollback()
            logger.exception(
                "Database error while confirming booking. booking_id=%s",
                booking_id,
            )
            raise DatabaseException()

    async def create_booking_with_payment(self, db: Session, booking_data, user_id):
        try:
            logger.info(
                "Creating booking with payment. user_id=%s seat_id=%s",
                user_id,
                booking_data.seat_id,
            )

            booking = await self.create_booking(
                db,
                booking_data,
                user_id=user_id,
            )

            seat = self.seat_repo.get_by_id(db, booking.seat_id)

            if not seat:
                logger.warning("Seat not found. seat_id=%s", booking.seat_id)
                raise SeatNotFoundException()

            amount = seat.price

            order = client.order.create(
                {
                    "amount": int(amount * 100),
                    "currency": "INR",
                }
            )

            payment = Payment(
                user_id=user_id,
                booking_id=booking.id,
                amount=amount,
                provider_order_id=order["id"],
                status=PaymentStatus.CREATED,
            )

            db.add(payment)
            db.commit()
            db.refresh(payment)

            logger.info(
                "Payment order created. booking_id=%s order_id=%s amount=%s",
                booking.id,
                order["id"],
                amount,
            )

            return {
                "booking_id": str(booking.id),
                "order_id": order["id"],
                "amount": amount,
                "key": os.getenv("RAZORPAY_KEY_ID"),
            }

        except (
            SeatNotFoundException,
            SeatTemporarilyLockedException,
            BookingConflictException,
            InvalidBookingTimeException,
        ):
            raise

        except SQLAlchemyError:
            db.rollback()
            logger.exception("Database error while creating booking payment.")
            raise DatabaseException()

        except Exception:
            db.rollback()

            if "booking" in locals():
                unlock_seat(
                    booking.seat_id,
                    booking.shift_id,
                    booking.start_date,
                )

            logger.exception("Payment provider error while creating order.")
            raise PaymentProviderException()

    async def verify_payment(self, db: Session, data: dict):
        try:
            logger.info("Verifying payment. order_id=%s", data.get("order_id"))

            secret = os.getenv("RAZORPAY_KEY_SECRET")

            if not secret:
                logger.error("RAZORPAY_KEY_SECRET is missing.")
                raise PaymentProviderException()

            generated_signature = hmac.new(
                secret.encode("utf-8"),
                (data["order_id"] + "|" + data["payment_id"]).encode("utf-8"),
                hashlib.sha256,
            ).hexdigest()

            if generated_signature != data["signature"]:
                logger.warning(
                    "Invalid payment signature. order_id=%s",
                    data.get("order_id"),
                )
                raise InvalidPaymentException()

            payment = (
                db.query(Payment)
                .filter(Payment.provider_order_id == data["order_id"])
                .first()
            )

            if not payment:
                logger.warning(
                    "Payment not found. order_id=%s",
                    data.get("order_id"),
                )
                raise PaymentNotFoundException()

            if payment.status == PaymentStatus.SUCCESS:
                logger.info(
                    "Payment already processed. payment_id=%s",
                    payment.id,
                )
                raise PaymentAlreadyCompletedException()

            payment.status = PaymentStatus.SUCCESS
            payment.provider_payment_id = data["payment_id"]

            booking = db.query(Booking).get(payment.booking_id)

            if not booking:
                logger.warning(
                    "Booking not found during payment verify. booking_id=%s",
                    payment.booking_id,
                )
                raise BookingNotFoundException()

            booking.status = "CONFIRMED"

            unlock_seat(
                booking.seat_id,
                booking.shift_id,
                booking.start_date,
            )

            db.commit()
            db.refresh(payment)
            db.refresh(booking)

            await manager.broadcast(
                {
                    "type": "SEAT_UPDATE",
                    "seat_id": str(booking.seat_id),
                    "status": "BOOKED",
                }
            )

            logger.info(
                "Payment verified successfully. booking_id=%s payment_id=%s",
                booking.id,
                payment.id,
            )

            return {"message": "Payment success"}

        except (
            InvalidPaymentException,
            PaymentNotFoundException,
            PaymentAlreadyCompletedException,
            BookingNotFoundException,
            PaymentProviderException,
        ):
            raise

        except SQLAlchemyError:
            db.rollback()
            logger.exception("Database error while verifying payment.")
            raise DatabaseException()