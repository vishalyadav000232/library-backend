from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import api_router
from app.database.db import Base, engine
from app.models.user import User
from app.models.seats import Seat


def create_app() -> FastAPI:
    app = FastAPI(title="Yadav Ji Library API")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",
            "http://localhost:3000",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router, prefix="/api/v1")

    @app.on_event("startup")
    def startup():
        Base.metadata.create_all(bind=engine)

    @app.get("/")
    def root():
        return {"message": "Yadav Ji Library Backend Running"}

    return app


app = create_app()
