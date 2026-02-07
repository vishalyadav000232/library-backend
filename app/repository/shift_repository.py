
from app.models.shift import Shift
import uuid
from sqlalchemy.orm import Session
from abc import ABC , abstractmethod


class ShiftRepositoryBase(ABC):

    @abstractmethod
    def create_shift(self, db: Session, shift: Shift) -> Shift:
        pass

    @abstractmethod
    def get_shift_by_name(self, db: Session, name: str) -> Shift | None:
        pass




class ShiftRepository(ShiftRepositoryBase):

    def create_shift(self, db: Session, shift: Shift) -> Shift:
        try:
            db.add(shift)
            db.commit()
            db.refresh(shift)
            return shift
        except Exception:
            db.rollback()
            raise

    def get_shift_by_name(self, db: Session, name: str):
        return db.query(Shift).filter(Shift.name == name).first()
