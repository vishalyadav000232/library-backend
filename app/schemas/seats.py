
from pydantic import BaseModel
from uuid import UUID

class SeatCreate(BaseModel):
    seat_number: str
    is_active: bool = True

class SeatResponse(BaseModel):
    id: UUID
    seat_number: str
    is_active: bool
