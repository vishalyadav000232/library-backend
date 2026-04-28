# app/api/v1/bookings/admin.py

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.database.db import get_db
from app.api.admin.admin_gaurd import admin_required
from app.api.dependency import get_booking_service
from app.services.booking_service import BookingService

router = APIRouter(
    prefix="/admin/bookings",
    tags=["Admin Bookings"]
)

# =====================================================
# GET ALL BOOKINGS (ADMIN)
# =====================================================
@router.get(
    "/",
    status_code=status.HTTP_200_OK
)
def get_all_bookings(
    db: Session = Depends(get_db),
    booking_service: BookingService = Depends(get_booking_service),
    admin=Depends(admin_required)
):
    return booking_service.get_all_bookings(db)


# =====================================================
# BOOKING REPORT (ADMIN ANALYTICS)
# =====================================================
@router.get(
    "/report",
    status_code=status.HTTP_200_OK
)
def booking_report(
    db: Session = Depends(get_db),
    booking_service: BookingService = Depends(get_booking_service),
    admin=Depends(admin_required)
):
    return booking_service.get_booking_report(db)


# =====================================================
# FORCE CANCEL BOOKING (ADMIN CONTROL)
# =====================================================
@router.patch(
    "/{booking_id}/cancel",
    status_code=status.HTTP_200_OK
)
def admin_cancel_booking(
    booking_id: UUID,
    db: Session = Depends(get_db),
    booking_service: BookingService = Depends(get_booking_service),
    admin=Depends(admin_required)
):
    return booking_service.admin_cancel_booking(db, booking_id)