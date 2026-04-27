from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional, List


class UserDTO(BaseModel):
    id: UUID
    name: str
    email: str
    role: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {
        "from_attributes": True
    }


class PaginatedUsersDTO(BaseModel):
    items: List[UserDTO]
    total: int
    page: int
    size: int
    pages: int