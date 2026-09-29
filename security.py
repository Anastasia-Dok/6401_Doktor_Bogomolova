import bcrypt

def hash_password(password: str) -> str:
    """Превращает сырой пароль в хеш (bcrypt напрямую)."""
    # bcrypt принимает bytes, возвращает bytes
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
