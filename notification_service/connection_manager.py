"""Реестр активных WS-подключений. Один пользователь = N сокетов (вкладки/устройства)."""
import logging
from collections import defaultdict
from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self) -> None:
        self.active: dict[int, set[WebSocket]] = defaultdict(set)

    def disconnect(self, user_id: int, ws: WebSocket) -> None:
        self.active[user_id].discard(ws) #Закрываем соединение (как remote)
        if not self.active[user_id]: #Если у пользователя не осталось сокетов, то удаляем ключ целиком
            self.active.pop(user_id, None)
        logger.info("[WS] user=%s отключён", user_id)

    async def send_to_user(self, user_id: int, message: dict) -> None: #dict в  json и отправляем на каждый сокет пользователя
        for ws in list(self.active.get(user_id, ())):
            try:
                await ws.send_json(message)
            except Exception as e:
                logger.warning("send user=%s: %s", user_id, e)
                self.disconnect(user_id, ws)

    async def broadcast(self, message: dict) -> None: #Рассылка всем пользователям
        for user_id in list(self.active.keys()):
            await self.send_to_user(user_id, message)

    @property
    def total_connections(self) -> int:
        return sum(len(s) for s in self.active.values())


manager = ConnectionManager()