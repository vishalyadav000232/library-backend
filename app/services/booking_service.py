from app.models.booking import Booking
from sqlalchemy.orm import Session
from datetime import datetime
import uuid
from fastapi import HTTPException, status

def is_seat_available(db: Session, seat_id: int, shift_id: int, start_date):
    """
    Check if a seat is available for a given shift and date.
    Returns True if available, False if already booked.
    """
    # Normalize date (remove time if datetime passed)
    start_date = start_date.date() if isinstance(start_date, datetime) else start_date

    existing_booking = (
        db.query(Booking)
        .filter(
            Booking.seat_id == seat_id,
            Booking.shift_id == shift_id,
            Booking.start_date == start_date,
            Booking.status == "ACTIVE"
        )
        .first()
    )

    return existing_booking is None


def create_booking(db: Session, booking_data):
    """
    Create a new booking safely.
    Raises HTTPException if seat is already booked.
    """
    if not is_seat_available(db, booking_data.seat_id, booking_data.shift_id, booking_data.start_date):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Seat already booked for this shift and date."
        )

    new_booking = Booking(
        id=uuid.uuid4(),  # Unique booking ID
        user_id=booking_data.user_id,
        seat_id=booking_data.seat_id,
        shift_id=booking_data.shift_id,
        start_date=booking_data.start_date,
        end_date=booking_data.end_date,
        status="ACTIVE"
    )

    try:
        db.add(new_booking)
        db.commit()
        db.refresh(new_booking)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Booking failed: {str(e)}"
        )

    return new_booking
