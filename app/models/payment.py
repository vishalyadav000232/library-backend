import uuid
import enum
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from app.database.db import Base


class PaymentStatus(enum.Enum):
    CREATED = "CREATED"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class Payment(Base):
    __tablename__ = "payments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    booking_id = Column(UUID(as_uuid=True), ForeignKey("bookings.id"), nullable=False)

    amount = Column(Integer, nullable=False)  # in paisa
    currency = Column(String, default="INR")

    status = Column(Enum(PaymentStatus), default=PaymentStatus.CREATED , index=True)

    provider = Column(String, default="razorpay")
    provider_order_id = Column(String, nullable=False)
    provider_payment_id = Column(String, unique=True, nullable=True)
    provider_signature = Column(String, nullable=True)

    payment_method = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)