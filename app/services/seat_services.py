# app/services/seat_services.py
from sqlalchemy.orm import Session
from app.models.seats import Seat
from app.schemas.seats import SeatCreate
from app.repository.seat_repository import SeatRepository
from abc import ABC, abstractmethod


class SeatServiceBase(ABC):
    
    @abstractmethod
    def create_seat(self, db: Session, sear: Seat):
        pass

    @abstractmethod
    def get_all_seat(self , db :Session ):
        pass


class SeatSearvice(SeatServiceBase):
    def __init__(self, repo: SeatRepository):
        self.repo = repo

    def get_all_seat(self , db :Session ):
        return self.repo.get_all_seat(db)

    def create_seat(self, db: Session, seat_data: SeatCreate):

        if self.repo.get_seat_by_seat_number(db , seat_data.seat_number):
            raise ValueError("Seat already exists")

        seat = Seat(
            seat_number=seat_data.seat_number,
            is_active=seat_data.is_active,  # default True from schema
            floor=seat_data.floor

        )

    
        return self.repo.create_seat(db , seat)
    
