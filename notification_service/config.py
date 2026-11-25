from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent #вычисляется корневая папка проекта

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env", extra="ignore")
    rabbitmq_url: str = "amqp://guest:guest@localhost:5672/"
    rabbitmq_exchange: str = "events" # имя обменника (exchange), куда API Service публикует события.
    rabbitmq_queue: str = "notifications"  # имя очереди, которую слушает Notification Service
    # Параметры собственного WS-сервера (вместо FastAPI-эндпоинта)
    ws_host: str = "127.0.0.1"
    ws_port: int = 8001

settings = Settings()