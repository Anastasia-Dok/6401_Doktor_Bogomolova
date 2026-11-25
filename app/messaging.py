"""Producer RabbitMQ с синхронным фасадом для вызова из def-роутеров."""
import asyncio
import pickle
import logging
import threading
from datetime import datetime, timezone
from threading import Lock

import aio_pika

from app.config import settings

logger = logging.getLogger(__name__)


class _Publisher: #не для импорта напрямую
    def __init__(self) -> None:
        self._loop: asyncio.AbstractEventLoop | None = None # отдельный цикл событий (asyncio loop), который будет работать в фон
        self._connection: aio_pika.RobustConnection | None = None #TCP-соединение с RabbitMQ.
        self._exchange: aio_pika.RobustExchange | None = None #бъект exchange (обменника) для публикации.
        self._lock = Lock() #замок» для потокобезопасности
        self._started = False #флаг (True/False), запущен ли уже публикатор.

    def start(self) -> None:
        with self._lock:
            if self._started:
                return
            self._loop = asyncio.new_event_loop() #Создаем новый цикл событий (отдельный от FastAPI)
            #Запускаем его в фоновом потоке. daemon=True значит, что поток закроется вместе с программой, 
            # даже если что-то зависнет. 
            # run_forever — бесконечный цикл, который крутит задачи asyncio.
            threading.Thread(target=self._loop.run_forever, daemon=True).start()
            #Отправляем асинхронную корутину _init() в фоновый поток. 
            # run_coroutine_threadsafe — это мост: запускает асинхронную функцию в другом потоке и возвращает Future (обещание результата).
            fut = asyncio.run_coroutine_threadsafe(self._init(), self._loop)
            #дем (синхронно!), пока _init() завершится. 
            # Таймаут — 5 секунд. Если брокер недоступен — будет ошибка
            fut.result(timeout=5)
            self._started = True
            logger.info("API Service: producer RabbitMQ готов")

    async def _init(self) -> None: # Асинхронная функция, которая выполняется в фоновом потоке
        # подключаемся к RabbitMQ. «Robust»  при обрыве связи библиотека сама попытается переподключиться
        self._connection = await aio_pika.connect_robust(settings.rabbitmq_url)
        channel = await self._connection.channel()
        #Объявляем exchange типа FANOUT (все очереди, привязанные к нему, получат копию сообщения). 
        # durable=True — exchange переживет рестарт RabbitMQ.
        self._exchange = await channel.declare_exchange(
            settings.rabbitmq_exchange,
            aio_pika.ExchangeType.FANOUT,  
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
        #Готовим корутину для публикации
        coro = self._exchange.publish(
            aio_pika.Message(
                body=pickle.dumps(message),
                content_type="application/python-pickle",
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,  # переживёт рестарт брокера
            ),
            routing_key="",  # для fanout не важен
        )
        fut = asyncio.run_coroutine_threadsafe(coro, self._loop) # Отправляем корутину в фоновый поток
        fut.result(timeout=settings.rabbitmq_publish_timeout)  # ждём ack БРОКЕРА
        logger.info("[PUBLISH] %s → %s", event_type, payload)

    def shutdown(self) -> None:
        if not self._started:
            return
        if self._connection: #Закрываем соединение с RabbitMQ 
            asyncio.run_coroutine_threadsafe(
                self._connection.close(), self._loop
            ).result(timeout=5)
        self._loop.call_soon_threadsafe(self._loop.stop) #Останавливаем event loop
        self._started = False

#Создаем единственный экземпляр класса. 
# Теперь любой модуль может импортировать publisher и вызывать publisher.start() / publisher.shutdown()
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