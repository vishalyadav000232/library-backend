# SQLAlchemy Payment model placeholder

import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column , Integer , String ,ForeignKey  
from app.database.db import Base


class Payment(Base):
    __tablename__= "payment"
    id = Column(UUID(as_uuid=True ), primary_key=True  , default=uuid.uuid4)
    booking_id = Column(UUID , ForeignKey("bookings.id"))
    amount  = Column( Integer )
    status = Column(String , default="PENDING")
    provider = Column(String)
    transaction_id = Column(String)