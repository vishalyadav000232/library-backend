from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database.db import get_db
from app.models.seats import Seat as SeatModel 
from app.models.user import User
from app.schemas.seats import SeatResponse   ,SeatCreate
from app.services.seat_services import create_seat
from app.models.booking import Booking

router = APIRouter()

# Example auth dependency
def get_current_user():
    return User(role="admin")  # placeholder

@router.post("/admin/seats", response_model=SeatResponse)
def add_seat(seat: SeatCreate, db: Session = Depends(get_db)):
    try:
        new_seat = create_seat(db, seat)
        return new_seat
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/admin/seats", response_model=List[SeatResponse])
def get_all_seats(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if user.role != "admin":
        raise HTTPException(403, "Not authorized")
    seats = db.query(SeatModel).all()
    return seats


@router.get("/admin/bookings")
def get_bookings(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if not user.role == "admin":
        raise HTTPException(403, "Not authorized")
    return db.query(Booking).all()
