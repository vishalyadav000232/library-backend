import uuid
from sqlalchemy import Column, String, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID
from app.database.db import Base

class Seat(Base):
    __tablename__ = "seats"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    seat_number = Column(String, unique=True, nullable=False, index=True)
    floor = Column(String, nullable=False, default="Ground Floor")   # Ground 
    seat_type = Column(String, nullable=False, default="Standard")   # Standard / 
    price = Column(Integer, nullable=False, default=50)              # price per 
    is_active = Column(Boolean, default=True)
