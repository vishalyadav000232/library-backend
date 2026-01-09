from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, LoginUser
from datetime import datetime, timedelta, timezone
from jose import jwt
from dotenv import load_dotenv
import os

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"


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
        hashed_password = user_data.password
    )


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
        "access_token": token,
        "token_type": "bearer"
    }
