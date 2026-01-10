from fastapi import HTTPException, status ,Depends
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, LoginUser
from datetime import datetime, timedelta, timezone
from jose import jwt , JWTError
from dotenv import load_dotenv
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer
from app.database.db import get_db
import os

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


# ✅ SIGNUP
def create_user(db: Session, user_data: UserCreate) -> User:
    if get_user_by_email(db, user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    new_user = User(
        name=user_data.name,
        email=user_data.email,
        
    )

    new_user.set_password(user_data.password)


    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# ✅ LOGIN
def login_user(db: Session, user_data: LoginUser):
    user = db.query(User).filter(User.email == user_data.email).first()

    if not user or not user.verify_password(user_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    payload = {
        "sub": str(user.id),                    # JWT standard
        "role": user.role,
        "exp": datetime.now(timezone.utc) + timedelta(hours=12)
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return {
        "message" : "User Successfully Login",
        "access_token": token,
        "token_type": "bearer"
    }


async def get_current_user(
    token: Annotated[str, Depends(oauth2_bearer)],
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is invalid or expired"
        )

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user
