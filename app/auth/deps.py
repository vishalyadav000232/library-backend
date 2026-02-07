from app.auth.provider.token_provider import JWTTokenProvider
from app.repository.user_repository import UserRepository


def get_token_provider():
    return JWTTokenProvider()


def get_user_repository():
    return UserRepository()
