import logging
from abc import ABC, abstractmethod
from uuid import UUID

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.exception.database import DatabaseException
from app.core.exception.seat import (
    SeatAlreadyExistsException,
    SeatHasActiveBookingsException,
    SeatNotFoundException,
)
from app.models.seats import Seat
from app.repository.seat_repository import SeatRepository
from app.schemas.seats import SeatCreate


logger = logging.getLogger(__name__)


class SeatServiceBase(ABC):

    @abstractmethod
    def create_seat(self, db: Session, seat_data: SeatCreate) -> Seat:
        pass

    @abstractmethod
    def get_all_seats(self, db: Session) -> list[Seat]:
        pass

    @abstractmethod
    def delete_seat(self, db: Session, seat_id: UUID) -> bool:
        pass

    @abstractmethod
    def get_by_id(self, db: Session, seat_id: UUID) -> Seat:
        pass

    @abstractmethod
    def update_seat(self, db: Session, seat_id: UUID, seat_data) -> Seat:
        pass


class SeatService(SeatServiceBase):

    def __init__(self, repo: SeatRepository):
        self.repo = repo

    def get_all_seats(self, db: Session) -> list[Seat]:
        try:
            logger.info("Fetching all seats")

            seats = self.repo.get_all_seat(db)

            logger.info("Fetched seats successfully. count=%s", len(seats))

            return seats

        except SQLAlchemyError:
            logger.exception("Database error while fetching seats.")
            raise DatabaseException()

    def get_by_id(self, db: Session, seat_id: UUID) -> Seat:
        try:
            logger.info("Fetching seat by id. seat_id=%s", seat_id)

            seat = self.repo.get_by_id(db, seat_id)

            if not seat:
                logger.warning("Seat not found. seat_id=%s", seat_id)
                raise SeatNotFoundException()

            return seat

        except SeatNotFoundException:
            raise

        except SQLAlchemyError:
            logger.exception(
                "Database error while fetching seat. seat_id=%s",
                seat_id,
            )
            raise DatabaseException()

    def create_seat(self, db: Session, seat_data: SeatCreate) -> Seat:
        try:
            logger.info(
                "Creating seat. seat_number=%s floor=%s",
                seat_data.seat_number,
                seat_data.floor,
            )

            existing_seat = self.repo.get_seat_by_seat_number(
                db,
                seat_data.seat_number,
            )

            if existing_seat:
                logger.warning(
                    "Seat creation failed. Seat already exists. seat_number=%s",
                    seat_data.seat_number,
                )
                raise SeatAlreadyExistsException()

            seat = Seat(
                seat_number=seat_data.seat_number,
                is_active=seat_data.is_active,
                floor=seat_data.floor,
            )

            created_seat = self.repo.create_seat(db, seat)

            logger.info(
                "Seat created successfully. seat_id=%s seat_number=%s",
                created_seat.id,
                created_seat.seat_number,
            )

            return created_seat

        except SeatAlreadyExistsException:
            raise

        except SQLAlchemyError:
            db.rollback()
            logger.exception(
                "Database error while creating seat. seat_number=%s",
                seat_data.seat_number,
            )
            raise DatabaseException()

    def delete_seat(self, db: Session, seat_id: UUID) -> bool:
        try:
            logger.info("Deleting seat. seat_id=%s", seat_id)

            seat = self.repo.get_by_id(db, seat_id)

            if not seat:
                logger.warning("Delete failed. Seat not found. seat_id=%s", seat_id)
                raise SeatNotFoundException()

            if self.repo.seat_has_bookings(db, seat_id):
                logger.warning(
                    "Delete failed. Seat has active bookings. seat_id=%s",
                    seat_id,
                )
                raise SeatHasActiveBookingsException()

            self.repo.delete(db, seat)

            logger.info("Seat deleted successfully. seat_id=%s", seat_id)

            return True

        except (SeatNotFoundException, SeatHasActiveBookingsException):
            raise

        except SQLAlchemyError:
            db.rollback()
            logger.exception(
                "Database error while deleting seat. seat_id=%s",
                seat_id,
            )
            raise DatabaseException()

    def update_seat(self, db: Session, seat_id: UUID, seat_data) -> Seat:
        try:
            logger.info("Updating seat. seat_id=%s", seat_id)

            seat = self.repo.get_by_id(db, seat_id)

            if not seat:
                logger.warning("Update failed. Seat not found. seat_id=%s", seat_id)
                raise SeatNotFoundException()

            if seat_data.seat_number:
                existing = self.repo.get_seat_by_seat_number(
                    db,
                    seat_data.seat_number,
                )

                if existing and existing.id != seat_id:
                    logger.warning(
                        "Update failed. Seat number already exists. seat_number=%s",
                        seat_data.seat_number,
                    )
                    raise SeatAlreadyExistsException()

            updated_seat = self.repo.update_seat(
                db,
                seat,
                seat_data.model_dump(exclude_unset=True),
            )

            logger.info("Seat updated successfully. seat_id=%s", seat_id)

            return updated_seat

        except (SeatNotFoundException, SeatAlreadyExistsException):
            raise

        except SQLAlchemyError:
            db.rollback()
            logger.exception(
                "Database error while updating seat. seat_id=%s",
                seat_id,
            )
            raise DatabaseException()