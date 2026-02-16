import uuid
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from app.database.db import Base
from datetime import datetime


class Payment(Base):
    __tablename__ = "payments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    booking_id = Column(
        UUID(as_uuid=True),
        ForeignKey("bookings.id"),
        nullable=False
    )
    amount = Column(Integer, nullable=False)
    currency = Column(String, default="INR")
    status = Column(String, default="CREATED")
    provider = Column(String, default="razorpay")
    provider_order_id = Column(String, nullable=False)  
    provider_payment_id = Column(String, nullable=True)
    provider_signature = Column(String, nullable=True)
    payment_method = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
