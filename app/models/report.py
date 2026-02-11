from sqlalchemy import Column, String, Date, Integer, DateTime, func
from app.database.db import Base
import uuid
from sqlalchemy.dialects.postgresql import UUID

class Report(Base):
    __tablename__ = "reports"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    report_type = Column(String(255), nullable=False, index=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    total_records = Column(Integer, default=0)
    total_revenue = Column(Integer, default=0)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
