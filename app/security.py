from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
import bcrypt

from app.config import settings


# ============ ХЭШИРОВАНИЕ ПАРОЛЕЙ ============
def hash_password(password: str) -> str:
    """Хэширует пароль через bcrypt."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    """Проверяет, соответствует ли пароль хэшу."""
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


# ============ JWT ============
def create_access_token(data: dict) -> str:
    """Создаёт JWT с payload и временем жизни."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.jwt_expire_minutes
    )
    to_encode.update({"exp": expire})
    return jwt.encode(
        to_encode,
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )


def decode_token(token: str) -> dict | None:
    """Проверяет подпись и срок действия JWT. None, если токен невалиден."""
    try:
        return jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )
    except JWTError:
        return None