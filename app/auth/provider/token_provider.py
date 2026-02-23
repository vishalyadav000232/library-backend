from jose import jwt, JWTError
import os
from typing import Optional
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from fastapi import HTTPException, status
from uuid import UUID
from app.auth.interface.token_provider import TokenProvider

load_dotenv()


class JWTTokenProvider(TokenProvider):

    def __init__(self):
        self.SECRET_KEY = os.getenv("SECRET_KEY")
        if not self.SECRET_KEY:
            raise RuntimeError("SECRET_KEY not set")

        self.ALGORITHM = "HS256"
        self.ACCESS_EXPIRE_HOURS = 15
        self.REFRESH_EXPIRE_DAYS = 7


    # =====================================================
    # CREATE ACCESS TOKEN
    # =====================================================
    def create_access_token(self, user_id: UUID, role: str) -> str:
        payload = {
            "sub": str(user_id),
            "role": role,
            "type": "access",
            "exp": datetime.now(timezone.utc)
                  + timedelta(seconds=self.ACCESS_EXPIRE_HOURS),
        }

        return jwt.encode(payload, self.SECRET_KEY, algorithm=self.ALGORITHM)


    # =====================================================
    # CREATE REFRESH TOKEN
    # =====================================================
    def create_refresh_token(self, user_id: UUID, role: Optional[str] = "user") -> str:

        payload = {
            "sub": str(user_id),
            "role": role or "user",
            "type": "refresh",
            "exp": datetime.now(timezone.utc)
                  + timedelta(days=self.REFRESH_EXPIRE_DAYS),
        }

        return jwt.encode(payload, self.SECRET_KEY, algorithm=self.ALGORITHM)


    def verify_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(
                token,
                self.SECRET_KEY,
                algorithms=[self.ALGORITHM]
            )

            if payload.get("type") != "access":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid access token"
                )

            return payload

        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired access token"
            )


    def verify_refresh_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(
                token,
                self.SECRET_KEY,
                algorithms=[self.ALGORITHM]
            )
            print("from veryfy : ",payload)

            if payload.get("type") != "refresh":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid refresh token"
                )

            return payload

        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token"
            )