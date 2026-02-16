from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from sqlalchemy import func ,exists
from uuid import UUID
from app.models.seats import Seat
from app.models.booking import Booking

class SeatRepositoryBase(ABC):

    @abstractmethod
    def create_seat(self, db: Session, seat: Seat) -> Seat:
        pass

    @abstractmethod
    def get_seat_by_seat_number(self, db: Session, seat_number: str):
        pass

    @abstractmethod
    def get_all_seat(self, db: Session):
        pass

    @abstractmethod
    def seat_stats(self, db: Session):
        pass

    @abstractmethod
    def get_by_id(self, db: Session, seat_id: UUID):
        pass

    @abstractmethod
    def delete(self, db: Session, seat: Seat):
        pass
    @abstractmethod
    def seat_has_bookings(self, db : Session, seat_id : UUID)-> bool:
        pass
    @abstractmethod
    
    def update_seat(self, db: Session, seat: Seat, update_data: dict):
        pass
    


class SeatRepository(SeatRepositoryBase):

    def create_seat(self, db: Session, seat: Seat) -> Seat:
        try:
            db.add(seat)
            db.commit()
            db.refresh(seat)
            return seat
        except Exception:
            db.rollback()
            raise

    def get_seat_by_seat_number(self, db: Session, seat_number: str):
        return db.query(Seat).filter(Seat.seat_number == seat_number).first()

    def get_all_seat(self, db: Session):
        return db.query(Seat).all()

    def seat_stats(self, db: Session):
        total = db.query(func.count(Seat.id)).scalar()
        active = db.query(func.count(Seat.id)).filter(
            Seat.is_active.is_(True)
        ).scalar()
        inactive = db.query(func.count(Seat.id)).filter(
            Seat.is_active.is_(False)
        ).scalar()

        return {
            "total": total,
            "active": active,
            "inactive": inactive
        }

    def get_by_id(self, db: Session, seat_id: UUID):
        return db.query(Seat).filter(Seat.id == seat_id).first()

    def delete(self, db: Session, seat: Seat):
        try:
            db.delete(seat)
            db.commit()
        except Exception:
            db.rollback()
            raise
        
    def seat_has_bookings(self, db: Session, seat_id: UUID) -> bool:
        return db.query(
            exists().where(Booking.seat_id == seat_id)
            ).scalar()or False
        
        
        
    def update_seat(self, db: Session, seat: Seat, update_data: dict):
        for key, value in update_data.items():
            setattr(seat, key, value)

        db.commit()
        db.refresh(seat)
        return seat

