"""Notification Service: FastAPI + WebSocket + consumer."""
import asyncio
import pickle
import logging

import websockets
from websockets.exceptions import ConnectionClosed

from notification_service.config import settings
from notification_service.connection_manager import manager
from notification_service.consumer import run_consumer

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)



async def ws_handler(websocket) -> None:
    """Обработчик одного WS-подключения.
    Путь (например, /ws) библиотека не проверяет, хендлер зовётся
    для любого пути.
    """
    peer = getattr(websocket, "remote_address", "?")
    logger.info("[WS] Клиент подключился: %s", peer)

    user_id = None
    try:
        #  ждём первое сообщение — JSON с user_id
        auth_message = await websocket.recv()
        auth_data = pickle.loads(auth_message)
        user_id = auth_data.get("user_id")

        if not user_id:
            await websocket.close(code=1008, reason="user_id required")
            return

        # Регистрируем сокет в общем реестре под этим ID
        manager.active[user_id].add(websocket)
        logger.info(
            "[WS] Пользователь %s авторизован и готов получать уведомления.",
            user_id,
        )

        # ЭТАП 3: держим соединение открытым, читаем всё, что шлёт клиент
        async for _ in websocket:
            pass  # клиент может слать пинги — нам всё равно

    except ConnectionClosed:
        pass
    except pickle.UnpicklingError as e:
        logger.warning("[WS] некорректный PICKLE от %s: %s", peer, e)
    finally:
        if user_id:
            manager.disconnect(user_id, websocket)
            logger.info("[WS] Пользователь %s отключился.", user_id)

async def main() -> None:
    #асинхронный «флажок» остановки stop
    stop = asyncio.Event()

    # Consumer RabbitMQ — фоновая задача
    consumer_task = asyncio.create_task(run_consumer(stop))

    # Собственно WS-сервер
    server = await websockets.serve(
        ws_handler,
        settings.ws_host,
        settings.ws_port,
    )
    logger.info(
        "Notification Service запущен: WS на ws://%s:%s",
        settings.ws_host,
        settings.ws_port,
    )

    try:
        await asyncio.Future()  # крутимся вечно
    finally:
        stop.set()
        try:
            await consumer_task 
            #дожидаемся, пока consumer отпишется от очереди и закроет соединение с RabbitMQ
        except asyncio.CancelledError:
            pass
        server.close() 
        await server.wait_closed()
        logger.info("Notification Service остановлен")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[NOTIFICATION] Остановлено")