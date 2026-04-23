from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import api_router
from app.middleware.token_middleware import TokenMiddleware
from app.auth.provider.token_provider import JWTTokenProvider
from app.repository.user_repository import UserRepository
from app.services.auth_services import UserServices
from app.repository.refresh_token_repository import RefreshTokenRepository
from app.services.refres_token_service import RefreshTokenService


def create_app() -> FastAPI:
    
    
    app = FastAPI(title=" Library Management API" , description="API for managing library operations, including user authentication, book management, and seat reservations.", version="1.0.0" , contact={
        "name": "Vishal Yadav",
        "email": "vishalyadav000232@gmail.com"
    }  , license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    })
    

    app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173"],  # keep only this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

    app.state.token_provider = JWTTokenProvider()
    app.state.user_service = UserServices(
        repo=UserRepository(),
        token_provider=app.state.token_provider
    )
    app.state.refresh_service = RefreshTokenService(
        repo=RefreshTokenRepository(),
        token_provider=app.state.token_provider
    )

    app.add_middleware(TokenMiddleware)

    app.include_router(api_router, prefix="/api/v1")

    @app.on_event("startup")
    def startup():
        pass

    @app.get("/")
    def root():
        return {"message": "Yadav Ji Library Backend Running"}

    return app


app = create_app()
