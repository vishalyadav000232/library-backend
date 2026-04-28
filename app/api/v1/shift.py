# app/api/v1/shifts/public.py

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.api.dependency import get_shift_service
from app.services.shift_services import ShiftService

router = APIRouter(
   
)

@router.get(
    "/",
    status_code=status.HTTP_200_OK
)
def get_all_shifts(
    db: Session = Depends(get_db),
    shift_service: ShiftService = Depends(get_shift_service)
):
    return shift_service.get_all_shift(db)