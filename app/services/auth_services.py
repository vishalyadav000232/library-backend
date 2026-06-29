import logging
from abc import ABC, abstractmethod
from uuid import UUID

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.auth.interface.token_provider import TokenProvider as Token
from app.core.exception.auth import InvalidCredentialsException
from app.core.exception.database import DatabaseException
from app.core.exception.user import (
    EmailAlreadyExistsException,
    UserNotFoundException,
)
from app.models.user import User
from app.repository.user_repository import UserRepositoryBase
from app.schemas.user import LoginUser, UserCreate

logger = logging.getLogger(__name__)


class UserServiceBase(ABC):

    @abstractmethod
    def create_user(self, db: Session, user_data: UserCreate) -> User:
        pass

    @abstractmethod
    def login_user(self, db: Session, user_data: LoginUser) -> User:
        pass

    @abstractmethod
    def delete_user(self, db: Session, user_id: UUID) -> User:
        pass

    @abstractmethod
    def get_all_user(self, db: Session) -> list[User]:
        pass

    @abstractmethod
    def get_user_by_id(self, db: Session, user_id: UUID) -> User:
        pass

    @abstractmethod
    def change_status(self, db: Session, user_id: UUID, is_active: bool) -> User:
        pass


class UserServices(UserServiceBase):

    def __init__(self, repo: UserRepositoryBase, token_provider: Token):
        self.repo = repo
        self.token_provider = token_provider

    def create_user(self, db: Session, user_data: UserCreate) -> User:
        try:
            logger.info("Creating user with email=%s", user_data.email)

            existing_user = self.repo.get_user_by_email(db, user_data.email)

            if existing_user:
                logger.warning(
                    "User creation failed. Email already exists: %s",
                    user_data.email,
                )
                raise EmailAlreadyExistsException()

            new_user = User(
                name=user_data.name,
                email=user_data.email,
                role=user_data.role,
            )

            new_user.set_password(user_data.password)

            created_user = self.repo.create(db, new_user)

            logger.info(
                "User created successfully. user_id=%s email=%s",
                created_user.id,
                created_user.email,
            )

            return created_user

        except EmailAlreadyExistsException:
            raise

        except SQLAlchemyError:
            logger.exception(
                "Database error while creating user. email=%s",
                user_data.email,
            )
            db.rollback()
            raise DatabaseException()

    def login_user(self, db: Session, user_data: LoginUser) -> User:
        try:
            logger.info("Login attempt for email=%s", user_data.email)

            user = self.repo.get_user_by_email(db, user_data.email)

            if not user or not user.verify_password(user_data.password):
                logger.warning(
                    "Login failed due to invalid credentials. email=%s",
                    user_data.email,
                )
                raise InvalidCredentialsException()

            if not user.is_active:
                logger.warning(
                    "Login failed because account is inactive. user_id=%s",
                    user.id,
                )
                raise InvalidCredentialsException()

            logger.info(
                "User login successful. user_id=%s email=%s",
                user.id,
                user.email,
            )

            return user

        except InvalidCredentialsException:
            raise

        except SQLAlchemyError:
            logger.exception(
                "Database error during login. email=%s",
                user_data.email,
            )
            raise DatabaseException()

    def delete_user(self, db: Session, user_id: UUID) -> User:
        try:
            logger.info("Deleting user. user_id=%s", user_id)

            user = self.repo.get_user_by_id(db, user_id)

            if not user:
                logger.warning("Delete user failed. User not found. user_id=%s", user_id)
                raise UserNotFoundException()

            self.repo.delete_user(db, user_id)

            logger.info("User deleted successfully. user_id=%s", user_id)

            return user

        except UserNotFoundException:
            raise

        except SQLAlchemyError:
            logger.exception(
                "Database error while deleting user. user_id=%s",
                user_id,
            )
            db.rollback()
            raise DatabaseException()

    def get_all_user(self, db: Session) -> list[User]:
        try:
            logger.info("Fetching all users")

            users = self.repo.get_all_users(db)

            if not users:
                logger.warning("No users found")
                raise UserNotFoundException()

            logger.info("Fetched users successfully. count=%s", len(users))

            return users

        except UserNotFoundException:
            raise

        except SQLAlchemyError:
            logger.exception("Database error while fetching all users")
            raise DatabaseException()

    def get_user_by_id(self, db: Session, user_id: UUID) -> User:
        try:
            logger.info("Fetching user by id. user_id=%s", user_id)

            user = self.repo.get_user_by_id(db, user_id)

            if not user:
                logger.warning("User not found. user_id=%s", user_id)
                raise UserNotFoundException()

            logger.info("User fetched successfully. user_id=%s", user_id)

            return user

        except UserNotFoundException:
            raise

        except SQLAlchemyError:
            logger.exception(
                "Database error while fetching user. user_id=%s",
                user_id,
            )
            raise DatabaseException()

    def change_status(
        self,
        db: Session,
        user_id: UUID,
        is_active: bool,
    ) -> User:
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

            db.commit()
            db.refresh(user)

            logger.info(
                "User status changed successfully. user_id=%s is_active=%s",
                user_id,
                is_active,
            )

            return user

        except UserNotFoundException:
            raise

        except SQLAlchemyError:
            logger.exception(
                "Database error while changing user status. user_id=%s",
                user_id,
            )
            db.rollback()
            raise DatabaseException()