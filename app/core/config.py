from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Регистрация новых пользователей
    REGISTRATION_ENABLED: bool = False  # По умолчанию регистрация отключена
    REGISTRATION_SECRET: str            # Секретный ключ для регистрации

    SECRET_KEY: str                     # Обязательная настройка без значения по умолчанию
    ALGORITHM: str = "HS256"            # Можно оставить разумное значение по умолчанию
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Остальные настройки...
    CLICKHOUSE_HOST: str = "localhost"
    CLICKHOUSE_PORT: int = 9000
    CLICKHOUSE_USER: str = "default" 
    CLICKHOUSE_PASSWORD: str = ""
    CLICKHOUSE_DATABASE: str = "cryptodata"
    
    class Config:
        env_file = ".env"

settings = Settings()
