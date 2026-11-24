"""Notification Service: FastAPI + WebSocket + consumer."""
import asyncio
import logging
from contextlib import asynccontextmanager
import  json

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from notification_service.connection_manager import manager
from notification_service.consumer import run_consumer

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    stop = asyncio.Event()
    task = asyncio.create_task(run_consumer(stop))
    logger.info("Notification Service запущен")
    try:
        yield
    finally:
        stop.set()
        await task
        logger.info("Notification Service остановлен")


app = FastAPI(title="Notification Service", lifespan=lifespan)


@app.websocket("/ws")
async def ws_endpoint(websocket: WebSocket):
    await websocket.accept() # ЭТАП 1: Соединение установлено (просто по порту)
    print("[WS] Клиент подключился.")
    
    user_id = None
    try:
        # ЭТАП 2: Получаем данные (ID пользователя)
        auth_message = await websocket.receive_text()
        auth_data = json.loads(auth_message)
        user_id = auth_data.get("user_id")
        
        if not user_id:
            await websocket.close(code=1008)
            return

        # Регистрируем сокет в менеджере под этим ID
        manager.active[user_id].add(websocket)
        print(f"[WS] Пользователь {user_id} авторизован и готов получать уведомления.")

        # ЭТАП 3: Держим соединение открытым
        while True:
            await websocket.receive_text() # ждем пинги
    except WebSocketDisconnect:
        if user_id:
            manager.disconnect(user_id, websocket)
            print(f"[WS] Пользователь {user_id} отключился.")


@app.get("/health")
def health():
    return {"status": "ok", "connections": manager.total_connections}