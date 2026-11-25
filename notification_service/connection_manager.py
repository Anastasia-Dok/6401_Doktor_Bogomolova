"""Реестр активных WS-подключений. Один пользователь = N сокетов (вкладки/устройства)."""
import logging
from collections import defaultdict
from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self) -> None:
        # создаем словарь active
        self.active: dict[int, set[WebSocket]] = defaultdict(set)
        #если мы обратимся к active[2], а пользователя 2 еще нет в словаре, 
        # Python автоматически создаст для него пустое множество set()

    def disconnect(self, user_id: int, ws: WebSocket) -> None:
        self.active[user_id].discard(ws) #.discard() не выбрасывает ошибку, если сокета там вдруг нет
        if not self.active[user_id]: #Если после удаления сокета множество стало пустым 
            self.active.pop(user_id, None)
        logger.info("[WS] user=%s отключён", user_id)

    async def send_to_user(self, user_id: int, message: dict) -> None:
        #Итерируемся по всем сокетам этого пользователя
        for ws in list(self.active.get(user_id, ())):
            try:
                await ws.send_json(message)  #Отправляем сообщение через конкретный сокет. 
                #send_json автоматически превращает словарь в JSON-строку и отправляет.
            except Exception as e:
                logger.warning("send user=%s: %s", user_id, e)
                self.disconnect(user_id, ws)

    @property #превращает метод в «свойство»
    #Складываем длины всех множеств (len(s)). 
    # Получаем общее количество открытых сокетов (не пользователей, а именно вкладок/устройств)
    def total_connections(self) -> int:
        return sum(len(s) for s in self.active.values())


manager = ConnectionManager()
'''Создаем единственный экземпляр класса (синглтон) на всё приложение. 
Когда main.py пишет from notification_service.connection_manager import manager, 
он получает именно этот объект. Это значит, что все модули (main.py, consumer.py) 
работают с одним и тем же словарем active. 
Именно поэтому consumer может найти сокеты, которые зарегистрировал main.py.'''