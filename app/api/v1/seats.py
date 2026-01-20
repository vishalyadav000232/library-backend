# app/api/v1/seats.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.schemas.seats import SeatCreate, SeatResponse
from app.services.seat_services import create_seat
from app.database.db import get_db
from app.models.seats import Seat   # ✅ IMPORT MODEL

router = APIRouter(
    prefix="/seats",
    tags=["Seats"]
)

# -----------------------------
# CREATE SEAT (ADMIN)
# -----------------------------
@router.post(
    "/",
    response_model=SeatResponse,
    status_code=status.HTTP_201_CREATED
)
def add_seat(seat: SeatCreate, db: Session = Depends(get_db)):
    try:
        new_seat = create_seat(db, seat)
        return new_seat
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

# -----------------------------
# GET ALL SEATS
# -----------------------------
@router.get(
    "/",
    response_model=List[SeatResponse],
    status_code=status.HTTP_200_OK
)
def get_seats(db: Session = Depends(get_db)):
    seats = db.query(Seat).all()
    return seats
