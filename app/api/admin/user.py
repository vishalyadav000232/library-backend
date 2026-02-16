from fastapi import APIRouter , HTTPException , status , Depends
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.api.admin.admin_gaurd import admin_required
from app.api.dependency import get_user_service
from app.services.auth_services import UserServices
from app.schemas.user import UserResponse , UserCreate , UserUpdate
from typing import List
from uuid import UUID
router = APIRouter(prefix="/admin/users" , tags=["Admin Users"])


@router.get("/" , status_code=status.HTTP_200_OK , response_model=List[UserResponse])
def get_users(
    db : Session = Depends(get_db),
    admin = Depends(admin_required),
    user_service : UserServices = Depends(get_user_service)
):
    
    return  user_service.get_all_user(db=db)

@router.get("/{user_id}", response_model=UserResponse , status_code=status.HTTP_200_OK)
def get_user_by_id(
    user_id: UUID,
    db: Session = Depends(get_db),
    admin = Depends(admin_required),
    user_service: UserServices = Depends(get_user_service)
):
    return user_service.get_user_by_id(db, user_id)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    admin = Depends(admin_required),
    user_service: UserServices = Depends(get_user_service)
):
    return user_service.create_user(db, user_data)


@router.patch("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: UUID,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    admin = Depends(admin_required),
    user_service: UserServices = Depends(get_user_service)
):
    return user_service.update_user(db, user_id, user_data)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    admin = Depends(admin_required),
    user_service: UserServices = Depends(get_user_service)
):
    user_service.delete_user(db, user_id)
    return {
        "message" : "successfully deleted"
    }


@router.patch("/{user_id}/status", response_model=UserResponse)
def change_user_status(
    user_id: UUID,
    is_active: bool,
    db: Session = Depends(get_db),
    admin = Depends(admin_required),
    user_service: UserServices = Depends(get_user_service)
):
    return user_service.change_status(db, user_id, is_active)
