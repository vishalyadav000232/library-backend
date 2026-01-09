from app.models.booking import Booking
from sqlalchemy.orm import Session



def is_seat_available(db:Session , seat_id: int, shift_id: int, start_date):
    exist = db.query(Booking).filter(
        Booking.seat_id == seat_id,
        Booking.shift_id ==shift_id,
        Booking.start_date == start_date,
        Booking.status == "ACTIVE"

    ).first()
    return exist is None


def create_booking(db: Session, booking_data):
    if not is_seat_available(db, booking_data.seat_id, booking_data.shift_id, booking_data.start_date):
        raise Exception("Seat already booked for this shift and date")
    
    new_booking = Booking(
        user_id=booking_data.user_id,
        seat_id=booking_data.seat_id,
        shift_id=booking_data.shift_id,
        start_date=booking_data.start_date,
        end_date=booking_data.end_date
    )
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)
    return new_booking