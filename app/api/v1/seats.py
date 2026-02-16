# app/api/v1/seats.py

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.database.db import get_db
from app.schemas.seats import SeatCreate, SeatResponse, SeatUpdate
from app.api.admin.admin_gaurd import admin_required
from app.api.dependency import get_seat_service
from app.services.seat_services import SeatService

router = APIRouter(
    prefix="/seats",
    tags=["Seats"]
)

# =====================================================
# CREATE SEAT
# =====================================================

@router.post(
    "/",
    response_model=SeatResponse,
    status_code=status.HTTP_201_CREATED
)
def create_seat(
    seat: SeatCreate,
    db: Session = Depends(get_db),
    seat_service: SeatService = Depends(get_seat_service),
    admin=Depends(admin_required)
):
    try:
        return seat_service.create_seat(db, seat)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# =====================================================
# GET ALL SEATS (WITH PAGINATION)
# =====================================================

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
    seat = seat_service.get_by_id(db, seat_id)

    if not seat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Seat not found"
        )

    return seat



@router.patch(
    "/{seat_id}/update",
    response_model=SeatResponse,
    status_code=status.HTTP_200_OK
)
def update_seat(
    seat_id: UUID,
    update_data: SeatUpdate,
    db: Session = Depends(get_db),
    seat_service: SeatService = Depends(get_seat_service),
    admin=Depends(admin_required)
):
    updated_seat = seat_service.update_seat(db, seat_id, update_data)

    return updated_seat



@router.delete(
    "/{seat_id}/delete",
    status_code=status.HTTP_200_OK
)
def delete_seat(
    seat_id: UUID,
    db: Session = Depends(get_db),
    seat_service: SeatService = Depends(get_seat_service),
    admin=Depends(admin_required)
):
    
    deleted = seat_service.delete_seat(db, seat_id)

    

    return {
  "message": "Seat deleted successfully",
  "deleted" : deleted
}




@router.get(
    "/stats/summary",
    status_code=status.HTTP_200_OK
)
def seat_stats(
    db: Session = Depends(get_db),
    seat_service: SeatService = Depends(get_seat_service),
    admin=Depends(admin_required)
):
    return seat_service.get_seat_stats(db)
