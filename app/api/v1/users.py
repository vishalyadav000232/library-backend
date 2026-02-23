from fastapi import APIRouter, status, Depends, HTTPException, Response, Request
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from uuid import UUID
from fastapi.responses import JSONResponse

from app.auth.deps import get_token_provider
from app.api.dependency import (
    get_current_user,
    get_user_service,
    get_refresh_token_service
)
from app.database.db import get_db
from app.models.user import User
from app.schemas.user import (
    UserCreate,
    UserResponse,
    LoginUser,
    ProfileResponse
)
from app.services.auth_services import UserServices
from app.repository.user_repository import UserRepository
from app.api.admin.admin_gaurd import admin_required
from app.services.refres_token_service import RefreshTokenService
from app.auth.provider.token_provider import TokenProvider

router = APIRouter(prefix="/users", tags=["Users"])
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/api/v1/users/login")

# =====================================================
# SIGNUP
# =====================================================
@router.post("/signup", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
def signup(
    user: UserCreate,
    db: Session = Depends(get_db),
    user_service: UserServices = Depends(get_user_service)
):
    return user_service.create_user(db, user)


# =====================================================
# LOGIN (JSON BODY)
# =====================================================
@router.post("/user-login", status_code=status.HTTP_200_OK)
def login(
    user_data: LoginUser,
    db: Session = Depends(get_db),
    user_service: UserServices = Depends(get_user_service),
    refresh_service: RefreshTokenService = Depends(get_refresh_token_service),
    token_provider: TokenProvider = Depends(get_token_provider)
):
    user = user_service.login_user(db, user_data)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = token_provider.create_access_token(user.id, user.role)
    refresh_token = refresh_service.create_and_store(db, user)

    content = {"access_token": access_token, "token_type": "bearer"}
    response = JSONResponse(content=content)

    # ✅ Swagger UI testing only: httponly=False
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
            secure=True,
            samesite="none",
        max_age=60*60*24*7
    )
    return response


# =====================================================
# LOGIN (OAuth2 FORM)
# =====================================================
@router.post("/login")
def login_oauth(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
    user_service: UserServices = Depends(get_user_service),
    refresh_service: RefreshTokenService = Depends(get_refresh_token_service),
    token_provider: TokenProvider = Depends(get_token_provider)
):
    user_data = LoginUser(email=form_data.username, password=form_data.password)
    user = user_service.login_user(db, user_data)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = token_provider.create_access_token(user.id, user.role)
    refresh_token = refresh_service.create_and_store(db, user)

    content = {"access_token": access_token, "token_type": "bearer", "role": user.role}
    response = JSONResponse(content=content)

    response.set_cookie(
    key="refresh_token",
    value=refresh_token,
    httponly=True,
    secure=False,        # <-- change to False for local dev
    samesite="lax",      # <-- Lax works for cross-origin in local dev
    max_age=60*60*24*7
)
    return response


# =====================================================
# CURRENT USER PROFILE
# =====================================================
@router.get("/me", response_model=ProfileResponse)
def get_profile(current_user: User = Depends(get_current_user)):
    return current_user


# =====================================================
# ADMIN GET USERS
# =====================================================
@router.get("/")
def get_users(db: Session = Depends(get_db), admin=Depends(admin_required)):
    return UserRepository().get_all_users(db)


# =====================================================
# ADMIN DELETE USER
# =====================================================
@router.delete("/{user_id}/delete", response_model=UserResponse)
def delete_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    admin=Depends(admin_required),
    user_service: UserServices = Depends(get_user_service)
):
    return user_service.delete_user(db, user_id)


# =====================================================
# REFRESH TOKEN (ROTATION + DB VALIDATION)
# =====================================================
@router.post("/refresh")
def refresh_token(
    request: Request,
    db: Session = Depends(get_db),
    refresh_service: RefreshTokenService = Depends(get_refresh_token_service),
    token_provider: TokenProvider = Depends(get_token_provider),
    user_service: UserServices = Depends(get_user_service)
):
    refresh_token_cookie = request.cookies.get("refresh_token")

    if not refresh_token_cookie:
        raise HTTPException(status_code=401, detail="Refresh token missing")

    payload = token_provider.verify_refresh_token(refresh_token_cookie)
    user_id = UUID(payload["sub"])

    user = user_service.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    access_token, new_refresh_token = refresh_service.rotate(
        db, refresh_token_cookie, user
    )

    response = JSONResponse({
        "access_token": access_token,
        "token_type": "bearer"
    })

    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60*60*24*7,
        path="/"
    )

    return response

# =====================================================
# LOGOUT (REVOKE TOKEN FROM DB)
# =====================================================
@router.post("/logout")
def logout(
    request: Request,
    db: Session = Depends(get_db),
    refresh_service: RefreshTokenService = Depends(get_refresh_token_service)
):
    refresh_token = request.cookies.get("refresh_token")
    if refresh_token:
        refresh_service.logout(db, refresh_token)

    response = JSONResponse(content={"message": "Logged out successfully"})
    response.delete_cookie("refresh_token")
    return response