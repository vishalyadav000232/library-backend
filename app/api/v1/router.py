from fastapi import APIRouter
from app.api.v1 import users, seats, bookings, payments, shift, report
from app.api.v1.auth import router as auth_router
from app.api.admin import dashboard
from app.api.admin.user import router as admin_user_router


api_router = APIRouter(prefix="/api/v1")

# Public APIs
api_router.include_router(auth_router, prefix="/auth", tags=["Auth"])
# api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(seats.router, prefix="/seats", tags=["Seats"])
api_router.include_router(bookings.router, prefix="/bookings", tags=["Bookings"])
api_router.include_router(payments.router, prefix="/payments", tags=["Payments"])
api_router.include_router(shift.router, prefix="/shifts", tags=["Shift"])
api_router.include_router(report.router, prefix="/reports", tags=["Reports"])

# Admin APIs



api_router.include_router(
    dashboard.router,
    prefix="/admin/dashboard",
    tags=["Admin Dashboard"]
)


api_router.include_router(admin_user_router , prefix="/admin/user"  , tags=["Admin Users"])


