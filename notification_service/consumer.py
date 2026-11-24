"""Consumer RabbitMQ: получает события и рассылает подписчикам."""
import asyncio
import json
import logging
from sqlalchemy import select

import aio_pika

from notification_service.config import settings
from notification_service.connection_manager import manager
from app.db import SessionLocal
from app.models import Subscription

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


async def _handle(message: aio_pika.abc.AbstractIncomingMessage) -> None:
    async with message.process():  # ack/nack
        try:
            event = json.loads(message.body)
        except json.JSONDecodeError:
            logger.error("Невалидный JSON: %r", message.body[:200])
            return

        etype = event.get("event_type")
        payload = event.get("payload", {})

        # ==========================================
        # 1. СОБЫТИЕ: ПОДПИСКА НА СПИСОК
        # ==========================================
        if etype == "subscription.created":
            user_id = payload.get("user_id")
            if not user_id:
                return
            
            logger.info("[CONSUME] subscription.created (user_id=%s, list_id=%s)", user_id, payload.get("list_id"))
            
            notification = _format_subscription_created(event)
            # Отправляем ТОЛЬКО тому, кто подписался
            await manager.send_to_user(user_id, notification)
            logger.info("  └─ Отправлено подтверждение пользователю user_id=%s", user_id)

        # ==========================================
        # 2. СОБЫТИЕ: НОВАЯ ЗАМЕТКА В СПИСКЕ
        # ==========================================
        elif etype == "note.created":
            list_id = payload.get("list_id")
            author_id = payload.get("user_id")
            if not list_id:
                return

            logger.info("[CONSUME] note.created для списка #%s", list_id)

            # Ищем всех подписчиков списка в БД
            def get_subscribers():
                with SessionLocal() as session:
                    stmt = select(Subscription.user_id).where(Subscription.list_id == list_id)
                    return [row[0] for row in session.execute(stmt)]

            subscribers = await asyncio.to_thread(get_subscribers)
            
            if not subscribers:
                logger.info("Нет подписчиков для списка #%s.", list_id)
                return

            notification = _format_note_created(event)
            
            # Отправляем всем подписчикам
            for sub_id in subscribers:
                # (Опционально) не отправляем уведомление автору заметки
                if sub_id == author_id:
                    continue 
                    
                await manager.send_to_user(sub_id, notification)
                logger.info("  └─ Отправлено user_id=%s", sub_id)


async def run_consumer(stop_event: asyncio.Event) -> None:
    connection = await aio_pika.connect_robust(settings.rabbitmq_url)
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=10)

    exchange = await channel.declare_exchange(
        settings.rabbitmq_exchange, aio_pika.ExchangeType.FANOUT, durable=True
    )
    queue = await channel.declare_queue(settings.rabbitmq_queue, durable=True)
    await queue.bind(exchange)

    logger.info("Notification Service слушает очередь %r", settings.rabbitmq_queue)
    tag = await queue.consume(_handle)
    try:
        await stop_event.wait()
    finally:
        await queue.cancel(tag)
        await connection.close()
        logger.info("Consumer RabbitMQ остановлен")