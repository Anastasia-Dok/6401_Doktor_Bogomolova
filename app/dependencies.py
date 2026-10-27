

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.models import User
from app.security import decode_token


# Swagger UI узнаёт, что токен получается через /login
# встроенный в FastAPI класс. Реализует стандарт OAuth2 Password Flow.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def get_db() : 
    """Открывает сессию БД на каждый запрос и закрывает её после."""
    db = SessionLocal() # ← SessionLocal → engine → пул соединений
    try:
        yield db    # ← передаём в роутер
    finally:
        db.close()  # ← ПОСЛЕ роутера
#yield — «отдать» db и приостановиться.
#FastAPI получает db (объект Session) и передаёт в роутер
#Роутер работает с db

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Достаёт текущего пользователя из JWT.

    - Берёт токен из заголовка `Authorization: Bearer <token>`
    - Декодирует через `decode_token`
    - Из payload достаёт `sub` (это user_id)
    - Загружает User из БД
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Неверный или просроченный токен",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_token(token)
    if payload is None:
        raise credentials_exception

    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    user = db.get(User, int(user_id))
    if user is None:
        raise credentials_exception

    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Пускает только пользователя с ролью admin."""
    if current_user.role.name != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Требуются права администратора",
        )
    return current_user