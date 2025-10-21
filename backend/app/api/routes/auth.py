"""
认证相关 API 路由
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional

from ...core.database import get_db
from ...core.auth import (
    AuthService,
    get_current_user,
    get_current_active_user,
    get_current_superuser
)
from ...core.config import settings
from ...services.user_service import UserService
from ...services.verification_service import VerificationService
from ...schemas.user import (
    UserCreate,
    UserLogin,
    UserResponse,
    UserUpdate,
    UserPasswordUpdate,
    UserListItem,
    UserStats,
    TokenResponse,
    TokenRefreshRequest,
    TokenRefreshResponse,
    MessageResponse
)
from ...models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    用户注册

    - **username**: 用户名(3-50字符)
    - **email**: 邮箱地址
    - **password**: 密码(至少6字符)
    - **verification_code**: 邮箱验证码
    - **full_name**: 全名(可选)
    - **timezone**: 时区(默认 Asia/Shanghai)
    """
    try:
        # 验证邮箱验证码
        is_valid, message = VerificationService.verify_code(
            db=db,
            email=user_data.email,
            code=user_data.verification_code,
            purpose="register"
        )

        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )

        # 创建用户
        user = UserService.create_user(db, user_data)

        # 生成令牌
        access_token = AuthService.create_access_token(user.id)
        refresh_token = AuthService.create_refresh_token(user.id)

        # 创建会话
        expires_at = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        UserService.create_session(
            db,
            user_id=user.id,
            token=access_token,
            refresh_token=refresh_token,
            expires_at=expires_at,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent")
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserResponse.model_validate(user)
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: UserLogin,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    用户登录

    - **username**: 用户名或邮箱
    - **password**: 密码
    """
    # 验证用户
    user = UserService.authenticate(db, login_data.username, login_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )

    # 生成令牌
    access_token = AuthService.create_access_token(user.id)
    refresh_token = AuthService.create_refresh_token(user.id)

    # 创建会话
    expires_at = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    UserService.create_session(
        db,
        user_id=user.id,
        token=access_token,
        refresh_token=refresh_token,
        expires_at=expires_at,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse.model_validate(user)
    )


@router.post("/logout", response_model=MessageResponse)
async def logout(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    用户登出

    删除所有会话
    """
    count = UserService.delete_user_sessions(db, current_user.id)

    return MessageResponse(
        message=f"Successfully logged out. {count} session(s) deleted.",
        success=True
    )


@router.post("/refresh", response_model=TokenRefreshResponse)
async def refresh_token(
    refresh_data: TokenRefreshRequest,
    db: Session = Depends(get_db)
):
    """
    刷新访问令牌

    使用刷新令牌获取新的访问令牌
    """
    try:
        # 解析刷新令牌
        payload = AuthService.decode_token(refresh_data.refresh_token)

        # 检查令牌类型
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )

        user_id = payload.get("sub")

        # 验证会话是否存在
        session = UserService.get_session_by_token(db, refresh_data.refresh_token)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session not found"
            )

        # 检查会话是否过期
        if session.expires_at < datetime.utcnow():
            UserService.delete_session(db, session.id)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session expired"
            )

        # 生成新的访问令牌
        new_access_token = AuthService.create_access_token(user_id)

        # 更新会话令牌
        session.token = new_access_token
        db.commit()

        return TokenRefreshResponse(
            access_token=new_access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not refresh token"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    获取当前登录用户信息
    """
    return UserResponse.model_validate(current_user)


@router.put("/me", response_model=UserResponse)
async def update_current_user_info(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    更新当前用户信息

    - **email**: 邮箱(可选)
    - **full_name**: 全名(可选)
    - **avatar_url**: 头像URL(可选)
    - **timezone**: 时区(可选)
    """
    updated_user = UserService.update_user(db, current_user.id, user_data)

    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return UserResponse.model_validate(updated_user)


@router.post("/me/password", response_model=MessageResponse)
async def update_password(
    password_data: UserPasswordUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    修改密码

    - **old_password**: 旧密码
    - **new_password**: 新密码(至少6字符)
    """
    success = UserService.update_password(
        db,
        current_user.id,
        password_data.old_password,
        password_data.new_password
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect old password"
        )

    # 删除所有会话,要求重新登录
    UserService.delete_user_sessions(db, current_user.id)

    return MessageResponse(
        message="Password updated successfully. Please login again.",
        success=True
    )


@router.get("/me/stats", response_model=UserStats)
async def get_current_user_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取当前用户统计信息

    包括文档数、版本数、文件夹数、存储使用量等
    """
    return UserService.get_user_stats(db, current_user.id)


# ============= 管理员接口 =============

@router.get("/users", response_model=list[UserListItem])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db)
):
    """
    获取用户列表(仅管理员)

    - **skip**: 跳过数量
    - **limit**: 限制数量(最多100)
    - **is_active**: 是否活跃(可选)
    """
    users = UserService.list_users(db, skip=skip, limit=min(limit, 100), is_active=is_active)
    return [UserListItem.model_validate(user) for user in users]


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: str,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db)
):
    """
    根据ID获取用户信息(仅管理员)
    """
    user = UserService.get_user(db, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return UserResponse.model_validate(user)


@router.delete("/users/{user_id}", response_model=MessageResponse)
async def delete_user(
    user_id: str,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db)
):
    """
    删除用户(仅管理员)

    软删除,将用户设置为非活跃状态
    """
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete yourself"
        )

    success = UserService.delete_user(db, user_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return MessageResponse(
        message="User deleted successfully",
        success=True
    )
