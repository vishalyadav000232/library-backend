from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

# ===============================
# DB
# ===============================
from app.database.db import get_db

# ===============================
# AUTH CORE
# ===============================
from app.auth.provider.token_provider import JWTTokenProvider
from app.auth.deps import get_token_provider, get_user_repository

# ===============================
# USER
# ===============================
from app.services.auth_services import UserServices
from app.repository.user_repository import UserRepository

# ===============================
# BOOKING
# ===============================
from app.repository.booking_repository import BookingRepository
from app.services.booking_service import BookingService

# ===============================
# SEAT
# ===============================
from app.services.seat_services import SeatService
from app.repository.seat_repository import SeatRepository

# ===============================
# REPORT
# ===============================
from app.services.report_service import ReportService
from app.repository.report_repoitory import ReportFactory

# ===============================
# SHIFT
# ===============================
from app.services.shift_services import ShiftService
from app.repository.shift_repository import ShiftRepository

# ===============================
# REFRESH TOKEN
# ===============================
from app.services.refres_token_service import RefreshTokenService
from app.repository.refresh_token_repository import RefreshTokenRepository


# =========================================================
# OAUTH2 SCHEME
# =========================================================
oauth2_bearer = OAuth2PasswordBearer(
    tokenUrl="/api/v1/users/login"
)


# =========================================================
# CURRENT USER DEPENDENCY
# =========================================================
def get_current_user(
    token: str = Depends(oauth2_bearer),
    db: Session = Depends(get_db),
    token_provider: JWTTokenProvider = Depends(get_token_provider),
    user_repo=Depends(get_user_repository)
):
    payload = token_provider.verify_token(token)

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    user = user_repo.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user


# =========================================================
# USER SERVICE
# =========================================================
def get_user_service(
    token_provider: JWTTokenProvider = Depends(get_token_provider)
):
    return UserServices(
        repo=UserRepository(),
        token_provider=token_provider
    )


# =========================================================
# BOOKING SERVICE
# =========================================================
def get_booking_service():
    return BookingService(repo=BookingRepository())


# =========================================================
# SEAT SERVICE
# =========================================================
def get_seat_service():
    return SeatService(repo=SeatRepository())


# =========================================================
# REPORT SERVICE
# =========================================================
def get_report_service() -> ReportService:
    factory = ReportFactory()
    return ReportService(factory=factory)


# =========================================================
# SHIFT SERVICE
# =========================================================
def get_shift_service():
    return ShiftService(repo=ShiftRepository())



def get_refresh_token_service(
    token_provider: JWTTokenProvider = Depends(get_token_provider)
):
    repo = RefreshTokenRepository()
    return RefreshTokenService(
        repo=repo,
        token_provider=token_provider
    )