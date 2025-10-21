"""
时区处理工具
"""
from datetime import datetime
from zoneinfo import ZoneInfo
from ..core.config import settings


def to_local_time(utc_time: datetime) -> datetime:
    """
    将 UTC 时间转换为本地时区时间

    Args:
        utc_time: UTC 时间（数据库中的时间）

    Returns:
        本地时区时间
    """
    return settings.get_local_time(utc_time)


def to_utc_time(local_time: datetime) -> datetime:
    """
    将本地时区时间转换为 UTC 时间

    Args:
        local_time: 本地时区时间

    Returns:
        UTC 时间（存储到数据库）
    """
    return settings.get_utc_time(local_time)


def now_local() -> datetime:
    """
    获取当前本地时区时间

    Returns:
        当前本地时区时间
    """
    utc_now = datetime.utcnow().replace(tzinfo=ZoneInfo("UTC"))
    return utc_now.astimezone(ZoneInfo(settings.DEFAULT_TIMEZONE))


def now_utc() -> datetime:
    """
    获取当前 UTC 时间

    Returns:
        当前 UTC 时间
    """
    return datetime.utcnow().replace(tzinfo=ZoneInfo("UTC"))
