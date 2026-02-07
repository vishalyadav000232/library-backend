from jose import jwt, JWTError
import os
from typing import Optional
from datetime import datetime, time, timedelta, timezone
from dotenv import load_dotenv
from fastapi import HTTPException, status
from uuid import UUID


load_dotenv()



class TokenService():
    def __init__(self):
        self.SECRET_KEY = os.getenv("SECRET_KEY")
        if not self.SECRET_KEY:
            raise RuntimeError("SECRET_KEY not set")
        self.ALGORITHM = 'HS256'
        self.EXPIRY  = 6 # IN HOURS 


    def create_token(self , user_id : UUID , role :str ):
        payload = {
            "sub" : str(user_id),
            "role" : role,
            "exp" : datetime.now(timezone.utc)+timedelta(hours=self.EXPIRY)

        }

        token = jwt.encode(payload , self.SECRET_KEY , algorithm=self.ALGORITHM)
        return token
    

    def verify_token(self , token : str) -> Optional[dict] | None:
        try:
            payload = jwt.decode(token , self.SECRET_KEY , algorithms=[self.ALGORITHM])
            return payload
        except JWTError:
            raise HTTPException(
                status_code = status.HTTP_401_UNAUTHORIZED,
                detail = "Invalid token"
            )
            return None
    
    
  

