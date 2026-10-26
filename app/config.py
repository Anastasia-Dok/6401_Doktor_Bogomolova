from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Корень проекта: app/config.py → parent = app → parent = корень
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # База данных
    database_url: str

    # Приложение
    debug: bool = False

    # JWT
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60

     # gRPC
    grpc_host: str = "localhost"
    grpc_port: int = 50051



settings = Settings()