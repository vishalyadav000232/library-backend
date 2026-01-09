from pydantic import BaseModel, Field
from uuid import UUID
from datetime import date

class BookingCreate(BaseModel):
    user_id: UUID = Field(..., example="550e8400-e29b-41d4-a716-446655440000")
    seat_id: int = Field(..., example=1)
    shift_id: int = Field(..., example=1)
    start_date: date = Field(..., example="2026-01-09")
    end_date: date = Field(..., example="2026-01-09")


class BookingResponse(BaseModel):
    id: UUID
    user_id: UUID
    seat_id: int
    shift_id: int
    start_date: date
    end_date: date
    status: str
