import uuid
from sqlalchemy import Column, String, Boolean, DateTime
from datetime import datetime
from app.database.db import Base
from sqlalchemy.dialects.postgresql import UUID
from passlib.context import CryptContext
from passlib.hash import bcrypt
from passlib.context import CryptContext
#  For the User Model

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="STUDENT")
    is_active = Column(Boolean, default=True)
    create_at = Column(DateTime, default=datetime.utcnow)

    def veryfy_password(self, password: str):
        return bcrypt.verify(password, self.hashed_password)

    def set_password(self, password: str):
        self.hashed_password = bcrypt.hash(password)
        

    # def hash_password(password: str) -> str:
    #     # truncate to max 72 bytes safely
    #     truncated = password.encode("utf-8")[:72].decode("utf-8", "ignore")
    #     return pwd_context.hash(truncated)

    # def verify_password(plain_password: str, hashed_password: str) -> bool:
    #     truncated = plain_password.encode(
    #         "utf-8")[:72].decode("utf-8", "ignore")
    #     return pwd_context.verify(truncated, hashed_password)
