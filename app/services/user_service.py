from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID, uuid4
from fastapi import HTTPException
import json

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.dto.user_dto import UserDTO, PaginatedUsersDTO

from app.redis.client import redis_client, CACHE_TTL
from app.repository.user_repository import UserRepositoryBase


# =====================================================
# INTERFACE
# =====================================================
class UserServiceInterface(ABC):

    @abstractmethod
    def get_users(self, db: Session, limit: int, offset: int,
                  search: Optional[str], is_active: Optional[bool]):
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


# =====================================================
# SERVICE IMPLEMENTATION
# =====================================================
class UserService(UserServiceInterface):

    def __init__(self, repo: UserRepositoryBase):
        self.repo = repo

    # -------------------------
    # GET USERS (PAGINATED)
    # -------------------------
    def get_users(self, db, limit, offset, search=None, is_active=None):

        cache_key = f"users:{limit}:{offset}:{search}:{is_active}"

        cached = redis_client.get(cache_key)
        if cached:
            return json.loads(cached)

        users, total = self.repo.get_users(db, limit, offset, search, is_active)

        items = [UserDTO.model_validate(u).model_dump() for u in users]

        page = (offset // limit) + 1
        pages = (total + limit - 1) // limit

        response = PaginatedUsersDTO(
            items=items,
            total=total,
            page=page,
            size=limit,
            pages=pages
        ).model_dump()

        redis_client.setex(
            cache_key,
            CACHE_TTL,
            json.dumps(response, default=str)
        )

        return response

    # -------------------------
    # GET USER BY ID
    # -------------------------
    def get_user(self, db, user_id):

        cache_key = f"user:{user_id}"

        cached = redis_client.get(cache_key)
        if cached:
            return json.loads(cached)

        user = self.repo.get_user_by_id(db, user_id)

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        dto = UserDTO.model_validate(user).model_dump()

        redis_client.setex(cache_key, 300, json.dumps(dto, default=str))

        return dto

    # -------------------------
    # CREATE USER
    # -------------------------
    def create_user(self, db, user_data):

        user = User(
            id=uuid4(),
            name=user_data.name,
            email=user_data.email,
            is_active=True
        )

        created = self.repo.create(db, user)

        redis_client.flushdb()

        return UserDTO.model_validate(created).model_dump()

    # -------------------------
    # UPDATE USER
    # -------------------------
    def update_user(self, db, user_id, user_data):

        user = self.repo.get_user_by_id(db, user_id)

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if user_data.name is not None:
            user.name = user_data.name

        if user_data.email is not None:
            user.email = user_data.email

        updated = self.repo.update_user(db, user)

        redis_client.delete(f"user:{user_id}")
        redis_client.flushdb()

        return UserDTO.model_validate(updated).model_dump()

    # -------------------------
    # DELETE USER
    # -------------------------
    def delete_user(self, db, user_id):

        user = self.repo.get_user_by_id(db, user_id)
        
        

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        self.repo.delete_user(db, user)

        redis_client.delete(f"user:{user_id}")
        redis_client.flushdb()

        return {"message": "User deleted successfully"}

    # -------------------------
    # CHANGE STATUS
    # -------------------------
    def change_status(self, db, user_id, is_active: bool):

        user = self.repo.get_user_by_id(db, user_id)

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        user.is_active = is_active

        updated = self.repo.update_user(db, user)

        redis_client.delete(f"user:{user_id}")
        redis_client.flushdb()

        return UserDTO.model_validate(updated).model_dump()