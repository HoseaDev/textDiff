"""
应用配置模块
"""
from pydantic_settings import BaseSettings
from typing import Optional
from datetime import datetime
from zoneinfo import ZoneInfo


class Settings(BaseSettings):
    """应用配置"""

    # 应用基础配置
    APP_NAME: str = "TextDiff"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # 数据库配置
    DATABASE_URL: str = "mysql+pymysql://work:s4TUPM.qXmfvAUu@23.19.231.78:3306/textdiff?charset=utf8mb4"

    # 数据库连接池配置
    DATABASE_POOL_SIZE: int = 10
    DATABASE_POOL_RECYCLE: int = 3600
    DATABASE_POOL_PRE_PING: bool = True

    # Redis 配置（可选，用于缓存和WebSocket）
    REDIS_URL: Optional[str] = None
    # 例如: "redis://localhost:6379/0"

    # JWT 认证配置
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24小时

    # CORS 配置
    ALLOWED_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]

    # 文件存储配置
    MAX_CONTENT_SIZE: int = 10 * 1024 * 1024  # 10MB

    # 时区配置
    DEFAULT_TIMEZONE: str = "Asia/Shanghai"

    # SMTP 邮件配置
    SMTP_HOST: str = "your-smtp-server.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = "your-email@example.com"
    SMTP_PASSWORD: str = "your-smtp-password"
    SMTP_FROM_EMAIL: str = "noreply@textdiff.com"
    SMTP_FROM_NAME: str = "TextDiff"
    SMTP_USE_TLS: bool = True

    # 验证码配置
    VERIFICATION_CODE_EXPIRE_MINUTES: int = 5
    VERIFICATION_CODE_LENGTH: int = 6

    def get_local_time(self, utc_time: datetime) -> datetime:
        """
        将 UTC 时间转换为本地时区时间

        Args:
            utc_time: UTC 时间

        Returns:
            本地时区时间
        """
        if utc_time is None:
            return None

        # 如果没有时区信息，假设是 UTC
        if utc_time.tzinfo is None:
            utc_time = utc_time.replace(tzinfo=ZoneInfo("UTC"))

        # 转换到本地时区
        local_tz = ZoneInfo(self.DEFAULT_TIMEZONE)
        return utc_time.astimezone(local_tz)

    def get_utc_time(self, local_time: datetime) -> datetime:
        """
        将本地时区时间转换为 UTC 时间

        Args:
            local_time: 本地时区时间

        Returns:
            UTC 时间
        """
        if local_time is None:
            return None

        # 如果没有时区信息，假设是本地时区
        if local_time.tzinfo is None:
            local_tz = ZoneInfo(self.DEFAULT_TIMEZONE)
            local_time = local_time.replace(tzinfo=local_tz)

        # 转换到 UTC
        return local_time.astimezone(ZoneInfo("UTC"))

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
