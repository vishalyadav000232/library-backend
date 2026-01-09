import uuid
from sqlalchemy import Column, String, Time
from sqlalchemy.dialects.postgresql import UUID
from app.database.db import Base

class Shift(Base):
    __tablename__ = "shifts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String, unique=True, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
