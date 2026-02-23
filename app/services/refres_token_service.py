from datetime import datetime, timedelta
from fastapi import HTTPException, status
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.user import User
from app.auth.provider.token_provider import JWTTokenProvider
from app.repository.refresh_token_repository import RefreshTokenRepositoryBase
from app.utils.hash_refresh_token import hash_token


class RefreshTokenService:

    def __init__(
        self,
        repo: RefreshTokenRepositoryBase,
        token_provider: JWTTokenProvider
    ):
        self.repo = repo
        self.token_provider = token_provider
        self.REFRESH_EXPIRE_DAYS = 7

    # =====================================================
    # CREATE + STORE REFRESH TOKEN IN DATABASE
    # =====================================================
    def create_and_store(self, db: Session, user: User) -> str:

        refresh_token = self.token_provider.create_refresh_token(
            user.id,
            user.role
        )

        self.repo.create(
            db=db,
            user_id=user.id,
            token_hash=hash_token(refresh_token),
            expires_at=datetime.utcnow() + timedelta(days=self.REFRESH_EXPIRE_DAYS)
        )

        return refresh_token

    # =====================================================
    # ROTATE REFRESH TOKEN (MAIN SECURITY LOGIC)
    # =====================================================
    def rotate(self, db: Session, refresh_token: str, user: User):

        payload = self.token_provider.verify_refresh_token(refresh_token)

        user_id = payload.get("sub")
        role = payload.get("role")

        if not user_id or not role:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token payload"
            )

        # 2️⃣ Validate token exists in DB
        token_hash_value = hash_token(refresh_token)
        token_record = self.repo.find_valid(db, token_hash_value)
        print(token_record)

        # 3️⃣ Reuse detection (VERY IMPORTANT SECURITY)
        if not token_record:
            self.repo.revoke_all_user_tokens(db, UUID(user_id))
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token reuse detected"
            )

        # 4️⃣ Revoke old refresh token
        self.repo.revoke(db, token_record)

        # 5️⃣ Generate new tokens
        new_access = self.token_provider.create_access_token(
            user.id,
            user.role
        )

        new_refresh = self.create_and_store(db, user)

        return new_access, new_refresh

    # =====================================================
    # LOGOUT (REVOKE CURRENT TOKEN)
    # =====================================================
    def logout(self, db: Session, refresh_token: str):

        try:
            self.token_provider.verify_refresh_token(refresh_token)
        except Exception:
            # Don't leak info if token invalid
            return

        token_hash_value = hash_token(refresh_token)
        token = self.repo.find_valid(db, token_hash_value)
        print(token)

        if token:
            self.repo.revoke(db, token)