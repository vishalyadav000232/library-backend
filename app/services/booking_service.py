from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.booking import Booking
from app.utils.booking_utils import normalize_date
from app.repository.booking_repository import BookingRepository , BookingRepositoryBase
import uuid
from abc import ABC , abstractmethod
from app.schemas.booking import BookingReport
class BookingServiceBase(ABC):
    
    @abstractmethod
    def create_booking(self, db: Session, booking_data):
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
    def get_booking_report(self , db :Session):
        pass


class BookingService(BookingServiceBase):

    def __init__(self, repo: BookingRepositoryBase):
        self.repo = repo

    def create_booking(self, db: Session, booking_data):
        start_date = normalize_date(booking_data.start_date)
        end_date = normalize_date(booking_data.end_date)

        if end_date < start_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="end_date cannot be less than start_date"
            )

        if not self.repo.is_seat_available(
            db,
            booking_data.seat_id,
            booking_data.shift_id,
            start_date
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Seat already booked for this shift"
            )

        booking = Booking(
            id=uuid.uuid4(),
            user_id=booking_data.user_id,
            seat_id=booking_data.seat_id,
            shift_id=booking_data.shift_id,
            start_date=start_date,
            end_date=end_date,
            status="ACTIVE"
        )

        try:
            return self.repo.create(db, booking)

        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Seat already booked (race condition)"
            )

    def get_all_bookings(self, db: Session):
        return self.repo.get_all_bookings(db)

    def get_booking_by_id(self, db: Session, booking_id):
        booking = self.repo.get_booking_by_id(db, booking_id)
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found"
            )
        return booking

    def cancel_booking(self, db: Session, booking_id):
        booking = self.repo.get_booking_by_id(db, booking_id)

        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found"
            )

        if booking.status != "ACTIVE":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only active bookings can be cancelled"
            )

        return self.repo.update_booking_status(
            db,
            booking,
            "CANCELLED"
        )
    
    def my_bookings(self, db: Session, user_id):   
        return self.repo.my_booking(db, user_id)  

    def get_booking_report(self , db :Session):
        rows = self.repo.get_full_booking_data(db)


        result = []

        for booking , user , seat , payment  , shift in rows:
            result.append(
                    BookingReport(
                    booking_id=booking.id,
                    booking_date=booking.start_date,
                    status=booking.status,
                    user={
                        "id": user.id,
                        "name": user.name,
                        "email": user.email
                    },
                    seat={
                        "seat_number": seat.seat_number,
                        "floor": seat.floor,
                        "amount": seat.price
                    },
                    payment={
                        "amount": payment.amount if payment else None,
                        "status": payment.status if payment else "pending"
                    },
                    shift= {
                        "name" : shift.name,
                        "start_time" : shift.start_time,
                        "end_time" : shift.end_time
                    }



                    

                )
            )

        return result
            


