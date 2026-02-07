

from abc import ABC, abstractmethod
from app.models.seats import Seat
from sqlalchemy.orm import Session
from sqlalchemy import func


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
        return db.query(Seat).order_by(Seat.seat_number.asc()).all()

    def get_all_seat(self, db):
        return db.query(Seat).all()

    def seat_stats(self, db: Session):

        total = db.query(func.count(Seat.id)).scalar()
        active = db.query(func.count(Seat.id)).filter(
            Seat.is_active == True).scalar()
        inactive = db.query(func.count(Seat.id)).filter(
            Seat.is_active == False).scalar()

        return {
            "total": total,
            "active": active,
            "inactive": inactive
        }
