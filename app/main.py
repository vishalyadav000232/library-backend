import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.auth.provider.token_provider import JWTTokenProvider
from app.core.exception.handlers import register_exception_handlers
from app.middleware.token_middleware import TokenMiddleware
from app.repository.refresh_token_repository import RefreshTokenRepository
from app.repository.user_repository import UserRepository
from app.services.auth_services import UserServices
from app.services.refres_token_service import RefreshTokenService
from app.core.logging import   configure_logging



configure_logging()

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        logger.info("Initializing StudySphere API...")

        app.state.token_provider = JWTTokenProvider()

        app.state.user_service = UserServices(
            repo=UserRepository(),
            token_provider=app.state.token_provider,
        )

        app.state.refresh_service = RefreshTokenService(
            repo=RefreshTokenRepository(),
            token_provider=app.state.token_provider,
        )

        logger.info("StudySphere API initialized successfully.")

        yield

    except Exception:
        logger.exception("StudySphere API startup failed.")
        raise

    finally:
        logger.info("StudySphere API shutdown completed.")


def create_app() -> FastAPI:
    app = FastAPI(
        title="StudySphere API",
        description=(
            "API for smart library seat booking, user authentication, "
            "payments, book management, and seat reservations."
        ),
        version="1.0.0",
        contact={
            "name": "Vishal Yadav",
            "email": "vishalyadav000232@gmail.com",
        },
        license_info={
            "name": "MIT License",
            "url": "https://opensource.org/licenses/MIT",
        },
        lifespan=lifespan,
    )

    register_exception_handlers(app)

    app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173",
        "http://127.0.0.1:5153",
        "http://localhost:5153",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

    app.add_middleware(TokenMiddleware)

    app.include_router(api_router)

    @app.get("/", tags=["Health"])
    async def root():
        return {
            "success": True,
            "message": "StudySphere API is running",
            "version": "1.0.0",
        }

    return app


app = create_app()