from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # GLM API Configuration
    glm_api_key: str = ""
    glm_model: str = "glm-4"

    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True

    # Database
    database_url: str = "sqlite+aiosqlite:///./aiteam.db"

    # CORS
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
