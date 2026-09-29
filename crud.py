
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload, joinedload
from db import engine
from models import Base, Role, User, Lists, Note, Subscription
from security import hash_password


# ---------- CRUD для Role ----------
def create_role(name: str) -> Role:
    with Session(engine) as session: # открыть сессию
        role = Role(name=name)# Transient - объект в памяти
        session.add(role)#добавить объект в Session (пометить на добавление в БД).
        #Pending — сессия знает о нём
        # Persistent
        session.commit()#завершает текущую транзакцию, делая все изменения постоянными
        session.refresh(role) #заново загрузить объект из БД       
        return role # объект Detached, но с данными

def get_role(role_id: int) -> Role | None:
    with Session(engine) as session:
        return session.get(Role, role_id) 
    #Сначала смотрит в identity map (кэш сессии). Если объект с этим PK уже загружен — вернёт его без SQL.
    #Если нет — генерирует 
    #объект Detached после return
    #получить объект по значению первичного ключа

def update_role(role_id: int, new_name: str) -> Role | None:
    with Session(engine) as session:
        role = session.get(Role, role_id)  # загрузили Persistent-объект
        if role:
            role.name = new_name
            #завершает текущую транзакцию, делая все изменения постоянными
            session.commit()
            session.refresh(role)
        return role

def delete_role(role_id: int) -> bool:
    with Session(engine) as session:
        role = session.get(Role, role_id)
        if role:
            session.delete(role)#пометить объект на удаление
            #завершает текущую транзакцию, делая все изменения постоянными
            session.commit()
            return True
        return False

def get_all_users_with_role() -> list[User]:
    """Все пользователи с ролями """
    with Session(engine) as session:
                                # жадная загрузка: 
                                # сразу подтянуть связанные роли одним JOIN-запросом
        stmt = select(User).options(joinedload(User.role)).order_by(User.user_id)
        return list(session.scalars(stmt).all()) #выполняет запрос, возвращает объекты User

