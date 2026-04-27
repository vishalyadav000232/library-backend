

from fastapi import APIRouter, WebSocket
from app.websockets.manger import manager

router = APIRouter()

@router.websocket("/ws/admin")
async def admin_dashboard_socket(websocket: WebSocket):
    await manager.connect(websocket)

    try:
        while True:
            await websocket.receive_text()

    except:
        manager.disconnect(websocket)