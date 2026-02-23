from typing import Optional
from abc import ABC, abstractmethod
from uuid import UUID


class TokenProvider(ABC):

    # =========================
    # CREATE ACCESS TOKEN
    # =========================
    @abstractmethod
    def create_access_token(self, user_id: UUID, role: str) -> str:
        pass

    # =========================
    # CREATE REFRESH TOKEN
    # =========================
    @abstractmethod
    def create_refresh_token(self, user_id: UUID, role: Optional[str] = None) -> str:
        pass

    # =========================
    # VERIFY ACCESS TOKEN
    # =========================
    @abstractmethod
    def verify_token(self, token: str) -> dict:
        pass

    # =========================
    # VERIFY REFRESH TOKEN
    # =========================
    @abstractmethod
    def verify_refresh_token(self, token: str) -> dict:
        pass