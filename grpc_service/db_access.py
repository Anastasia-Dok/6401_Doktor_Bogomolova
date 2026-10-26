"""Функции работы с БД для gRPC-сервиса."""
import sys
from pathlib import Path

# Чтобы импорт `app.*` работал при запуске `python -m grpc_service.server`
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import func, select, desc

from app.db import SessionLocal
from app.models import User, Lists, Note, Subscription


def get_summary_data() -> dict:
    with SessionLocal() as session:
        return {
            "users": session.scalar(select(func.count()).select_from(User)),
            "lists": session.scalar(select(func.count()).select_from(Lists)),
            "notes": session.scalar(select(func.count()).select_from(Note)),
            "subscriptions": session.scalar(select(func.count()).select_from(Subscription)),
        }


def get_top_lists_data(limit: int) -> list[dict]:
    with SessionLocal() as session:
        stmt = (
            select(
                Lists.list_id,
                Lists.title,
                func.count(func.distinct(Note.note_id)).label("notes_count"),
                func.count(func.distinct(Subscription.user_id)).label("subscribers_count"),
            )
            .outerjoin(Note, Note.list_id == Lists.list_id)
            .outerjoin(Subscription, Subscription.list_id == Lists.list_id)
            .group_by(Lists.list_id, Lists.title)
            .order_by(desc("notes_count"))
            .limit(limit)
        )
        return [
            {
                "list_id": r.list_id,
                "title": r.title,
                "notes_count": r.notes_count,
                "subscribers_count": r.subscribers_count,
            }
            for r in session.execute(stmt)
        ]


def get_top_users_data(limit: int) -> list[dict]:
    with SessionLocal() as session:
        stmt = (
            select(
                User.user_id,
                User.username,
                User.email,
                func.count(Note.note_id).label("notes_count"),
            )
            .outerjoin(Note, Note.user_id == User.user_id)
            .group_by(User.user_id, User.username, User.email)
            .order_by(desc("notes_count"))
            .limit(limit)
        )
        return [
            {
                "user_id": r.user_id,
                "username": r.username,
                "email": r.email,
                "notes_count": r.notes_count,
            }
            for r in session.execute(stmt)
        ]


def get_top_authors_data(limit: int) -> list[dict]:
    with SessionLocal() as session:
        stmt = (
            select(Note.author, func.count(Note.note_id).label("mentions"))
            .group_by(Note.author)
            .order_by(desc("mentions"))
            .limit(limit)
        )
        return [{"author": r.author, "mentions": r.mentions} for r in session.execute(stmt)]