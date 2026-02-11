from fastapi import APIRouter
from app.api.v1 import users, seats, bookings, payments,shift , report
from app.api.admin import dashboard

api_router = APIRouter()
api_router.include_router(users.router,  tags=["Users"])
api_router.include_router(seats.router, tags=["Seats"])
api_router.include_router(bookings.router,  tags=["Bookings"])
api_router.include_router(payments.router,  tags=["Payments"])
api_router.include_router(shift.router, tags=["Shift"])
api_router.include_router(dashboard.router ,   tags=["Admin Dashboard"])
api_router.include_router(report.router ,   tags=["Reports"])

