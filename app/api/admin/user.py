# app/api/admin/admin_users.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import UUID

from app.database.db import get_db
from app.api.admin.admin_gaurd import admin_required
from app.services.user_service import UserServiceInterface
from app.dto.user_dto import PaginatedUsersDTO, UserDTO
from app.api.dependency import get_user_service_admin





router = APIRouter()




# =====================================================
# GET USERS (PAGINATION + SEARCH)
# =====================================================
@router.get("/", response_model=PaginatedUsersDTO)
def get_users(
    page: int = 1,
    size: int = 10,
    search: str | None = None,
    db: Session = Depends(get_db),
    admin=Depends(admin_required),
    service : UserServiceInterface = Depends(get_user_service_admin)
):
    return service.get_users(db, page, size, search)


# =====================================================
# GET USER BY ID
# =====================================================
@router.get("/{user_id}", response_model=UserDTO)
def get_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    admin=Depends(admin_required),
    service : UserServiceInterface = Depends(get_user_service_admin)
):
    return service.get_user(db, user_id)


# =====================================================
# DELETE USER
# =====================================================
@router.delete("/{user_id}")
def delete_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    admin=Depends(admin_required),
    service : UserServiceInterface = Depends(get_user_service_admin)
):
    service.delete_user(db, user_id)
    return {"message": "User deleted successfully"}