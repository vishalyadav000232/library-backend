from pydantic import BaseModel
from uuid import UUID


class ShiftCreate(BaseModel):
    name: str
    start_time: str  # ISO time string
    end_time: str

class ShiftResponse(BaseModel):
    id: UUID
    name: str
    start_time: str
    end_time: str

    class Config:
        orm_mode = True