from sqlalchemy import Column , DateTime , String , Boolean , ForeignKey 
from uuid import   uuid4
from datetime import datetime
from app.database.db import Base
from sqlalchemy.dialects.postgresql import UUID


class RefreshToken(Base):
    
    __tablename__ = "refresh_tokens"

    id = Column(UUID, primary_key=True, default=uuid4)
    user_id = Column(UUID, ForeignKey("users.id"))
    token_hash = Column(String, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    revoked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)