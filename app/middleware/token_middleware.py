from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session
from uuid import UUID
from app.database.db import SessionLocal

class TokenMiddleware(BaseHTTPMiddleware):
    

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        refresh_token = request.cookies.get("refresh_token")
        if not refresh_token:
            return response

        try:
            token_provider = getattr(self.app.state, "token_provider", None)
            refresh_service = getattr(self.app.state, "refresh_service", None)
            user_service = getattr(self.app.state, "user_service", None)

            if not all([token_provider, refresh_service, user_service]):
                return response

            db: Session = SessionLocal()
            try:
                payload = token_provider.verify_refresh_token(refresh_token)
                user_id = UUID(payload["sub"])
                user = user_service.get_user_by_id(db, user_id)

                if user:
                    # 4️⃣ Rotate the token
                    _, new_refresh_token = refresh_service.rotate(
                        db, refresh_token, user
                    )
                    # 5️⃣ Attach new refresh_token cookie
                    response.set_cookie(
                        key="refresh_token",
                        value=new_refresh_token,
                        httponly=True,
                        secure=True,
                        samesite="none",
                        path="/",
                        max_age=60*60*24*7
                    )
            finally:
                db.close()

        except Exception as e:
            pass

        return response