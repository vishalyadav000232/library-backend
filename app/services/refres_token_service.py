import logging
from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.auth.provider.token_provider import JWTTokenProvider
from app.core.exception.auth import (
    InvalidRefreshTokenPayloadException,
    InvalidTokenException,
    RefreshTokenReuseDetectedException,
)
from app.core.exception.database import DatabaseException
from app.models.user import User
from app.repository.refresh_token_repository import RefreshTokenRepositoryBase
from app.utils.hash_refresh_token import hash_token


logger = logging.getLogger(__name__)


class RefreshTokenService:

    def __init__(
        self,
        repo: RefreshTokenRepositoryBase,
        token_provider: JWTTokenProvider,
    ):
        self.repo = repo
        self.token_provider = token_provider
        self.REFRESH_EXPIRE_DAYS = 7

    def create_and_store(self, db: Session, user: User) -> str:
        try:
            logger.info("Creating refresh token. user_id=%s", user.id)

            refresh_token = self.token_provider.create_refresh_token(
                user.id,
                user.role,
            )

            self.repo.create(
                db=db,
                user_id=user.id,
                token_hash=hash_token(refresh_token),
                expires_at=datetime.now(timezone.utc)
                + timedelta(days=self.REFRESH_EXPIRE_DAYS),
            )

            logger.info("Refresh token stored successfully. user_id=%s", user.id)

            return refresh_token

        except SQLAlchemyError:
            db.rollback()
            logger.exception(
                "Database error while storing refresh token. user_id=%s",
                user.id,
            )
            raise DatabaseException()

    def rotate(self, db: Session, refresh_token: str, user: User):
        try:
            logger.info("Rotating refresh token. user_id=%s", user.id)

            payload = self.token_provider.verify_refresh_token(refresh_token)

            user_id = payload.get("sub")
            role = payload.get("role")

            if not user_id or not role:
                logger.warning("Invalid refresh token payload.")
                raise InvalidRefreshTokenPayloadException()

            if UUID(user_id) != user.id:
                logger.warning(
                    "Refresh token user mismatch. token_user_id=%s current_user_id=%s",
                    user_id,
                    user.id,
                )
                raise InvalidTokenException()

            token_hash_value = hash_token(refresh_token)
            token_record = self.repo.find_valid(db, token_hash_value)

            if not token_record:
                logger.warning(
                    "Refresh token reuse detected. user_id=%s",
                    user.id,
                )

                self.repo.revoke_all_user_tokens(db, UUID(user_id))

                raise RefreshTokenReuseDetectedException()

            self.repo.revoke(db, token_record)

            new_access = self.token_provider.create_access_token(
                user.id,
                user.role,
            )

            new_refresh = self.create_and_store(db, user)

            logger.info("Refresh token rotated successfully. user_id=%s", user.id)

            return new_access, new_refresh

        except (
            InvalidRefreshTokenPayloadException,
            InvalidTokenException,
            RefreshTokenReuseDetectedException,
        ):
            raise

        except SQLAlchemyError:
            db.rollback()
            logger.exception(
                "Database error while rotating refresh token. user_id=%s",
                user.id,
            )
            raise DatabaseException()

    def logout(self, db: Session, refresh_token: str) -> None:
        try:
            logger.info("Logout request received.")

            try:
                self.token_provider.verify_refresh_token(refresh_token)
            except Exception:
                logger.warning("Logout ignored because refresh token is invalid.")
                return

            token_hash_value = hash_token(refresh_token)
            token = self.repo.find_valid(db, token_hash_value)

            if token:
                self.repo.revoke(db, token)
                logger.info("Refresh token revoked successfully.")
            else:
                logger.info("No valid refresh token found during logout.")

        except SQLAlchemyError:
            db.rollback()
            logger.exception("Database error while logging out user.")
            raise DatabaseException()