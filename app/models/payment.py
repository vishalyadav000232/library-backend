import uuid
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.database.db import Base


class Payment(Base):
    __tablename__ = "payments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    booking_id = Column(
        UUID(as_uuid=True),
        ForeignKey("bookings.id"),
        nullable=False
    )

    amount = Column(Integer, nullable=False)  

    status = Column(
        String,
        default="CREATED"
    )

    provider = Column(String, default="razorpay")

    provider_payment_id = Column(String, nullable=True)
