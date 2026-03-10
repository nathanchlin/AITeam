from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # GLM API Configuration
    glm_api_key: str = ""
    glm_model: str = "glm-4-flash"  # 用于分析、讨论、计划生成
    glm_base_url: str = ""  # 可选的备用端点

    # GLM Coding Model (用于代码生成，更强的能力)
    glm_coding_model: str = "glm-5"  # 代码生成专用模型
    glm_coding_base_url: str = "https://open.bigmodel.cn/api/coding/paas/v4"  # Coding Plan 端点

    # Token limits
    glm_max_tokens: int = 131072  # Maximum output tokens (128K for GLM-5)

    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True

    # Database
    database_url: str = "sqlite+aiosqlite:///./aiteam.db"

    # CORS (允许所有来源 - 开发环境)
    # In production, set CORS_ORIGINS environment variable (comma-separated)
    cors_origins: str = "*"

    # Redis Configuration
    redis_url: str = "redis://localhost:6379/0"

    # Celery Configuration
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/1"

    @property
    def celery_config(self) -> dict:
        """Get Celery configuration dict"""
        return {
            "broker_url": self.celery_broker_url,
            "result_backend": self.celery_result_backend,
            "task_serializer": "json",
            "accept_content": ["json"],
            "result_serializer": "json",
            "timezone": "UTC",
            "enable_utc": True,
            "task_track_started": True,
            "task_time_limit": 1800,  # 30 minutes hard limit
            "task_soft_time_limit": 1500,  # 25 minutes soft limit
            "worker_prefetch_multiplier": 1,  # Only fetch one task at a time
            "worker_concurrency": 2,  # Number of concurrent workers
        }

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
