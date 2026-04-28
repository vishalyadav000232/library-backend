# app/api/v1/seats/public.py

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.database.db import get_db
from app.schemas.seats import SeatResponse
from app.api.dependency import get_seat_service
from app.services.seat_services import SeatService

router = APIRouter()


@router.get(
    "/",
    response_model=List[SeatResponse],
    status_code=status.HTTP_200_OK
)
def get_all_seats(
    db: Session = Depends(get_db),
    seat_service: SeatService = Depends(get_seat_service)
):
    return seat_service.get_all_seats(db)



@router.get(
    "/{seat_id}",
    response_model=SeatResponse,
    status_code=status.HTTP_200_OK
)
def get_seat_by_id(
    seat_id: UUID,
    db: Session = Depends(get_db),
    seat_service: SeatService = Depends(get_seat_service)
):
    return seat_service.get_by_id(db, seat_id)