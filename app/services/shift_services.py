import json
import logging
import uuid
from abc import ABC, abstractmethod
from uuid import UUID

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.exception.database import DatabaseException
from app.core.exception.shift import (
    InvalidShiftTimeException,
    ShiftAlreadyExistsException,
    ShiftCacheException,
    ShiftNotFoundException,
)
from app.models.shift import Shift
from app.redis.client import redis_client
from app.repository.shift_repository import ShiftRepositoryBase


logger = logging.getLogger(__name__)


class ShiftDTO:
    def __init__(self, shift: Shift):
        self.id = shift.id
        self.name = shift.name
        self.start_time = shift.start_time
        self.end_time = shift.end_time

    def to_dict(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "start_time": str(self.start_time),
            "end_time": str(self.end_time),
        }


class ShiftServiceInterface(ABC):

    @abstractmethod
    def create_shift(self, db: Session, name, start_time, end_time):
        pass

    @abstractmethod
    def get_all_shift(self, db: Session):
        pass

    @abstractmethod
    def delete_shift(self, db: Session, shift_id: UUID):
        pass


class ShiftService(ShiftServiceInterface):

    def __init__(self, repo: ShiftRepositoryBase):
        self.repo = repo

    def create_shift(self, db: Session, name, start_time, end_time):
        try:
            logger.info(
                "Creating shift. name=%s start_time=%s end_time=%s",
                name,
                start_time,
                end_time,
            )

            if start_time >= end_time:
                logger.warning(
                    "Invalid shift time. name=%s start_time=%s end_time=%s",
                    name,
                    start_time,
                    end_time,
                )
                raise InvalidShiftTimeException()

            existing_shift = self.repo.get_shift_by_name(db, name)

            if existing_shift:
                logger.warning("Shift already exists. name=%s", name)
                raise ShiftAlreadyExistsException()

            new_shift = Shift(
                id=uuid.uuid4(),
                name=name,
                start_time=start_time,
                end_time=end_time,
            )

            created_shift = self.repo.create_shift(db, new_shift)

            self._clear_shift_cache(created_shift.id)

            logger.info(
                "Shift created successfully. shift_id=%s name=%s",
                created_shift.id,
                created_shift.name,
            )

            return ShiftDTO(created_shift).to_dict()

        except (
            InvalidShiftTimeException,
            ShiftAlreadyExistsException,
            ShiftCacheException,
        ):
            raise

        except SQLAlchemyError:
            db.rollback()
            logger.exception("Database error while creating shift. name=%s", name)
            raise DatabaseException()

    def get_all_shift(self, db: Session):
        cache_key = "shifts:all"

        try:
            logger.info("Fetching all shifts")

            if redis_client:
                cached = redis_client.get(cache_key)

                if cached:
                    logger.info("Shifts fetched from cache.")
                    return json.loads(cached)

            shifts = self.repo.get_all_shifts(db)

            if not shifts:
                logger.info("No shifts found.")
                return []

            result = [ShiftDTO(shift).to_dict() for shift in shifts]

            if redis_client:
                redis_client.setex(cache_key, 300, json.dumps(result))
                logger.info("Shifts stored in cache. count=%s", len(result))

            logger.info("Shifts fetched successfully. count=%s", len(result))

            return result

        except json.JSONDecodeError:
            logger.exception("Invalid shift cache data.")
            raise ShiftCacheException()

        except SQLAlchemyError:
            logger.exception("Database error while fetching shifts.")
            raise DatabaseException()

    def delete_shift(self, db: Session, shift_id: UUID):
        try:
            logger.info("Deleting shift. shift_id=%s", shift_id)

            shift = self.repo.get_shift_by_id(db, shift_id)

            if not shift:
                logger.warning("Shift not found. shift_id=%s", shift_id)
                raise ShiftNotFoundException()

            self.repo.delete_shift(db, shift_id)

            self._clear_shift_cache(shift_id)

            logger.info("Shift deleted successfully. shift_id=%s", shift_id)

            return {"message": "Shift deleted successfully"}

        except (ShiftNotFoundException, ShiftCacheException):
            raise

        except SQLAlchemyError:
            db.rollback()
            logger.exception(
                "Database error while deleting shift. shift_id=%s",
                shift_id,
            )
            raise DatabaseException()

    def _clear_shift_cache(self, shift_id: UUID | None = None) -> None:
        if not redis_client:
            return

        try:
            redis_client.delete("shifts:all")

            if shift_id:
                redis_client.delete(f"shift:{shift_id}")

            logger.info("Shift cache cleared. shift_id=%s", shift_id)

        except Exception:
            logger.exception("Failed to clear shift cache. shift_id=%s", shift_id)
            raise ShiftCacheException()