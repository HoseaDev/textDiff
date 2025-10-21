"""
用户相关的 Pydantic 模型
"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_serializer
from typing import Optional
from datetime import datetime
from zoneinfo import ZoneInfo


# ============= 用户基础模型 =============

class UserBase(BaseModel):
    """用户基础模型"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱地址")
    full_name: Optional[str] = Field(None, max_length=100, description="全名")
    timezone: str = Field(default="Asia/Shanghai", description="时区")


# ============= 用户创建模型 =============

class UserCreate(UserBase):
    """用户注册请求模型"""
    password: str = Field(..., min_length=6, max_length=100, description="密码")
    verification_code: str = Field(..., min_length=4, max_length=10, description="邮箱验证码")


# ============= 用户登录模型 =============

class UserLogin(BaseModel):
    """用户登录请求模型"""
    username: str = Field(..., description="用户名或邮箱")
    password: str = Field(..., description="密码")


# ============= 用户更新模型 =============

class UserUpdate(BaseModel):
    """用户信息更新模型"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, max_length=100)
    avatar_url: Optional[str] = Field(None, max_length=500)
    timezone: Optional[str] = None


class UserPasswordUpdate(BaseModel):
    """用户密码更新模型"""
    old_password: str = Field(..., description="旧密码")
    new_password: str = Field(..., min_length=6, max_length=100, description="新密码")


# ============= 用户响应模型 =============

class UserResponse(UserBase):
    """用户信息响应模型"""
    id: str
    avatar_url: Optional[str] = None
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

    @field_serializer('created_at', 'updated_at', 'last_login_at')
    def serialize_datetime(self, value: Optional[datetime]) -> Optional[str]:
        """将 UTC 时间转换为本地时区并序列化为 ISO 格式字符串"""
        if value is None:
            return None
        if value.tzinfo is None:
            value = value.replace(tzinfo=ZoneInfo("UTC"))
        local_time = value.astimezone(ZoneInfo("Asia/Shanghai"))
        return local_time.isoformat()


class UserListItem(BaseModel):
    """用户列表项(简化版)"""
    id: str
    username: str
    email: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_serializer('created_at')
    def serialize_datetime(self, value: datetime) -> str:
        """将 UTC 时间转换为本地时区并序列化"""
        if value.tzinfo is None:
            value = value.replace(tzinfo=ZoneInfo("UTC"))
        local_time = value.astimezone(ZoneInfo("Asia/Shanghai"))
        return local_time.isoformat()


# ============= Token 响应模型 =============

class TokenResponse(BaseModel):
    """Token 响应模型"""
    access_token: str = Field(..., description="访问令牌")
    refresh_token: str = Field(..., description="刷新令牌")
    token_type: str = Field(default="bearer", description="令牌类型")
    expires_in: int = Field(..., description="过期时间(秒)")
    user: UserResponse = Field(..., description="用户信息")


class TokenRefreshRequest(BaseModel):
    """刷新令牌请求模型"""
    refresh_token: str = Field(..., description="刷新令牌")


class TokenRefreshResponse(BaseModel):
    """刷新令牌响应模型"""
    access_token: str = Field(..., description="新的访问令牌")
    token_type: str = Field(default="bearer", description="令牌类型")
    expires_in: int = Field(..., description="过期时间(秒)")


# ============= 用户会话模型 =============

class SessionResponse(BaseModel):
    """用户会话响应模型"""
    id: str
    user_id: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime
    expires_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_serializer('created_at', 'expires_at')
    def serialize_datetime(self, value: datetime) -> str:
        """时区转换序列化"""
        if value.tzinfo is None:
            value = value.replace(tzinfo=ZoneInfo("UTC"))
        local_time = value.astimezone(ZoneInfo("Asia/Shanghai"))
        return local_time.isoformat()


# ============= 用户统计模型 =============

class UserStats(BaseModel):
    """用户统计信息"""
    total_documents: int = Field(default=0, description="文档总数")
    total_versions: int = Field(default=0, description="版本总数")
    total_folders: int = Field(default=0, description="文件夹总数")
    storage_used: int = Field(default=0, description="已使用存储(字节)")
    last_active: Optional[datetime] = None

    @field_serializer('last_active')
    def serialize_datetime(self, value: Optional[datetime]) -> Optional[str]:
        """时区转换序列化"""
        if value is None:
            return None
        if value.tzinfo is None:
            value = value.replace(tzinfo=ZoneInfo("UTC"))
        local_time = value.astimezone(ZoneInfo("Asia/Shanghai"))
        return local_time.isoformat()


# ============= 通用响应模型 =============

class MessageResponse(BaseModel):
    """通用消息响应"""
    message: str = Field(..., description="消息内容")
    success: bool = Field(default=True, description="是否成功")
