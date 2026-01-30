from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.admin.admin_gaurd import admin_required
from app.database.db import get_db

from app.models.user import User
from app.models.seats import Seat
from app.models.payment import Payment
from app.models.booking import Booking


router = APIRouter(
    prefix="/admin",
    tags=["Admin Dashboard "]
)


@router.get("/dashboard")
def admin_dashboard(
    db: Session = Depends(get_db),
    admin=Depends(admin_required)
):
    total_users = db.query(User).count()

    active_users = db.query(User).filter(
        User.is_active == True
    ).count()

    total_bookings = db.query(Booking).count()

    total_seats = db.query(Seat).count()

    occupied_seats = db.query(Seat).filter(
        Seat.is_active.isnot(None)
    ).count()

    verified_payments = db.query(Payment).filter(
        Payment.status == "verified"
    ).count()

    return {
        "total_users": total_users,
        "active_users": active_users,
        "total_bookings": total_bookings,
        "total_seats": total_seats,
        "occupied_seats": occupied_seats,
        "available_seats": total_seats - occupied_seats,
        "verified_payments": verified_payments
    }
