from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from app.models.refresh_token import RefreshToken
from datetime import datetime
from uuid import UUID


class RefreshTokenRepositoryBase(ABC):

    @abstractmethod
    def create(
        self,
        db: Session,
        user_id: UUID,
        token_hash: str,
        expires_at
    ) -> RefreshToken:
        pass

    @abstractmethod
    def find_valid(
        self,
        db: Session,
        token_hash: str
    ) -> RefreshToken | None:
        pass

    @abstractmethod
    def revoke(
        self,
        db: Session,
        token: RefreshToken
    ) -> None:
        pass

    @abstractmethod
    def revoke_all_user_tokens(
        self,
        db: Session,
        user_id: UUID
    ) -> None:
        pass
    


class RefreshTokenRepository(RefreshTokenRepositoryBase):

    def create(
        self,
        db: Session,
        user_id: UUID,
        token_hash: str,
        expires_at
    ) -> RefreshToken:

        token = RefreshToken(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at
        )

        db.add(token)
        db.commit()
        db.refresh(token)

        return token

    def find_valid(
        self,
        db: Session,
        token_hash: str
    ) -> RefreshToken | None:

        return db.query(RefreshToken).filter(
            RefreshToken.token_hash == token_hash,
            RefreshToken.revoked == False,
            RefreshToken.expires_at > datetime.utcnow()
        ).first()

    def revoke(
        self,
        db: Session,
        token: RefreshToken
    ) -> None:

        token.revoked = True
        db.commit()

    def revoke_all_user_tokens(
        self,
        db: Session,
        user_id: UUID
    ) -> None:

        db.query(RefreshToken).filter(
            RefreshToken.user_id == user_id
        ).update(
            {"revoked": True},
            synchronize_session=False
        )

        db.commit()