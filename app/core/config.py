from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    REGISTRATION_ENABLED: bool = False        # Registration is disabled by default
    REGISTRATION_SECRET: Optional[str] = None # Secret key to registration (to create user)
    ADMIN_SECRET: Optional[str] = None        # Secret to create admin
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Service DB
    DATABASE_URL: str = "sqlite:///./crypto_api.db"

    # Clickhouse DB
    CLICKHOUSE_HOST: str
    CLICKHOUSE_PORT: int = 8123
    CLICKHOUSE_USER: str
    CLICKHOUSE_PASSWORD: str
    CLICKHOUSE_DATABASE: str
    
    class Config:
        env_file = ".env"

settings = Settings()
