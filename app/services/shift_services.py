# app/services/shift_service.py

from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List
from uuid import UUID
import uuid
import json

from app.models.shift import Shift
from app.schemas.shift import ShiftCreate
from app.repository.shift_repository import ShiftRepositoryBase
from app.redis.client import redis_client



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
    def create_shift(self, db: Session, shift: ShiftCreate):
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
    def create_shift(self, db: Session, name , start_time , end_time):

        if start_time >= end_time:
            raise HTTPException(
                status_code=400,
                detail="Start time must be before end time"
            )
            
        if self.repo.get_shift_by_name(db, name):
            raise HTTPException(
                status_code=400,
                detail=f"Shift '{name}' already exists"
            )

        new_shift = Shift(
            id=uuid.uuid4(),
            name=name,
            start_time=start_time,
            end_time=end_time
        )

        created = self.repo.create_shift(db, new_shift)

        if redis_client:
            redis_client.delete("shifts:all")

        return ShiftDTO(created).to_dict()



    def get_all_shift(self, db: Session):

        cache_key = "shifts:all"

        if redis_client:
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)

        shifts = self.repo.get_all_shifts(db)

        if not shifts:
            return [] 

        result = [ShiftDTO(s).to_dict() for s in shifts]

        if redis_client:
            redis_client.setex(cache_key, 300, json.dumps(result))

        return result

    # =====================================================
    # DELETE SHIFT
    # =====================================================
    def delete_shift(self, db: Session, shift_id: UUID):

        shift = self.repo.get_shift_by_id(db, shift_id)

        if not shift:
            raise HTTPException(
                status_code=404,
                detail="Shift not found"
            )

        self.repo.delete_shift(db, shift_id)

        if redis_client:
            redis_client.delete("shifts:all")
            redis_client.delete(f"shift:{shift_id}")

        return {"message": "Shift deleted successfully"}