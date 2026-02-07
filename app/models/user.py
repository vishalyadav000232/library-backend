import uuid
from sqlalchemy import Column, String, Boolean, DateTime
from datetime import datetime
from app.database.db import Base
from sqlalchemy.dialects.postgresql import UUID
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def truncate_password(password :str):
     return password.encode("utf-8")[:72].decode("utf-8", "ignore")

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), default="STUDENT")
    is_active = Column(Boolean, default=True)
    create_at = Column(DateTime, default=datetime.utcnow)

    
    def set_password(self, password: str):
        truncate = truncate_password(password)
        self.hashed_password = pwd_context.hash(truncate)

    
    def verify_password(self, password: str) -> bool:
        truncate = truncate_password(password)
        return pwd_context.verify(truncate, self.hashed_password)
    def hello(self):
        return "hello world"