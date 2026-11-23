"""Producer RabbitMQ с синхронным фасадом для вызова из def-роутеров."""
import asyncio
import json
import logging
import threading
from datetime import datetime, timezone
from threading import Lock

import aio_pika

from app.config import settings

logger = logging.getLogger(__name__)


class _Publisher:
    def __init__(self) -> None:
        self._loop: asyncio.AbstractEventLoop | None = None
        self._connection: aio_pika.RobustConnection | None = None
        self._exchange: aio_pika.RobustExchange | None = None
        self._lock = Lock()
        self._started = False

    def start(self) -> None:
        with self._lock:
            if self._started:
                return
            self._loop = asyncio.new_event_loop()
            threading.Thread(target=self._loop.run_forever, daemon=True).start()
            fut = asyncio.run_coroutine_threadsafe(self._init(), self._loop)
            fut.result(timeout=5)
            self._started = True
            logger.info("API Service: producer RabbitMQ готов")

    async def _init(self) -> None:
        self._connection = await aio_pika.connect_robust(settings.rabbitmq_url)
        channel = await self._connection.channel()
        self._exchange = await channel.declare_exchange(
            settings.rabbitmq_exchange,
            aio_pika.ExchangeType.FANOUT,  # ← pub/sub из лекции
            durable=True,
        )

    def publish(self, event_type: str, payload: dict) -> None:
        if not self._started:
            self.start()
        message = {
            "event_type": event_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "payload": payload,
        }
        coro = self._exchange.publish(
            aio_pika.Message(
                body=json.dumps(message, ensure_ascii=False).encode(),
                content_type="application/json",
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,  # переживёт рестарт брокера
            ),
            routing_key="",  # для fanout не важен
        )
        fut = asyncio.run_coroutine_threadsafe(coro, self._loop)
        fut.result(timeout=settings.rabbitmq_publish_timeout)  # ждём ack БРОКЕРА
        logger.info("[PUBLISH] %s → %s", event_type, payload)

    def shutdown(self) -> None:
        if not self._started:
            return
        if self._connection:
            asyncio.run_coroutine_threadsafe(
                self._connection.close(), self._loop
            ).result(timeout=5)
        self._loop.call_soon_threadsafe(self._loop.stop)
        self._started = False


publisher = _Publisher()


def publish_event(event_type: str, payload: dict) -> None:
    """
    Публикует событие в брокер. Ошибки брокера НЕ ломают бизнес-операцию:
    заметка уже закоммичена в БД, уведомление — побочный эффект.
    """
    try:
        publisher.publish(event_type, payload)
    except Exception as e:
        logger.error("Не удалось опубликовать %s: %s", event_type, e)