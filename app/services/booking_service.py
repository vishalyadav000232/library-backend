from app.models.booking import Booking
from sqlalchemy.orm import Session
from datetime import datetime, date
import uuid
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError


def normalize_date(d):
    return d.date() if isinstance(d, datetime) else d


def is_seat_available(db: Session, seat_id: int, shift_id: int, start_date):
    start_date = normalize_date(start_date)

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


    start_date = normalize_date(booking_data.start_date)
    end_date = normalize_date(booking_data.end_date)

    if end_date < start_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="end_date cannot be less than start_date"
        )

    # 2) Check seat availability
    if not is_seat_available(db, booking_data.seat_id, booking_data.shift_id, start_date):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Seat already booked for this shift and date."
        )

    new_booking = Booking(
        id=uuid.uuid4(),
        user_id=booking_data.user_id,
        seat_id=booking_data.seat_id,
        shift_id=booking_data.shift_id,
        start_date=start_date,
        end_date=end_date,
        status="ACTIVE"
    )

    try:
        db.add(new_booking)
        db.commit()
        db.refresh(new_booking)

    except IntegrityError:
        db.rollback()
        # This catches DB unique constraint error (race condition safe)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Seat already booked (conflict). Try another seat."
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Booking failed: {str(e)}"
        )

    return new_booking
