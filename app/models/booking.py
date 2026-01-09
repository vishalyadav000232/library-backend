# SQLAlchemy Booking model placeholder

import uuid
from sqlalchemy import Column , String  , Date  , ForeignKey ,Integer ,Boolean , UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from app.database.db import Base

class Booking(Base):
    __tablename__ = "bookings"
    __table_args__ = (UniqueConstraint('seat_id', 'shift_id', 'start_date', name='unique_seat_shift_date'),)
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID ,ForeignKey("users.id"))
    seat_id = Column(Integer, ForeignKey("seats.id"))
    shift_id = Column(Integer, ForeignKey("shifts.id"))
    start_date = Column(Date)
    end_date = Column(Date)
    is_active = Column(Boolean, default=True)
    status = Column(String, default="ACTIVE")