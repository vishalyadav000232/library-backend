from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.schemas.user import (
    UserCreate,
    UserResponse,
    LoginUser,
    LoginResponse
)
from app.services.user_services import create_user, login_user

router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "/signup",
    status_code=status.HTTP_201_CREATED,
    response_model=UserResponse
)
def signup(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    return create_user(db, user)


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    response_model=LoginResponse
)
def login(
    user_data: LoginUser,
    db: Session = Depends(get_db)
):
    try:
        return login_user(db, user_data)

    except HTTPException as e:
        raise e

    except Exception:

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong during login"
        )
