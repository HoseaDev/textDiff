"""
JWT 认证服务模块
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from .config import settings
from .database import get_db
from ..models.user import User

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer 认证
security = HTTPBearer()


class AuthService:
    """认证服务类"""

    @staticmethod
    def hash_password(password: str) -> str:
        """
        对密码进行哈希加密

        Args:
            password: 明文密码

        Returns:
            加密后的密码哈希
        """
        # bcrypt限制密码最长72字节,需要截断
        password_bytes = password.encode('utf-8')
        if len(password_bytes) > 72:
            password = password_bytes[:72].decode('utf-8', errors='ignore')
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        验证密码是否正确

        Args:
            plain_password: 明文密码
            hashed_password: 加密后的密码哈希

        Returns:
            密码是否匹配
        """
        # bcrypt限制密码最长72字节,需要截断
        password_bytes = plain_password.encode('utf-8')
        if len(password_bytes) > 72:
            plain_password = password_bytes[:72].decode('utf-8', errors='ignore')
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def create_access_token(
        user_id: str,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        创建 JWT 访问令牌

        Args:
            user_id: 用户ID
            expires_delta: 过期时间增量,默认使用配置中的值

        Returns:
            JWT token 字符串
        """
        if expires_delta is None:
            expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

        expire = datetime.utcnow() + expires_delta
        payload = {
            "sub": user_id,  # subject: 用户ID
            "exp": expire,   # expiration time: 过期时间
            "iat": datetime.utcnow(),  # issued at: 签发时间
            "type": "access"  # token类型
        }

        encoded_jwt = jwt.encode(
            payload,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        return encoded_jwt

    @staticmethod
    def create_refresh_token(user_id: str) -> str:
        """
        创建刷新令牌(有效期更长)

        Args:
            user_id: 用户ID

        Returns:
            刷新令牌字符串
        """
        expire = datetime.utcnow() + timedelta(days=7)  # 7天有效期
        payload = {
            "sub": user_id,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh"
        }

        encoded_jwt = jwt.encode(
            payload,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        return encoded_jwt

    @staticmethod
    def decode_token(token: str) -> dict:
        """
        解析 JWT token

        Args:
            token: JWT token 字符串

        Returns:
            解析后的 payload 字典

        Raises:
            HTTPException: token 过期或无效
        """
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

    @staticmethod
    def get_user_from_token(token: str, db: Session) -> User:
        """
        从 token 中获取用户对象

        Args:
            token: JWT token 字符串
            db: 数据库会话

        Returns:
            用户对象

        Raises:
            HTTPException: 用户不存在或 token 无效
        """
        payload = AuthService.decode_token(token)
        user_id: str = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Inactive user"
            )

        return user


# 依赖注入: 获取当前用户
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    依赖注入函数: 从请求头中获取当前登录用户

    Args:
        credentials: HTTP Bearer 凭证
        db: 数据库会话

    Returns:
        当前登录的用户对象

    Raises:
        HTTPException: 认证失败
    """
    token = credentials.credentials
    return AuthService.get_user_from_token(token, db)


# 依赖注入: 获取当前活跃用户
async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    依赖注入函数: 获取当前活跃用户(已验证 is_active)

    Args:
        current_user: 当前用户

    Returns:
        活跃用户对象

    Raises:
        HTTPException: 用户未激活
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


# 依赖注入: 要求超级用户权限
async def get_current_superuser(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    依赖注入函数: 要求超级用户权限

    Args:
        current_user: 当前活跃用户

    Returns:
        超级用户对象

    Raises:
        HTTPException: 权限不足
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user
