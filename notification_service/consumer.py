"""Consumer RabbitMQ: получает события и рассылает подписчикам."""
import asyncio
import pickle
import logging
from sqlalchemy import select

import aio_pika

from notification_service.config import settings
from notification_service.connection_manager import manager


logger = logging.getLogger(__name__)


def _format_note_created(event: dict) -> dict:
    p = event.get("payload", {})
    text = f"В списке #{p.get('list_id')} новая заметка: «{p.get('title')}» (автор: {p.get('username')})"
    return {
        "type": "notification",
        "event": "note.created",
        "text": text,
        "timestamp": event.get("timestamp"),
        "meta": p,
    }


def _format_subscription_created(event: dict) -> dict:
    p = event.get("payload", {})
    text = f"Вы успешно подписались на список #{p.get('list_id')}"
    return {
        "type": "notification",
        "event": "subscription.created",
        "text": text,
        "timestamp": event.get("timestamp"),
        "meta": p,
    }

#Она вызывается каждый раз, когда в RabbitMQ приходит новое сообщение
async def _handle(message: aio_pika.abc.AbstractIncomingMessage) -> None:
    async with message.process():  # ack/nack
        try:
            event = pickle.loads(message.body)
        except pickle.UnpicklingError:
            logger.error("Невалидный PICKLE: %r", message.body[:200])
            return

        etype = event.get("event_type")
        payload = event.get("payload", {})

        
        #  СОБЫТИЕ: ПОДПИСКА НА СПИСОК
        
        if etype == "subscription.created":
            user_id = payload.get("user_id")
            if not user_id:
                return
            
            logger.info("[CONSUME] subscription.created (user_id=%s, list_id=%s)", user_id, payload.get("list_id"))
            
            notification = _format_subscription_created(event)
            # Отправляем ТОЛЬКО тому, кто подписался
            await manager.send_to_user(user_id, notification)
            logger.info("  - Отправлено подтверждение пользователю user_id=%s", user_id)

        
        #  СОБЫТИЕ: НОВАЯ ЗАМЕТКА В СПИСКЕ
        
        elif etype == "note.created":
            subscribers = payload.get("subscribers", [])
            author_id = payload.get("user_id")
            notification = _format_note_created(event)
            
            for sub_id in subscribers:
                if sub_id == author_id:
                    continue

                sent = await manager.send_to_user(sub_id, notification)
                if sent:
                    logger.info("  - Доставлено user_id=%s (сокетов: %d)", sub_id, sent)
                else:
                    logger.info("  - user_id=%s оффлайн (уведомление не получено клиентом)", sub_id)

async def run_consumer(stop_event: asyncio.Event) -> None:
     #подключаемся к RabbitMQ с авто-переподключением при обрыве
    connection = await aio_pika.connect_robust(settings.rabbitmq_url)
    # открываем канал (легкий виртуальный «сокет» внутри TCP-соединения).
    channel = await connection.channel()
    #не больше 10 сообщ за раз
    await channel.set_qos(prefetch_count=10)
    #Объявляем exchange типа FANOUT (рассылка всем очередям, привязанным к нему).
    #  durable=True — exchange переживет рестарт RabbitMQ.
    exchange = await channel.declare_exchange(
        settings.rabbitmq_exchange, aio_pika.ExchangeType.FANOUT, durable=True
    )
    queue = await channel.declare_queue(settings.rabbitmq_queue, durable=True)
    await queue.bind(exchange) #привязываем очередь к exchange

    logger.info("Notification Service слушает очередь %r", settings.rabbitmq_queue)
    # регистрируем нашу функцию _handle как обработчик 
    # Теперь каждое новое сообщение в очереди будет вызывать _handle
    tag = await queue.consume(_handle) #ждем, пока не будет установлен флажок остановки
    try:
        await stop_event.wait()
    finally:
        #гарантирует, что мы корректно отменим consumer (queue.cancel) 
        # и закроем соединение с RabbitMQ (connection.close())
        await queue.cancel(tag)
        await connection.close()
        logger.info("Consumer RabbitMQ остановлен")