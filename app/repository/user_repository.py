from sqlalchemy.orm import Session
from app.models.user import User
from pydantic import EmailStr
from uuid import UUID
from typing import Optional
from abc import ABC , abstractmethod

class UserRepositoryBase(ABC):
    @abstractmethod
    def get_user_by_email(self , db : Session , email :EmailStr ) -> Optional[User]:
        pass

    @abstractmethod
    def get_user_by_id(self , db : Session , userId : UUID)-> Optional[User]:
        pass

    @abstractmethod
    def get_all_users(self , db : Session):
        pass
    
    @abstractmethod
    def create(self , db:Session , user: User):
        pass

    def delete_user(self , db : Session , user_id):
        pass    


class UserRepository(UserRepositoryBase):
    
    def get_user_by_email(self , db : Session , email :EmailStr ) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()
    

    def get_user_by_id(self , db : Session , userId : UUID)-> Optional[User]:
        return db.query(User).filter(User.id == userId).first()
    

    def get_all_users(self , db : Session):
        return db.query(User).all()
    
    
    def create(self , db:Session , user: User):
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    def delete_user(self , db : Session , user_id):
        user = self.get_user_by_id(db , user_id)
        if user:
            db.delete(user)
            db.commit()
            return True
        return False