
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.booking import BookingCreate, BookingResponse
from app.services.booking_service import create_booking
from app.database.db import get_db
from fastapi import status


router = APIRouter()


@router.post("/", status_code=status.HTTP_200_OK , response_model=BookingResponse)
def book_seat(booking: BookingCreate, db: Session = Depends(get_db)):
    try:
        new_booking = create_booking(db, booking)
        return new_booking
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
