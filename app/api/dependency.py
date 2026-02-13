from app.repository.booking_repository import BookingRepository
from app.services.booking_service import BookingService
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session


from app.services.auth_services import UserServices
from app.repository.user_repository import UserRepository
from app.auth.provider.token_provider import JWTTokenProvider
from app.services.seat_services import SeatSearvice
from app.repository.seat_repository import SeatRepository
from app.services.report_service import ReportService
from app.repository.report_repoitory import   ReportFactory
from app.services.shift_services import ShiftService
from app.repository.shift_repository import ShiftRepository
from app.database.db import get_db
from app.auth.deps import (
    get_token_provider,
    get_user_repository
)

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/api/v1/users/login")


def get_current_user(
    token: str = Depends(oauth2_bearer),
    db: Session = Depends(get_db),
    token_provider=Depends(get_token_provider),
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


def get_user_service():
    return UserServices(
        repo=UserRepository(),
        token_provider=JWTTokenProvider()
    )


def get_booking_service():
    return BookingService(repo=BookingRepository())


def get_seat_service():
    return SeatSearvice(repo=SeatRepository())


def get_report_service() -> ReportService:
    factory = ReportFactory()  
    return ReportService(factory=factory)


def get_shift_service():
    return ShiftService(repo=ShiftRepository())