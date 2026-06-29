import json
import logging
from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.exception.database import DatabaseException
from app.core.exception.user import (
    EmailAlreadyExistsException,
    UserCacheException,
    UserNotFoundException,
)
from app.dto.user_dto import PaginatedUsersDTO, UserDTO
from app.models.user import User
from app.redis.client import CACHE_TTL, redis_client
from app.repository.user_repository import UserRepositoryBase
from app.schemas.user import UserCreate, UserUpdate


logger = logging.getLogger(__name__)


class UserServiceInterface(ABC):

    @abstractmethod
    def get_users(
        self,
        db: Session,
        limit: int,
        offset: int,
        search: Optional[str],
        is_active: Optional[bool],
    ):
        pass

    @abstractmethod
    def get_user(self, db: Session, user_id: UUID):
        pass

    @abstractmethod
    def create_user(self, db: Session, user_data: UserCreate):
        pass

    @abstractmethod
    def update_user(self, db: Session, user_id: UUID, user_data: UserUpdate):
        pass

    @abstractmethod
    def delete_user(self, db: Session, user_id: UUID):
        pass

    @abstractmethod
    def change_status(self, db: Session, user_id: UUID, is_active: bool):
        pass


class UserService(UserServiceInterface):

    def __init__(self, repo: UserRepositoryBase):
        self.repo = repo

    def get_users(
        self,
        db: Session,
        limit: int,
        offset: int,
        search: Optional[str] = None,
        is_active: Optional[bool] = None,
    ):
        cache_key = f"users:{limit}:{offset}:{search}:{is_active}"

        try:
            logger.info(
                "Fetching users. limit=%s offset=%s search=%s is_active=%s",
                limit,
                offset,
                search,
                is_active,
            )

            cached = self._cache_get(cache_key)

            if cached:
                logger.info("Users fetched from cache. cache_key=%s", cache_key)
                return cached

            users, total = self.repo.get_users(
                db,
                limit,
                offset,
                search,
                is_active,
            )

            items = [
                UserDTO.model_validate(user).model_dump()
                for user in users
            ]

            page = (offset // limit) + 1
            pages = (total + limit - 1) // limit

            response = PaginatedUsersDTO(
                items=items,
                total=total,
                page=page,
                size=limit,
                pages=pages,
            ).model_dump()

            self._cache_set(cache_key, response, CACHE_TTL)

            logger.info(
                "Users fetched successfully. total=%s page=%s size=%s",
                total,
                page,
                limit,
            )

            return response

        except UserCacheException:
            raise

        except SQLAlchemyError:
            logger.exception("Database error while fetching users.")
            raise DatabaseException()

    def get_user(self, db: Session, user_id: UUID):
        cache_key = f"user:{user_id}"

        try:
            logger.info("Fetching user. user_id=%s", user_id)

            cached = self._cache_get(cache_key)

            if cached:
                logger.info("User fetched from cache. user_id=%s", user_id)
                return cached

            user = self.repo.get_user_by_id(db, user_id)

            if not user:
                logger.warning("User not found. user_id=%s", user_id)
                raise UserNotFoundException()

            dto = UserDTO.model_validate(user).model_dump()

            self._cache_set(cache_key, dto, CACHE_TTL)

            logger.info("User fetched successfully. user_id=%s", user_id)

            return dto

        except (UserNotFoundException, UserCacheException):
            raise

        except SQLAlchemyError:
            logger.exception(
                "Database error while fetching user. user_id=%s",
                user_id,
            )
            raise DatabaseException()

    def create_user(self, db: Session, user_data: UserCreate):
        try:
            logger.info("Creating user. email=%s", user_data.email)

            user = User(
                id=uuid4(),
                name=user_data.name,
                email=user_data.email,
                is_active=True,
            )

            created_user = self.repo.create(db, user)

            self._clear_users_cache()

            logger.info(
                "User created successfully. user_id=%s email=%s",
                created_user.id,
                created_user.email,
            )

            return UserDTO.model_validate(created_user).model_dump()

        except IntegrityError:
            db.rollback()
            logger.warning(
                "User creation failed. Email already exists. email=%s",
                user_data.email,
            )
            raise EmailAlreadyExistsException()

        except UserCacheException:
            raise

        except SQLAlchemyError:
            db.rollback()
            logger.exception(
                "Database error while creating user. email=%s",
                user_data.email,
            )
            raise DatabaseException()

    def update_user(self, db: Session, user_id: UUID, user_data: UserUpdate):
        try:
            logger.info("Updating user. user_id=%s", user_id)

            user = self.repo.get_user_by_id(db, user_id)

            if not user:
                logger.warning("Update failed. User not found. user_id=%s", user_id)
                raise UserNotFoundException()

            if user_data.name is not None:
                user.name = user_data.name

            if user_data.email is not None:
                user.email = user_data.email

            updated_user = self.repo.update_user(db, user)

            self._clear_user_cache(user_id)

            logger.info("User updated successfully. user_id=%s", user_id)

            return UserDTO.model_validate(updated_user).model_dump()

        except UserNotFoundException:
            raise

        except IntegrityError:
            db.rollback()
            logger.warning(
                "User update failed. Email already exists. user_id=%s email=%s",
                user_id,
                user_data.email,
            )
            raise EmailAlreadyExistsException()

        except UserCacheException:
            raise

        except SQLAlchemyError:
            db.rollback()
            logger.exception(
                "Database error while updating user. user_id=%s",
                user_id,
            )
            raise DatabaseException()

    def delete_user(self, db: Session, user_id: UUID):
        try:
            logger.info("Deleting user. user_id=%s", user_id)

            user = self.repo.get_user_by_id(db, user_id)

            if not user:
                logger.warning("Delete failed. User not found. user_id=%s", user_id)
                raise UserNotFoundException()

            self.repo.delete_user(db, user)

            self._clear_user_cache(user_id)

            logger.info("User deleted successfully. user_id=%s", user_id)

            return {"message": "User deleted successfully"}

        except UserNotFoundException:
            raise

        except UserCacheException:
            raise

        except SQLAlchemyError:
            db.rollback()
            logger.exception(
                "Database error while deleting user. user_id=%s",
                user_id,
            )
            raise DatabaseException()

    def change_status(
        self,
        db: Session,
        user_id: UUID,
        is_active: bool,
    ):
        try:
            logger.info(
                "Changing user status. user_id=%s is_active=%s",
                user_id,
                is_active,
            )

            user = self.repo.get_user_by_id(db, user_id)

            if not user:
                logger.warning(
                    "Change status failed. User not found. user_id=%s",
                    user_id,
                )
                raise UserNotFoundException()

            user.is_active = is_active

            updated_user = self.repo.update_user(db, user)

            self._clear_user_cache(user_id)

            logger.info(
                "User status changed successfully. user_id=%s is_active=%s",
                user_id,
                is_active,
            )

            return UserDTO.model_validate(updated_user).model_dump()

        except UserNotFoundException:
            raise

        except UserCacheException:
            raise

        except SQLAlchemyError:
            db.rollback()
            logger.exception(
                "Database error while changing user status. user_id=%s",
                user_id,
            )
            raise DatabaseException()

    def _cache_get(self, key: str):
        if not redis_client:
            return None

        try:
            cached = redis_client.get(key)

            if not cached:
                return None

            return json.loads(cached)

        except json.JSONDecodeError:
            logger.exception("Invalid cache JSON. cache_key=%s", key)
            redis_client.delete(key)
            raise UserCacheException()

        except Exception:
            logger.exception("Failed to read user cache. cache_key=%s", key)
            raise UserCacheException()

    def _cache_set(self, key: str, value, ttl: int) -> None:
        if not redis_client:
            return

        try:
            redis_client.setex(
                key,
                ttl,
                json.dumps(value, default=str),
            )

        except Exception:
            logger.exception("Failed to set user cache. cache_key=%s", key)
            raise UserCacheException()

    def _clear_user_cache(self, user_id: UUID) -> None:
        if not redis_client:
            return

        try:
            redis_client.delete(f"user:{user_id}")
            self._clear_users_cache()

        except Exception:
            logger.exception("Failed to clear user cache. user_id=%s", user_id)
            raise UserCacheException()

    def _clear_users_cache(self) -> None:
        if not redis_client:
            return

        try:
            redis_client.flushdb()

        except Exception:
            logger.exception("Failed to clear users cache.")
            raise UserCacheException()