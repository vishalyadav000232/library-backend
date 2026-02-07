from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.shift import Shift
import uuid
from app.repository.shift_repository import ShiftRepositoryBase



class ShiftServiceBase(ABC):

    @abstractmethod
    def create_shift(self,db: Session,name: str,start_time,end_time):
        pass



class ShiftService(ShiftServiceBase):

    def __init__(self, repo: ShiftRepositoryBase):
        self.repo = repo

    def create_shift(
        self,
        db: Session,
        name: str,
        start_time,
        end_time
    ):

        if self.repo.get_shift_by_name(db, name):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Shift with name '{name}' already exists."
            )

        new_shift = Shift(
            id=uuid.uuid4(),
            name=name,
            start_time=start_time,
            end_time=end_time
        )

        return self.repo.create_shift(db, new_shift)


    