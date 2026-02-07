
from sqlalchemy.orm import Session
from app.models.booking import Booking
from uuid import UUID
from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from app.models.booking import Booking
from uuid import UUID
from typing import List, Optional

class BookingRepositoryBase(ABC):

    @abstractmethod
    def is_seat_available(
        self,
        db: Session,
        seat_id: UUID,
        shift_id: UUID,
        start_date
    ) -> bool:
        pass

    @abstractmethod
    def create(self, db: Session, booking: Booking) -> Booking:
        pass

    @abstractmethod
    def get_all_bookings(self, db: Session) -> List[Booking]:
        pass

    @abstractmethod
    def get_booking_by_id(
        self, db: Session, booking_id: UUID
    ) -> Optional[Booking]:
        pass

    @abstractmethod
    def update_booking_status(
        self, db: Session, booking: Booking, new_status: str
    ) -> Booking:
        pass

    @abstractmethod
    def my_booking(self, db: Session, user_id: UUID) -> List[Booking]:
        pass

class BookingRepository(BookingRepositoryBase):

    def is_seat_available(
        self,
        db: Session,
        seat_id: UUID,
        shift_id: UUID,
        start_date
    ) -> bool:
        return not db.query(Booking).filter(
            Booking.seat_id == seat_id,
            Booking.shift_id == shift_id,
            Booking.start_date <= start_date,
            Booking.end_date >= start_date,
            Booking.status == "ACTIVE"
        ).first()

    def create(self, db: Session, booking: Booking) -> Booking:
        db.add(booking)
        db.commit()
        db.refresh(booking)
        return booking

    def get_all_bookings(self, db: Session):
        return db.query(Booking).all()

    def get_booking_by_id(self, db: Session, booking_id: UUID):
        return db.query(Booking).filter(Booking.id == booking_id).first()

    def update_booking_status(
        self, db: Session, booking: Booking, new_status: str
    ) -> Booking:
        booking.status = new_status
        db.commit()
        db.refresh(booking)
        return booking

    def my_booking(self, db: Session, user_id: UUID):
        return db.query(Booking).filter(Booking.user_id == user_id).all()


    def is_seat_available(
        self,
        db: Session,
        seat_id: UUID,
        shift_id: UUID,
        start_date
    ) -> bool:
        return not db.query(Booking).filter(
            Booking.seat_id == seat_id,
            Booking.shift_id == shift_id,
            Booking.start_date <= start_date,
            Booking.end_date >= start_date,
            Booking.status == "ACTIVE"
        ).first()

    def create(self, db: Session, booking: Booking):
        db.add(booking)
        db.commit()
        db.refresh(booking)
        return booking

    def get_all_bookings(self, db: Session):
        return db.query(Booking).all()

    def get_booking_by_id(self, db: Session, booking_id):
        return db.query(Booking).filter(Booking.id == booking_id).first()

    def update_booking_status(self, db: Session, booking: Booking, new_status: str):
        booking.status = new_status
        db.commit()
        db.refresh(booking)
        return booking

    def cancel_booking(self, db: Session, booking_id):
        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            return None
        db.delete(booking)
        db.commit()
        return booking

    def my_booking(self, db: Session, user_id):
        return db.query(Booking).filter(Booking.user_id == user_id).all()
