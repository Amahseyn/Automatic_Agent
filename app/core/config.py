from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    APP_NAME: str = "LLMAgent User Service"
    VERSION: str = "1.0.0"
    SQLALCHEMY_DATABASE_URI: str = "postgresql://postgres:m102030m@localhost:5432/agent"
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 500

settings = Settings()