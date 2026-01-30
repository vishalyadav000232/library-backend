from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.admin.admin_gaurd import admin_required
from app.database.db import get_db
from app.models.user import User
from fastapi.security import OAuth2PasswordRequestForm
from app.schemas.user import (
    UserCreate,
    UserResponse,
    LoginUser,
    TokenResponse,
    ProfileResponse
)
from app.services.user_services import (
    create_user,
    login_user,
    get_current_user
)
from app.api.admin.admin_gaurd import admin_required
from uuid import UUID

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/signup", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    return create_user(db, user)


@router.post("/user-login",status_code=status.HTTP_200_OK,response_model=TokenResponse)
def login(
    user_data: LoginUser,
    db: Session = Depends(get_db)
):
    return login_user(db, user_data)


@router.post("/login")
def login_oauth(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user_data = LoginUser(
        email=form_data.username,
        password=form_data.password
    )
    return login_user(db, user_data)


@router.get("/me",status_code=status.HTTP_200_OK,response_model=ProfileResponse)
def get_profile(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/", status_code=status.HTTP_200_OK)
def get_users(
    db: Session = Depends(get_db),
    admin=Depends(admin_required)
):
    return db.query(User).all()



#  Delete user 


@router.delete( "/{user_id}/delete",status_code=status.HTTP_200_OK,response_model=UserResponse
)
def delete_user(user_id: UUID,db: Session = Depends(get_db),admin=Depends(admin_required)):
    deleted_user = db.query(User).filter(User.id == user_id).first()

    if not deleted_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    db.delete(deleted_user)
    db.commit()

    return deleted_user
