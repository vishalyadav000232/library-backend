
import logging
from fastapi import APIRouter, WebSocket
from app.websockets.manger import manager


logger = logging.getLogger(__name__)

router = APIRouter()

@router.websocket("/ws/admin")
async def admin_dashboard_socket(websocket: WebSocket):
    await manager.connect(websocket)
    logger.info(
        "Websocket connected successfully "
    )

    try:
        while True:
            await websocket.receive_text()

    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)