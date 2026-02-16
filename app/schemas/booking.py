from pydantic import BaseModel, Field , field_validator
from uuid import UUID
from datetime import date
from typing import Optional
from datetime import time


class BookingCreate(BaseModel):
    user_id: UUID = Field(..., example="550e8400-e29b-41d4-a716-446655440000")
    seat_id: UUID = Field(..., example=1)
    shift_id: UUID = Field(..., example=1)
    start_date: date = Field(..., example="2026-01-09")
    end_date: date = Field(..., example="2026-01-09")







class BookingResponse(BaseModel):
    id: UUID
    user_id: UUID
    seat_id: UUID
    shift_id: UUID
    start_date: date
    end_date: date
    status: str



class UserInfo(BaseModel):
    id: UUID
    name: str
    email: str


class SeatInfo(BaseModel):
    seat_number: str
    floor: str
    amount: float


class PaymentInfo(BaseModel):
    amount: Optional[float]
    status: str
 
class ShiftInfo(BaseModel):
    name: str
    start_time: time
    end_time: time

class BookingReport(BaseModel):
    booking_id: UUID
    booking_date: date
    status : str
    user: UserInfo
    seat: SeatInfo
    shift: ShiftInfo
    payment: PaymentInfo


