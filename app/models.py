# models.py
from sqlalchemy import  Integer, String, Text, ForeignKey, Index #Импорт элементов SQLAlchemy, которые используются внутри колонок
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

#Создаём общий родительский класс Base для всех моделей. который наследует от DeclarativeBase
class Base(DeclarativeBase):
    pass

class Role(Base):
    # задающий имя таблицы (уникальный в рамках одного Base)
    __tablename__ = 'roles'
    #поле первичного ключа
                #Тип и параметры колонки
    role_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    #Поля, участвующие в механизме персистентности
    name: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)

    users: Mapped[list["User"]] = relationship(back_populates="role")
    #двусторонняя связь с атрибутом role в классе User. для автоматичиского обновления изменений.

    def __repr__(self) -> str:
        return f"Role(id={self.role_id!r}, name={self.name!r})"

   

class User(Base):
    __tablename__ = 'users'

    user_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable = False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str]= mapped_column(String(255), nullable=False)
    role_id: Mapped[int] = mapped_column( ForeignKey('roles.role_id'), nullable=False)

    # Индекс по факту для форейн кей
    __table_args__ = (
        Index('idx_users_role_id', 'role_id'),
    )

    
    role: Mapped["Role"] = relationship( back_populates="users")
    notes: Mapped[list["Note"]]= relationship(back_populates="user")

    subscriptions: Mapped[list['Subscription']] = relationship( back_populates="user")
    def __repr__(self) -> str:
        return f"User(id={self.user_id!r}, name={self.username!r}, email={self.email!r})"

class Lists(Base):
    __tablename__ = 'lists'

    list_id:Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str]= mapped_column(String(255), nullable=False)
   
    notes: Mapped[list["Note"]] = relationship(back_populates="list")
    subscriptions: Mapped[list['Subscription']] = relationship(back_populates="list")

    def __repr__(self) -> str:
        return f"Lists(id={self.list_id!r}, title={self.title!r})"

class Note(Base):
    __tablename__ = 'notes'

    note_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id:Mapped[int] = mapped_column(ForeignKey('users.user_id'), nullable=False)
    list_id: Mapped[int] = mapped_column(ForeignKey('lists.list_id'), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    author: Mapped[str] = mapped_column(String(255), nullable=False)
    review: Mapped[str] = mapped_column(Text, nullable=False)

    # Индексы
    __table_args__ = (
        Index('idx_notes_user_id', 'user_id'),
        Index('idx_notes_list_id', 'list_id'),
    )
    def __repr__(self) -> str:
        return f"Note(id={self.note_id!r}, title={self.title!r}, author={self.author!r}, review={self.review!r})"

    user: Mapped["User"] = relationship(back_populates="notes")
    list: Mapped['Lists'] = relationship(back_populates="notes")

class Subscription(Base):
    __tablename__ = 'subscriptions'

    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), primary_key=True)
    list_id: Mapped[int] = mapped_column (ForeignKey('lists.list_id'), primary_key=True)

    # Индексы
    __table_args__ = (
        Index('idx_subscriptions_user_id', 'user_id'),
        Index('idx_subscriptions_list_id', 'list_id'),
    )
    user: Mapped["User"] = relationship(back_populates="subscriptions")
    list: Mapped["Lists"] = relationship(back_populates="subscriptions")

    def __repr__(self) -> str:
        return f"Subscription(user_id={self.user_id!r}, list_id={self.list_id!r})"