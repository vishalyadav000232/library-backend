from pydantic import BaseModel
from datetime import time
from uuid import UUID


class ShiftCreate(BaseModel):
    name: str
    start_time: time
    end_time: time


class ShiftResponse(BaseModel):
    id: UUID
    name: str
    start_time: time
    end_time: time

    class Config:
        from_attributes = True