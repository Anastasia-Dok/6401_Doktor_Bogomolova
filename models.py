# models.py
from sqlalchemy import  Integer, String, Text, ForeignKey, Index #Импорт элементов SQLAlchemy, которые используются внутри колонок
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

#Создаём общий родительский класс Base для всех моделей.
class Base(DeclarativeBase):
    pass

class Role(Base):
    __tablename__ = 'roles'
    
    role_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)

    users: Mapped[list["User"]] = relationship(back_populates="role")
    #двусторонняя связь с атрибутом role в классе User

   

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
    lists: Mapped[list['List']] = relationship(back_populates="creator")
    notes: Mapped[list["Note"]]= relationship(back_populates="user")

    subscriptions: Mapped[list['Subscription']] = relationship( back_populates="user")
    def __repr__(self) -> str:
        return f"User(id={self.user_id!r}, name={self.username!r}, email={self.email!r})"

class List(Base):
    __tablename__ = 'lists'

    list_id:Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str]= mapped_column(String(255), nullable=False)
   
    notes: Mapped[list["Note"]] = relationship(back_populates="list")
    subscriptions: Mapped[List['Subscription']] = relationship(back_populates="list")

class Note(Base):
    __tablename__ = 'notes'

    note_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id:Mapped[int] = mapped_column(ForeignKey('users.user_id'), nullable=False)
    list_id: Mapped[int] = mapped_column(ForeignKey('lists.list_id'), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    author: Mapped[str] = mapped_column(String(255), nullable=False)
    review: Mapped[str] = mapped_column(Text, nullable=True)

    # Индексы
    __table_args__ = (
        Index('idx_notes_user_id', 'user_id'),
        Index('idx_notes_list_id', 'list_id'),
    )
    def __repr__(self) -> str:
        return f"Note(id={self.note_id!r}, title={self.title!r}, author={self.author!r})"

    user: Mapped["User"] = relationship(back_populates="notes")
    list: Mapped['List'] = relationship(back_populates="notes")

class Subscription(Base):
    __tablename__ = 'subscriptions'

    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), primary_key=True)
    list_id: Mapped[int] = mapped_column ( ForeignKey('lists.list_id'), primary_key=True)

    # Индексы
    __table_args__ = (
        Index('idx_subscriptions_user_id', 'user_id'),
        Index('idx_subscriptions_list_id', 'list_id'),
    )

    user: Mapped["User"] = relationship(back_populates="subscriptions")
    list: Mapped["List"] = relationship(back_populates="subscriptions")