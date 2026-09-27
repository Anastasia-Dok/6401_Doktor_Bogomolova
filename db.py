# db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

# Замените данные на свои
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/rec_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Создает таблицы в базе данных"""
    Base.metadata.create_all(bind=engine)

def get_session():
    """Возвращает сессию для работы с БД"""
    return SessionLocal()