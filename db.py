# db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base


DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/rec_db"

#создаёт движок -  объект, который управляет подключением к базе данных.
#Создаёт пул соединений,Загружает драйвер
engine = create_engine(DATABASE_URL) 
               # создаёт новые сессии при каждом вызове
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Создает таблицы в базе данных"""
    
    Base.metadata.create_all(bind=engine)
    #для появления в бд  таблицы сущности
    #Через Base.metadata доступна вся информация о схеме (таблицы, колонки, связи, индексы)
    #SQLAlchemy проходит по всем моделям, зарегистрированным в Base.metadata 
     #(это Role, User, List, Note, Subscription).

def get_session():
    """Возвращает сессию для работы с БД"""
    #вызывает фабрику, создавая новый экземпляр сессии.
    return SessionLocal()