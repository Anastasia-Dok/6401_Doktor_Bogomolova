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
    stop = asyncio.Event() #создаем «флажок», который скажет consumer'у, когда пора остановиться.
    #Запускаем run_consumer как фоновую задачу.
    # create_task позволяет ей работать параллельно с основным приложением (приемом WebSocket'ов). 
    # Мы передаем ей stop, чтобы она знала, когда остановиться.
    task = asyncio.create_task(run_consumer(stop))
    logger.info("Notification Service запущен")
    try:
        yield #На yield функция lifespan приостанавливается и ждет сигнала на остановку
    finally: #этот блок выполнится только тогда, когда сервер будет останавливаться
        stop.set() #выставляем флажок stop. Consumer увидит это и корректно закроет соединение с RabbitMQ.
        await task #Ждем, пока consumer действительно завершит работу
        logger.info("Notification Service остановлен")


app = FastAPI(title="Notification Service", lifespan=lifespan)
#Создаем приложение FastAPI и привязываем к нему наш lifespan

@app.websocket("/ws") #Регистрируем эндпоинт /ws
#websocket — объект для общения с конкретным клиентом.
async def ws_endpoint(websocket: WebSocket):
    await websocket.accept() # ЭТАП 1: Соединение установлено (просто по порту)
    print("[WS] Клиент подключился.")
    
    user_id = None
    try:
        # ЭТАП 2: Получаем данные (ID пользователя)
        auth_message = await websocket.receive_text() #Ждем первое сообщение от клиента. 
        #Программа замирает, пока клиент не пришлет хоть какие-то данные 
        auth_data = json.loads(auth_message)
        user_id = auth_data.get("user_id")
        
        if not user_id:
            await websocket.close(code=1008)
            return

        # Регистрируем сокет в менеджере под этим ID
        #мы добавляем этот сокет в словарь manager.active под ключом user_id. Теперь, 
        #когда из RabbitMQ придет уведомление для этого пользователя,
        #manager найдет его сокет и отправит сообщение.
        manager.active[user_id].add(websocket)
        print(f"[WS] Пользователь {user_id} авторизован и готов получать уведомления.")

        # ЭТАП 3: Держим соединение открытым
        while True:
            await websocket.receive_text() # ждем пинги
    except WebSocketDisconnect: # Если клиент отключился, выбрасывается это исключение
        #Если user_id был известен (то есть клиент успел авторизоваться), удаляем его сокет из manager.active
        if user_id:
            manager.disconnect(user_id, websocket)
            print(f"[WS] Пользователь {user_id} отключился.")


@app.get("/health")
def health():
    return {"status": "ok", "connections": manager.total_connections} #с количеством активных подключений