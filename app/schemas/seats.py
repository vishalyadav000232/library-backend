
from pydantic import BaseModel ,ConfigDict 
from uuid import UUID
from typing import Optional
class SeatCreate(BaseModel):
    seat_number: str
    is_active: Optional[bool ]  = True

class SeatResponse(BaseModel):
    id: UUID
    seat_number: str
    is_active: bool

    class Config:
        model_config = ConfigDict(from_attributes=True)


class SeatUpdate(BaseModel):
    seat_number: Optional[str] = None
    is_active: Optional[bool] = None
