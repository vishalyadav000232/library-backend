# app/api/v1/bookings/public.py

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.database.db import get_db
from app.schemas.booking import BookingCreate, BookingResponse
from app.models.user import User
from app.api.dependency import get_current_user, get_booking_service
from app.services.booking_service import BookingService

router = APIRouter(
 
)

# =====================================================
# CREATE BOOKING (USER)
# =====================================================
@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=BookingResponse
)
async def book_seat(
    booking: BookingCreate,
    db: Session = Depends(get_db),
    booking_service: BookingService = Depends(get_booking_service),
    current_user: User = Depends(get_current_user)
):
    return await booking_service.create_booking(db, booking, current_user.id)


# =====================================================
# MY BOOKINGS (USER ONLY)
# =====================================================
@router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    response_model=list[BookingResponse]
)
def my_bookings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    booking_service: BookingService = Depends(get_booking_service)
):
    return booking_service.my_bookings(db, current_user.id)


# =====================================================
# GET SINGLE BOOKING (USER - OWN ONLY)
# =====================================================
@router.get(
    "/{booking_id}",
    status_code=status.HTTP_200_OK,
    response_model=BookingResponse
)
def get_booking_by_id(
    booking_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    booking_service: BookingService = Depends(get_booking_service)
):
    return booking_service.get_booking_for_user(db, booking_id, current_user.id)


# =====================================================
# CANCEL BOOKING (USER - OWN ONLY)
# =====================================================
@router.patch(
    "/{booking_id}/cancel",
    status_code=status.HTTP_200_OK
)
def cancel_booking(
    booking_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    booking_service: BookingService = Depends(get_booking_service)
):
    return booking_service.cancel_booking_user(db, booking_id, current_user.id)