# ---------- CRUD для User ----------
def create_user(username: str, email: str, password: str, role_id: int) -> User:
    with Session(engine) as session:
        user = User(
            username=username,
            email=email,
            password_hash=hash_password(password),
            role_id=role_id
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return user

def get_user_by_id(user_id: int) -> User | None:
    with Session(engine) as session:
        return session.get(User, user_id) # если после return обратиться к user.role, будет DetachedInstanceError


def get_user_by_email(email: str) -> User | None:
    with Session(engine) as session:
        stmt = (
            select(User)
            .where(User.email == email)
            .options(joinedload(User.role))
        )
        return session.scalars(stmt).first()


def get_user_by_username(username: str) -> User | None:
    with Session(engine) as session:
        stmt = (
            select(User)
            .where(User.username == username)
            .options(joinedload(User.role))
        )
        return session.scalars(stmt).first()

def update_user(user_id: int, **kwargs) -> User | None:
    with Session(engine) as session:
        user = session.get(User, user_id)
        if user:
            for key, value in kwargs.items():
                setattr(user, key, value)
            session.commit()
            session.refresh(user)
        return user

def delete_user(user_id: int) -> bool:
    with Session(engine) as session:
        user = session.get(User, user_id)
        if user:
            session.delete(user)
            session.commit()
            return True
        return False

# ---------- CRUD для Lists ----------
def create_list(title: str) -> Lists:
    with Session(engine) as session:
        lst = Lists(title=title)
        session.add(lst)
        session.commit()
        session.refresh(lst)
        return lst

def get_list(list_id: int) -> Lists | None:
    with Session(engine) as session:
        return session.get(Lists, list_id)

def get_all_lists() -> list[Lists]:
    """Все списки, отсортированные по названию."""
    with Session(engine) as session:
        stmt = select(Lists).order_by(Lists.title)
        return list(session.scalars(stmt).all())

def update_list(list_id: int, new_title: str) -> Lists | None:
    with Session(engine) as session:
        lst = session.get(Lists, list_id)
        if lst:
            lst.title = new_title
            session.commit()
            session.refresh(lst)
        return lst

def delete_list(list_id: int) -> bool:
    with Session(engine) as session:
        lst = session.get(Lists, list_id)
        if lst:
            session.delete(lst)
            session.commit()
            return True
        return False

def search_lists_by_title(query: str) -> list[Lists]:
    """Поиск списков по подстроке в названии"""
    with Session(engine) as session:
        stmt = select(Lists).where(Lists.title.ilike(f"%{query}%")).order_by(Lists.title)
        return list(session.scalars(stmt).all())

def get_list_with_notes(list_id: int) -> Lists | None:
    """Список вместе со всеми его заметками"""
    with Session(engine) as session:
        stmt = (
            select(Lists)
            .where(Lists.list_id == list_id)
            .options(selectinload(Lists.notes))# Делает два SQL-запроса
        )
        return session.scalars(stmt).first()

def get_list_with_notes_and_authors(list_id: int) -> Lists | None:
    """Список + заметки + их авторы"""
    with Session(engine) as session:
        stmt = (
            select(Lists)
            .where(Lists.list_id == list_id)
            .options(
                
                selectinload(Lists.notes).joinedload(Note.user)
                 #  жадная загрузка заметок
            )
        )
        return session.scalars(stmt).first()

# ---------- CRUD для Note ----------
def create_note(user_id: int, list_id: int, title: str, author: str, review: str | None = None) -> Note:
    with Session(engine) as session:
        note = Note(
            user_id=user_id,
            list_id=list_id,
            title=title,
            author=author,
            review=review
        )
        session.add(note)
        session.commit()
        session.refresh(note)
        return note

def get_note(note_id: int) -> Note | None:
    with Session(engine) as session:
        return session.get(Note, note_id)

def update_note(note_id: int, **kwargs) -> Note | None:
    with Session(engine) as session:
        note = session.get(Note, note_id)
        if note:
            for key, value in kwargs.items():
                setattr(note, key, value)
            session.commit()
            session.refresh(note)
        return note

def delete_note(note_id: int) -> bool:
    with Session(engine) as session:
        note = session.get(Note, note_id)
        if note:
            session.delete(note)
            session.commit()
            return True
        return False

def get_notes_by_list(list_id: int) -> list[Note]:
    """Все заметки конкретного списка."""
    with Session(engine) as session:
        stmt = select(Note).where(Note.list_id == list_id).order_by(Note.note_id)
        return list(session.scalars(stmt).all())


def get_notes_by_user(user_id: int) -> list[Note]:
    """Все заметки конкретного пользователя."""
    with Session(engine) as session:
        stmt = select(Note).where(Note.user_id == user_id).order_by(Note.note_id)
        return list(session.scalars(stmt).all())

def get_note_with_author(note_id: int) -> Note | None:
    """Заметка вместе с автором (joinedload)."""
    with Session(engine) as session:
        stmt = (
            select(Note)
            .where(Note.note_id == note_id)
            .options(joinedload(Note.user))
        )
        return session.scalars(stmt).first()

# ---------- CRUD для Subscription ----------
def create_subscription(user_id: int, list_id: int) -> Subscription:
    with Session(engine) as session:
        sub = Subscription(user_id=user_id, list_id=list_id)
        session.add(sub)
        session.commit()
        return sub

def get_subscription(user_id: int, list_id: int) -> Subscription | None:
    with Session(engine) as session:
        return session.get(Subscription, (user_id, list_id))

def delete_subscription(user_id: int, list_id: int) -> bool:
    with Session(engine) as session:
        sub = session.get(Subscription, (user_id, list_id))
        if sub:
            session.delete(sub)
            session.commit()
            return True
        return False

def get_user_subscriptions(user_id: int) -> list[Lists]:
    """Списки, на которые подписан пользователь."""
    with Session(engine) as session:
        stmt = (
            select(Lists)
            .join(Subscription, Subscription.list_id == Lists.list_id)
            .where(Subscription.user_id == user_id)
            .order_by(Lists.title)
        )
        return list(session.scalars(stmt).all())

def get_list_subscribers(list_id: int) -> list[User]:
    """Пользователи, подписанные на список (для админа и рассылки уведомлений)."""
    with Session(engine) as session:
        stmt = (
            select(User)
            .join(Subscription, Subscription.user_id == User.user_id)
            .where(Subscription.list_id == list_id)
            .order_by(User.username)
        )
        return list(session.scalars(stmt).all())