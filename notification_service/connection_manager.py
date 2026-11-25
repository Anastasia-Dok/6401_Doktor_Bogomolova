"""Реестр активных WS-подключений. Один пользователь = N сокетов (вкладки/устройства)."""
import logging
from collections import defaultdict
import pickle

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self) -> None:
        # user_id -> множество открытых сокетов этого пользователя.
        # defaultdict(set): при обращении к active[user_id] для ещё не
        # встречавшегося user_id автоматически создаётся пустое множество.
        self.active: dict[int, set] = defaultdict(set)

    def disconnect(self, user_id: int, ws) -> None:
        """Убрать сокет из реестра (безопасно вызывать повторно)."""
        # .discard() не бросает KeyError, если сокета там уже нет
        self.active[user_id].discard(ws)
        # Если у пользователя больше нет открытых сокетов — чистим ключ,
        # чтобы словарь не разрастался пустыми множествами.
        if not self.active[user_id]:
            self.active.pop(user_id, None)
        logger.info("[WS] user=%s отключён", user_id)
        
    async def send_to_user(self, user_id: int, message: dict) -> int:
        """Разослать сообщение во все открытые сокеты пользователя.

        Ошибка на одном сокете не должна ломать рассылку в остальные:
        неудачные сокеты просто выкидываем из реестра.
        """
        sockets = list(self.active.get(user_id, ()))
        if not sockets:
            return 0

        payload = pickle.dumps(message)
        sent_count = 0

        for ws in sockets:
            try:
                await ws.send(payload)
                sent_count += 1
            except Exception as e:
                logger.warning(" - Ошибка отправки =%s: %s", user_id, e)
                self.disconnect(user_id, ws)

        return sent_count
       

    @property
    def total_connections(self) -> int:
        return sum(len(s) for s in self.active.values())


manager = ConnectionManager()