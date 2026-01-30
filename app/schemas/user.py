from pydantic import BaseModel, EmailStr, Field ,ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional

# CREATE USER SCHEMA (PYDANTIC SCHEEMA)


class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password : str
    role: Optional[str] = "STUDENT"
    

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
       model_config = ConfigDict(from_attributes=True)
    
class TokenResponse(BaseModel):
    message: str
    access_token: str
    role : str
    token_type: str


class ProfileResponse(BaseModel):
    id:UUID
    name : str
    email: str
    role :str