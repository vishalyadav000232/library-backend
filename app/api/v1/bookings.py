from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi import status
from uuid import UUID
from app.schemas.booking import BookingCreate, BookingResponse
from app.services.booking_service import create_booking 
from app.database.db import get_db
from app.models.booking import Booking
from app.models.user import User
from app.services.user_services import get_current_user

router = APIRouter(prefix="/bookings", tags=["Bookings"])


# ✅ 1) Create booking
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=BookingResponse)
def book_seat(booking: BookingCreate, db: Session = Depends(get_db)):
    return create_booking(db, booking)


# ✅ 2) Get all bookings (admin usage mostly)
@router.get("/", status_code=status.HTTP_200_OK, response_model=list[BookingResponse])
def get_all_booking(db: Session = Depends(get_db)):
    return db.query(Booking).all()


# ✅ 3) Get booking by ID
@router.get("/{booking_id}", status_code=status.HTTP_200_OK, response_model=BookingResponse)
def get_booking_by_id(booking_id: UUID, db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking


# ✅ 4) Cancel booking
@router.patch("/{booking_id}/cancel", status_code=status.HTTP_200_OK)
def cancel_booking(booking_id: UUID, db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()

    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    if booking.status != "ACTIVE":
        raise HTTPException(status_code=400, detail="Only ACTIVE booking can be cancelled")

    booking.status = "CANCELLED"
    db.commit()
    db.refresh(booking)

    return {"message": "Booking cancelled successfully", "booking_id": booking.id}


@router.get(
    "/me/my-bookings",
    status_code=status.HTTP_200_OK,
    response_model=list[BookingResponse]
)
def my_bookings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return (
        db.query(Booking)
        .filter(Booking.user_id == current_user.id)
        .all()
    )
