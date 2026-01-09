# app/api/v1/seats.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.seats import SeatCreate, SeatResponse
from app.services.seat_services import create_seat
from app.database.db import get_db

router = APIRouter(
    prefix="/seats",
    tags=["Seats"]
)

@router.post("/", response_model=SeatResponse)
def add_seat(seat: SeatCreate, db: Session = Depends(get_db)):
    try:
        new_seat = create_seat(db, seat)
        return new_seat
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
