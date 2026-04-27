from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date
import json
from app.api.admin.admin_gaurd import admin_required
from app.database.db import get_db

from app.models.user import User
from app.models.seats import Seat
from app.models.payment import Payment
from app.models.booking import Booking
from app.redis.client import redis_client , CACHE_TTL


router = APIRouter(tags=["Admin Dashboard"])

CACHE_KEY = "admin_dashboard_v1"

@router.get("/dashboard")
def admin_dashboard(db: Session = Depends(get_db), admin=Depends(admin_required)):


    cached_data = redis_client.get(CACHE_KEY)
    if cached_data:
        return json.loads(cached_data)

    
    total_users = db.query(User.id).count()
    active_users = db.query(User.id).filter(User.is_active == True).count()

    total_bookings = db.query(Booking.id).count()

    active_bookings = db.query(Booking.id).filter(
        Booking.status == "CONFIRMED"
    ).count()

    total_seats = db.query(Seat.id).count()

    occupied_seats = db.query(Booking.id).filter(
        Booking.status == "CONFIRMED"
    ).count()

    total_revenue = db.query(func.sum(Payment.amount)).filter(
        Payment.status == "SUCCESS"
    ).scalar() or 0

    
    response = {
        "users": {
            "total": total_users,
            "active": active_users
        },
        "bookings": {
            "total": total_bookings,
            "active": active_bookings
        },
        "seats": {
            "total": total_seats,
            "occupied": occupied_seats,
            "available": total_seats - occupied_seats
        },
        "payments": {
            "revenue": float(total_revenue)
        }
    }

    
    redis_client.setex(
        CACHE_KEY,
        CACHE_TTL,
        json.dumps(response)
    )

    return response