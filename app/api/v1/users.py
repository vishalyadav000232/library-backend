from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from uuid import UUID
from app.api.dependency import get_current_user, get_user_service
from app.database.db import get_db
from app.models.user import User
from app.schemas.user import (
    UserCreate,
    UserResponse,
    LoginUser,
    TokenResponse,
    ProfileResponse
)
from app.services.auth_services import UserServices
from app.repository.user_repository import UserRepository
from app.auth.provider.token_provider import JWTTokenProvider
from app.api.admin.admin_gaurd import admin_required


router = APIRouter(prefix="/users", tags=["Users"])

oauth2_bearer = OAuth2PasswordBearer(
    tokenUrl="/api/v1/users/login"
)

# -------------------------------------------------------------------
# ROUTES
# -------------------------------------------------------------------


@router.post(
    "/signup",
    status_code=status.HTTP_201_CREATED,
    response_model=UserResponse
)
def signup(
    user: UserCreate,
    db: Session = Depends(get_db),
    user_service: UserServices = Depends(get_user_service)
):
    return user_service.create_user(db, user)


@router.post(
    "/user-login",
    status_code=status.HTTP_200_OK,
    response_model=TokenResponse
)
def login(
    user_data: LoginUser,
    db: Session = Depends(get_db),
    user_service: UserServices = Depends(get_user_service)
):
    return user_service.login_user(db, user_data)


@router.post("/login", response_model=TokenResponse)
def login_oauth(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db), user_service: UserServices = Depends(get_user_service)):
    user_data = LoginUser(
        email=form_data.username,
        password=form_data.password
    )
    return user_service.login_user(db, user_data)


@router.get("/me", status_code=status.HTTP_200_OK, response_model=ProfileResponse)
def get_profile(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/", status_code=status.HTTP_200_OK)
def get_users(db: Session = Depends(get_db), admin=Depends(admin_required)):
    return UserRepository().get_all_users(db)


@router.delete("/{user_id}/delete", status_code=status.HTTP_200_OK, response_model=UserResponse)
def delete_user(user_id: UUID, db: Session = Depends(get_db), admin=Depends(admin_required),
                user_service: UserServices = Depends(get_user_service)):
    return user_service.delete_user(db, user_id)
