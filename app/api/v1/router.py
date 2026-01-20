from fastapi import APIRouter
from app.api.v1 import users, seats, bookings, payments,shift
from app.api.v1.admin import admin_routes

api_router = APIRouter()
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(seats.router, prefix="/seats", tags=["Seats"])
api_router.include_router(bookings.router, prefix="/bookings", tags=["Bookings"])
api_router.include_router(payments.router, prefix="/payments", tags=["Payments"])
api_router.include_router(shift.router, prefix="/payments", tags=["Shift"])
api_router.include_router(admin_routes.router, prefix="/payments", tags=["Admin"])

