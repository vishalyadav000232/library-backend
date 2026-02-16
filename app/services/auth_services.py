from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.repository.user_repository import   UserRepositoryBase
from app.schemas.user import UserCreate , LoginUser
from app.models.user import User
from abc import ABC , abstractmethod
from app.auth.interface.token_provider import TokenProvider as Token



from uuid import UUID
class UserServiceBase(ABC):

    @abstractmethod
    def create_user(self, db: Session, user_data: UserCreate):
        pass

    @abstractmethod
    def login_user(self , db :Session , user_data : LoginUser):
        pass
    @abstractmethod
    def delete_user(self , db : Session , user_id ):
        pass
    @abstractmethod
    def get_all_user(self , db : Session ):
        pass
    @abstractmethod
    def get_user_by_id( self , db : Session , user_id : UUID):
        pass
    @abstractmethod
    def change_status(self , db : Session , user_id : UUID):
        pass

class UserServices(UserServiceBase):

    def __init__(self, repo: UserRepositoryBase, token_provider: Token):
        self.repo = repo
        self.token_provider = token_provider

    def create_user(self, db: Session, user_data: UserCreate):

        if self.repo.get_user_by_email(db, user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email alredy register "
            )

        new_user = User(
            name=user_data.name,
            email=user_data.email,
            role=user_data.role,
        )

        new_user.set_password(user_data.password)

        return self.repo.create(db , new_user)
    
    def login_user(self , db :Session , user_data : LoginUser):
        user = self.repo.get_user_by_email(db , user_data.email)

        if not user or not user.verify_password(user_data.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Credential !"
            )
        
        token = self.token_provider.create_token(user.id , user.role)

        return {
            "message": "User Successfully Login",
            "access_token": token,
            "token_type": "bearer",
            "role": user.role
        }
    
    def delete_user(self , db : Session , user_id ):
        user = self.repo.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        self.repo.delete_user(db, user_id)
        return user
    
    
    def get_all_user(self, db):
        user = self.repo.get_all_users(db)
        
        if not user : 
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Not user"
            )
        return user
        
        
    def get_user_by_id( self , db : Session , user_id : UUID):
        user = self.repo.get_user_by_id(db , user_id)
        
        if not user :
             raise HTTPException(
                 status_code=status.HTTP_404_NOT_FOUND,
                 detail="user not found !"
             )
        return user
    
    
    def change_status(self , db : Session , user_id : UUID , is_active : bool):        
        user = self.repo.get_user_by_id(db , user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=" User not found !"
            )  
        
        user.is_active = is_active  
        db.commit()
        db.refresh(user)
        return user
