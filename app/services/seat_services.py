from sqlalchemy.orm import Session
from app.models.seats import Seat
from app.schemas.seats import SeatCreate
from app.repository.seat_repository import SeatRepository
from abc import ABC, abstractmethod
from uuid import UUID
from fastapi import HTTPException , status

class SeatServiceBase(ABC):

    @abstractmethod
    def create_seat(self, db: Session, seat_data: SeatCreate):
        pass

    @abstractmethod
    def get_all_seats(self, db: Session):
        pass

    @abstractmethod
    def delete_seat(self, db: Session, seat_id: UUID):
        pass

    @abstractmethod
    def get_by_id(self, db: Session, seat_id: UUID):
        pass


class SeatService(SeatServiceBase):

    def __init__(self, repo: SeatRepository):
        self.repo = repo

    def get_all_seats(self, db: Session):
        return self.repo.get_all_seat(db)

    def get_by_id(self, db: Session, seat_id: UUID):
        return self.repo.get_by_id(db, seat_id)

    def create_seat(self, db: Session, seat_data: SeatCreate):

        if self.repo.get_seat_by_seat_number(db, seat_data.seat_number):
            raise ValueError("Seat already exists")

        seat = Seat(
            seat_number=seat_data.seat_number,
            is_active=seat_data.is_active,
            floor=seat_data.floor
        )

        return self.repo.create_seat(db, seat)

    def delete_seat(self, db: Session, seat_id: UUID):

        seat = self.repo.get_by_id(db, seat_id)

        if not seat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="seat not found "
            )
        
        if self.repo.seat_has_bookings(db, seat_id):
            raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Seat has active bookings and cannot be deleted"
        )

        self.repo.delete(db, seat)
        return True
    
    def update_seat(self , db : Session , seat_id : UUID , seat_data : dict):
        
        
        seat = self.repo.get_by_id(db , seat_id)
        
        if not seat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=" Seat not found"
            )
        
        if seat_data.seat_number:
            existing = self.repo.get_seat_by_seat_number(db , seat_data.seat_number)
            if existing and existing.id != seat_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="seat Already Exist "
                )
        updated_seat = self.repo.update_seat(
            db,
            seat,
            seat_data.model_dump(exclude_unset=True)
        )
        
        
        return updated_seat
                
    
