import logging
import os
from datetime import datetime, timedelta, timezone
from uuid import UUID

from dotenv import load_dotenv
from jose import JWTError, ExpiredSignatureError, jwt

from app.core.exception.auth import (
    InvalidTokenException,
    TokenExpiredException,
)
from app.auth.interface.token_provider import TokenProvider


load_dotenv()

logger = logging.getLogger(__name__)


class TokenService(TokenProvider):

    def __init__(self):
        self.SECRET_KEY = os.getenv("SECRET_KEY")

        if not self.SECRET_KEY:
            logger.critical("SECRET_KEY environment variable is missing.")
            raise RuntimeError("SECRET_KEY is not configured.")

        self.ALGORITHM = "HS256"
        self.EXPIRY = 6

        logger.info("TokenService initialized successfully.")

    def create_token(self, user_id: UUID, role: str) -> str:
        logger.info(
            "Generating access token. user_id=%s role=%s",
            user_id,
            role,
        )

        payload = {
            "sub": str(user_id),
            "role": role,
            "exp": datetime.now(timezone.utc)
            + timedelta(hours=self.EXPIRY),
        }

        token = jwt.encode(
            payload,
            self.SECRET_KEY,
            algorithm=self.ALGORITHM,
        )

        logger.info("Access token generated successfully. user_id=%s", user_id)

        return token

    def verify_token(self, token: str) -> dict:
        try:
            logger.info("Verifying JWT token.")

            payload = jwt.decode(
                token,
                self.SECRET_KEY,
                algorithms=[self.ALGORITHM],
            )

            logger.info(
                "JWT token verified successfully. user_id=%s",
                payload.get("sub"),
            )

            return payload

        except ExpiredSignatureError:
            logger.warning("JWT token has expired.")
            raise TokenExpiredException()

        except JWTError:
            logger.warning("Invalid JWT token.")
            raise InvalidTokenException()

        except Exception:
            logger.exception("Unexpected error while verifying JWT token.")
            raise InvalidTokenException()