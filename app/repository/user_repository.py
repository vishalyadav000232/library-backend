
from app.models.user import User
from typing import Optional, List, Tuple
from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from pydantic import EmailStr
from uuid import UUID



class UserRepositoryBase(ABC):

    @abstractmethod
    def get_users(
        self,
        db: Session,
        limit: int,
        offset: int,
        search: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> Tuple[List[User], int]:
        pass

    @abstractmethod
    def get_user_by_email(self, db: Session, email: EmailStr) -> Optional[User]:
        pass

    @abstractmethod
    def get_user_by_id(self, db: Session, user_id: UUID) -> Optional[User]:
        pass

    @abstractmethod
    def get_all_users(self, db: Session) -> List[User]:
        pass

    @abstractmethod
    def create(self, db: Session, user: User) -> User:
        pass

    @abstractmethod
    def delete_user(self, db: Session, user : User) -> bool:
        pass
    @abstractmethod
    def update_user(self, db: Session, user: User) -> User:
        pass


class UserRepository(UserRepositoryBase):

    def get_users(
        self,
        db: Session,
        limit: int,
        offset: int,
        search: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> Tuple[List[User], int]:

        query = db.query(User)

        if search:
            query = query.filter(User.name.ilike(f"%{search}%"))

        if is_active is not None:
            query = query.filter(User.is_active == is_active)

        total = query.count()

        users = query.offset(offset).limit(limit).all()

        return users, total

    def get_user_by_email(self, db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    def get_user_by_id(self, db: Session, user_id: UUID) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()

    def get_all_users(self, db: Session) -> List[User]:
        return db.query(User).all()

    def create(self, db: Session, user: User) -> User:
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def delete_user(self, db: Session, user: User) -> bool:
        if not user:
            return False

        db.delete(user)
        db.commit()
        return True
    
    def update_user(self, db: Session, user: User) -> User:
        db.add(user)          
        db.commit()           
        db.refresh(user)      
        return user