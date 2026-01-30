# app/services/seat_services.py
from sqlalchemy.orm import Session
from app.models.seats import Seat
from app.schemas.seats import SeatCreate  

def create_seat(db: Session, seat_data: SeatCreate):
    
    
    existing = db.query(Seat).filter(Seat.seat_number == seat_data.seat_number).first()
    if existing:
        raise ValueError("Seat already exists")

    seat = Seat(
        seat_number=seat_data.seat_number,
        is_active=seat_data.is_active  # default True from schema
    )
    db.add(seat)
    db.commit()
    db.refresh(seat)
    return seat



