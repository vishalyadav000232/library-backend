from pydantic import BaseModel, EmailStr, Field
from uuid import UUID
from datetime import datetime
from typing import Optional

# CREATE USER SCHEMA (PYDANTIC SCHEEMA)


class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password : str
    

class UserResponse(BaseModel):
    id: UUID
    name: str
    email: EmailStr
    hashed_password:str
    role : str
    is_active: bool
    create_at: datetime

    class Config:
        from_attributes = True

# LOGIN USER SCHEMA (PYDANTIC SHCEMA)

class LoginUser(BaseModel):
    email : EmailStr
    password : str


class LoginResponse(BaseModel):
    id: UUID
    name: str
    email: EmailStr
    role : str
    is_active: bool
    create_at: datetime

    class Config:
        from_attributes = True