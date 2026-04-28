# app/api/v1/shifts/admin.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import time

from app.database.db import get_db
from app.api.admin.admin_gaurd import admin_required
from app.api.dependency import get_shift_service
from app.services.shift_services import ShiftService

router = APIRouter(
    prefix="/admin/shifts",
    tags=["Admin Shifts"]
)

# =====================================================
# CREATE SHIFT (ADMIN ONLY)
# =====================================================
@router.post(
    "/",
    status_code=status.HTTP_201_CREATED
)
def create_shift(
    name: str,
    start_time: str,
    end_time: str,
    db: Session = Depends(get_db),
    shift_service: ShiftService = Depends(get_shift_service),
    admin=Depends(admin_required)
):
    try:
        start = time.fromisoformat(start_time)
        end = time.fromisoformat(end_time)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid time format. Use HH:MM"
        )

    shift = shift_service.create_shift(db, name, start, end)

    return {
        "message": "Shift created successfully",
        "shift_id": str(shift["id"])
    }


# =====================================================
# DELETE SHIFT (ADMIN ONLY)
# =====================================================
@router.delete(
    "/{shift_id}",
    status_code=status.HTTP_200_OK
)
def delete_shift(
    shift_id: str,
    db: Session = Depends(get_db),
    shift_service: ShiftService = Depends(get_shift_service),
    admin=Depends(admin_required)
):
    return shift_service.delete_shift(db, shift_id)
