from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.user import User
from app.services.user_services import get_current_user
from app.database.db import get_db
from app.schemas.user import (
    UserCreate,
    UserResponse,
    LoginUser,
    TokenResponse,
    ProfileResoponse
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
    response_model=TokenResponse
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
            status_code=500,
            detail="Something went wrong during login"
        )


@router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    response_model=ProfileResoponse
)
def get_profile(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email
    }


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    
)
def get_users(db: Session = Depends(get_db)):
    return  db.query(User).all()