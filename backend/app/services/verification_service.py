"""
验证码服务模块
包含验证码生成、存储、验证和防机器人机制
"""
import random
import string
from datetime import datetime, timedelta
from typing import Optional, Dict
import hashlib
from sqlalchemy.orm import Session

from ..core.config import settings
from ..models.user import VerificationCode
from .email_service import EmailService


class VerificationService:
    """验证码服务类"""

    # 内存中的频率限制缓存 (生产环境应使用Redis)
    _rate_limit_cache: Dict[str, dict] = {}

    @staticmethod
    def generate_code(length: int = None) -> str:
        """
        生成随机验证码

        Args:
            length: 验证码长度,默认使用配置中的值

        Returns:
            验证码字符串
        """
        if length is None:
            length = settings.VERIFICATION_CODE_LENGTH

        # 只使用数字,更容易识别和输入
        return ''.join(random.choices(string.digits, k=length))

    @staticmethod
    def _get_rate_limit_key(email: str, ip: str) -> str:
        """生成频率限制的缓存键"""
        return hashlib.md5(f"{email}:{ip}".encode()).hexdigest()

    @staticmethod
    def check_rate_limit(email: str, ip: str) -> tuple[bool, Optional[str]]:
        """
        检查发送频率限制 - 防机器人机制

        规则:
        1. 同一邮箱60秒内只能发送1次
        2. 同一IP 1分钟内最多发送3次
        3. 同一邮箱1小时内最多发送10次

        Args:
            email: 邮箱地址
            ip: IP地址

        Returns:
            (是否允许发送, 错误信息)
        """
        now = datetime.utcnow()
        cache_key = VerificationService._get_rate_limit_key(email, ip)

        # 获取或创建缓存记录
        if cache_key not in VerificationService._rate_limit_cache:
            VerificationService._rate_limit_cache[cache_key] = {
                'last_send_time': None,
                'send_times_minute': [],
                'send_times_hour': []
            }

        cache = VerificationService._rate_limit_cache[cache_key]

        # 清理过期记录
        cache['send_times_minute'] = [
            t for t in cache['send_times_minute']
            if now - t < timedelta(minutes=1)
        ]
        cache['send_times_hour'] = [
            t for t in cache['send_times_hour']
            if now - t < timedelta(hours=1)
        ]

        # 检查1: 同一邮箱60秒内只能发送1次
        if cache['last_send_time']:
            seconds_since_last = (now - cache['last_send_time']).total_seconds()
            if seconds_since_last < 60:
                wait_seconds = int(60 - seconds_since_last)
                return False, f"发送过于频繁,请 {wait_seconds} 秒后重试"

        # 检查2: 同一IP 1分钟内最多发送3次
        if len(cache['send_times_minute']) >= 3:
            return False, "发送次数过多,请1分钟后重试"

        # 检查3: 同一邮箱1小时内最多发送10次
        if len(cache['send_times_hour']) >= 10:
            return False, "今日发送次数已达上限,请稍后重试"

        return True, None

    @staticmethod
    def record_send(email: str, ip: str):
        """记录发送时间"""
        now = datetime.utcnow()
        cache_key = VerificationService._get_rate_limit_key(email, ip)

        if cache_key in VerificationService._rate_limit_cache:
            cache = VerificationService._rate_limit_cache[cache_key]
            cache['last_send_time'] = now
            cache['send_times_minute'].append(now)
            cache['send_times_hour'].append(now)

    @staticmethod
    def create_verification_code(
        db: Session,
        email: str,
        purpose: str = "register",
        ip_address: Optional[str] = None
    ) -> tuple[bool, str, Optional[str]]:
        """
        创建并发送验证码

        Args:
            db: 数据库会话
            email: 邮箱地址
            purpose: 用途 (register/login/reset_password)
            ip_address: IP地址

        Returns:
            (是否成功, 消息, 验证码ID)
        """
        # 检查频率限制
        if ip_address:
            allowed, error_msg = VerificationService.check_rate_limit(email, ip_address)
            if not allowed:
                return False, error_msg, None

        # 生成验证码
        code = VerificationService.generate_code()

        # 计算过期时间
        expires_at = datetime.utcnow() + timedelta(
            minutes=settings.VERIFICATION_CODE_EXPIRE_MINUTES
        )

        # 删除该邮箱之前未使用的验证码
        db.query(VerificationCode).filter(
            VerificationCode.email == email,
            VerificationCode.purpose == purpose,
            VerificationCode.is_used == False
        ).delete()

        # 创建验证码记录
        import uuid
        verification = VerificationCode(
            id=str(uuid.uuid4()),
            email=email,
            code=code,
            purpose=purpose,
            expires_at=expires_at,
            ip_address=ip_address
        )

        db.add(verification)
        db.commit()
        db.refresh(verification)

        # 发送邮件
        success = EmailService.send_verification_code(
            email,
            code,
            settings.VERIFICATION_CODE_EXPIRE_MINUTES
        )

        if not success:
            return False, "邮件发送失败,请稍后重试", None

        # 记录发送时间
        if ip_address:
            VerificationService.record_send(email, ip_address)

        return True, "验证码已发送,请查收邮件", verification.id

    @staticmethod
    def verify_code(
        db: Session,
        email: str,
        code: str,
        purpose: str = "register",
        delete_after_verify: bool = True
    ) -> tuple[bool, str]:
        """
        验证验证码

        Args:
            db: 数据库会话
            email: 邮箱地址
            code: 验证码
            purpose: 用途
            delete_after_verify: 验证成功后是否删除

        Returns:
            (是否验证成功, 消息)
        """
        # 查找验证码
        verification = db.query(VerificationCode).filter(
            VerificationCode.email == email,
            VerificationCode.code == code,
            VerificationCode.purpose == purpose,
            VerificationCode.is_used == False
        ).first()

        if not verification:
            return False, "验证码无效或已使用"

        # 检查是否过期
        if datetime.utcnow() > verification.expires_at:
            return False, "验证码已过期,请重新获取"

        # 标记为已使用
        verification.is_used = True
        verification.used_at = datetime.utcnow()

        if delete_after_verify:
            db.delete(verification)

        db.commit()

        return True, "验证成功"

    @staticmethod
    def cleanup_expired_codes(db: Session):
        """
        清理过期的验证码

        Args:
            db: 数据库会话
        """
        db.query(VerificationCode).filter(
            VerificationCode.expires_at < datetime.utcnow()
        ).delete()
        db.commit()
