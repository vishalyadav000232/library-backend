from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi import status
from uuid import UUID
from app.schemas.booking import BookingCreate, BookingResponse

from app.database.db import get_db
from app.models.booking import Booking
from app.models.user import User
from app.api.dependency import get_current_user, get_booking_service



from app.models.booking import Booking
from app.models.user import User
from app.models.seats import Seat
from  app.models.payment import Payment

from app.services.booking_service import BookingService
router = APIRouter(prefix="/bookings", tags=["Bookings"])



@router.get("/all")
def get_all_booking_data(
    db: Session = Depends(get_db),
    booking_service: BookingService = Depends(get_booking_service)
    ):
    return booking_service.get_booking_report(db)


    


# ✅ 1) Create booking
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=BookingResponse)
def book_seat(booking: BookingCreate, db: Session = Depends(get_db), booking_service: BookingService = Depends(get_booking_service)):
    return booking_service.create_booking(db, booking)


# ✅ 2) Get all bookings (admin usage mostly)

@router.get("/", status_code=status.HTTP_200_OK, response_model=list[BookingResponse])
def get_all_booking(
        booking_service: BookingService = Depends(get_booking_service),
        db: Session = Depends(get_db)):
    return booking_service.get_all_bookings(db)


# ✅ 3) Get booking by ID
@router.get("/{booking_id}", status_code=status.HTTP_200_OK, response_model=BookingResponse)
def get_booking_by_id(
        booking_id: UUID, db: Session = Depends(get_db),
        booking_service: BookingService = Depends(get_booking_service)):
    return booking_service.get_booking_by_id(db , booking_id)
    


# ✅ 4) Cancel booking
@router.patch("/{booking_id}/cancel", status_code=status.HTTP_200_OK)
def cancel_booking(booking_id: UUID, db: Session = Depends(get_db),
                   booking_service: BookingService = Depends(
                       get_booking_service)
                   ):
    return booking_service.cancel_booking(db, booking_id)


@router.get(
    "/me/my-bookings",
    status_code=status.HTTP_200_OK,
    response_model=list[BookingResponse]
)
def my_bookings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    booking_service: BookingService = Depends(get_booking_service)
):
    return booking_service.my_bookings(db, current_user.id)


