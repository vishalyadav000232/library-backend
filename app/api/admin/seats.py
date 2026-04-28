# app/api/v1/seats/admin.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.database.db import get_db
from app.schemas.seats import SeatCreate, SeatResponse, SeatUpdate
from app.api.admin.admin_gaurd import admin_required
from app.api.dependency import get_seat_service
from app.services.seat_services import SeatService

router = APIRouter(
    prefix="/admin/seats",
    tags=["Admin Seats"]
)

# =====================================================
# CREATE SEAT (ADMIN ONLY)
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
# UPDATE SEAT (ADMIN ONLY)
# =====================================================
@router.patch(
    "/{seat_id}",
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
    return seat_service.update_seat(db, seat_id, update_data)


# =====================================================
# DELETE SEAT (ADMIN ONLY)
# =====================================================
@router.delete(
    "/{seat_id}",
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
        "deleted": deleted
    }


# =====================================================
# SEAT STATS (ADMIN ONLY)
# =====================================================
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