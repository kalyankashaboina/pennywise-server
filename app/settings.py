from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # --------------------
    # App
    # --------------------
    APP_NAME: str = "PennyWise API"
    ENV: str = Field(
        default="development", description="development | staging | production"
    )
    DEBUG: bool = False

    # --------------------
    # API
    # --------------------
    API_PREFIX: str = "/api"

    # --------------------
    # Security
    # --------------------
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ALGORITHM: str = "HS256"

    # --------------------
    # Database (MongoDB)
    # --------------------
    MONGO_URI: str = "mongodb://localhost:27017"
    MONGO_DB_NAME: str = "pennywise"

    # --------------------
    # CORS
    # --------------------
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    # Loading values form environment variables or .env file
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
