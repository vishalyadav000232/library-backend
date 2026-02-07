

from typing import Optional
from abc import ABC , abstractmethod
from uuid import UUID


class TokenProvider(ABC):

    
    @abstractmethod
    def create_token(user_id : UUID , role : str)-> str :
        pass


    @abstractmethod
    def verify_token(self , token : str) -> Optional[dict] | None:
        pass