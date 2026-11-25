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


# создаёт токен при логине
def create_access_token(data: dict) -> str: #Принимает словарь — payload (что «положить внутрь» токена).
    """Создаёт JWT с payload и временем жизни."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.jwt_expire_minutes
    )
    to_encode.update({"exp": expire})
    return jwt.encode( # сам создаёт header, сериализует payload, считает подпись.
        to_encode,
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )
#Header — {"alg": "HS256", "typ": "JWT"} → base64url.
#Payload — данные → JSON → base64url.
#Signature — HMAC-SHA256(header.payload, SECRET_KEY).
#Возвращает строку header.payload.signature.

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