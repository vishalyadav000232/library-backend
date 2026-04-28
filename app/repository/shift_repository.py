from app.models.shift import Shift
from sqlalchemy.orm import Session
from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID


class ShiftRepositoryBase(ABC):

    @abstractmethod
    def create_shift(self, db: Session, shift: Shift) -> Shift:
        pass

    @abstractmethod
    def get_shift_by_name(self, db: Session, name: str) -> Optional[Shift]:
        pass

    @abstractmethod
    def get_all_shifts(self, db: Session) -> List[Shift]:
        pass

    @abstractmethod
    def get_shift_by_id(self, db: Session, shift_id: UUID) -> Optional[Shift]:
        pass

    @abstractmethod
    def delete_shift(self, db: Session, shift_id: UUID) -> None:
        pass

# =====================================================

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

    def get_shift_by_name(self, db: Session, name: str) -> Optional[Shift]:
        return db.query(Shift).filter(Shift.name == name).first()

    def get_all_shifts(self, db: Session) -> List[Shift]:
        return db.query(Shift).all()

    def get_shift_by_id(self, db: Session, shift_id: UUID) -> Optional[Shift]:
        return db.query(Shift).filter(Shift.id == shift_id).first()

    def delete_shift(self, db: Session, shift_id: UUID) -> None:
        shift = self.get_shift_by_id(db, shift_id)

        if not shift:
            return  

        try:
            db.delete(shift)
            db.commit()
        except Exception:
            db.rollback()
            raise