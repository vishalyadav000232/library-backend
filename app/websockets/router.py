import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.websockets.manger import manager

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/ws/admin")
async def admin_dashboard_socket(websocket: WebSocket):
    await manager.connect(websocket)
    logger.info("Admin WebSocket connected successfully")

    try:
        while True:
            await websocket.receive_text()

    except WebSocketDisconnect as e:
        logger.info("Admin WebSocket disconnected. code=%s", e.code)

    except Exception as e:
        logger.warning("Unexpected WebSocket error: %s", e)

    finally:
        manager.disconnect(websocket)