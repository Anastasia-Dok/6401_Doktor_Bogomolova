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
    jwt_secret: str  # ← секрет для подписи
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60

     # gRPC
    grpc_host: str = "localhost"
    grpc_port: int = 50051
    
    # RabbitMQ
    rabbitmq_url: str = "amqp://guest:guest@localhost:5672/"
    rabbitmq_exchange: str = "events"
    rabbitmq_queue: str = "notifications"
    rabbitmq_publish_timeout: float = 2.0  # сек, чтобы API не зависал, если брокер лежит



settings = Settings()