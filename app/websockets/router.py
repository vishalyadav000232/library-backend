import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, status
from app.websockets.manger import manager


logger = logging.getLogger(__name__)

router = APIRouter()

@router.websocket("/ws/admin")
async def admin_dashboard_socket(websocket: WebSocket, token: str | None = Query(default=None)):
    token_provider = getattr(websocket.app.state, "token_provider", None)

    if not token or token_provider is None:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Missing token")
        return

    try:
        payload = token_provider.verify_token(token)
    except Exception:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid or expired token")
        return

    if payload.get("role", "").lower() != "admin":
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Admin access required")
        return

    await manager.connect(websocket)
    logger.info(f"Admin websocket connected: user_id={payload.get('sub')}")

    try:
        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info(f"Admin websocket disconnected: user_id={payload.get('sub')}")

    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)