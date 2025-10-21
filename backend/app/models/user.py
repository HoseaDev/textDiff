"""
用户相关的数据模型
"""
from sqlalchemy import Column, String, Boolean, TIMESTAMP, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base


class User(Base):
    """用户表"""
    __tablename__ = "users"

    id = Column(String(36), primary_key=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100))
    avatar_url = Column(String(500))
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    last_login_at = Column(TIMESTAMP, nullable=True)
    timezone = Column(String(50), default='Asia/Shanghai')

    # 关系
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="owner", cascade="all, delete-orphan")
    folders = relationship("Folder", back_populates="owner", cascade="all, delete-orphan")


class UserSession(Base):
    """用户会话表"""
    __tablename__ = "user_sessions"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token = Column(String(500), nullable=False, index=True)
    refresh_token = Column(String(500))
    expires_at = Column(TIMESTAMP, nullable=False)
    ip_address = Column(String(45))
    user_agent = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())

    # 关系
    user = relationship("User", back_populates="sessions")


class Folder(Base):
    """文件夹表"""
    __tablename__ = "folders"

    id = Column(String(36), primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    parent_id = Column(String(36), ForeignKey("folders.id", ondelete="CASCADE"))
    owner_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    color = Column(String(7))
    icon = Column(String(50))
    is_public = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # 关系
    owner = relationship("User", back_populates="folders")
    parent = relationship("Folder", remote_side=[id], backref="children")
    documents = relationship("Document", back_populates="folder")


class VerificationCode(Base):
    """邮箱验证码表"""
    __tablename__ = "verification_codes"

    id = Column(String(36), primary_key=True)
    email = Column(String(100), nullable=False, index=True)
    code = Column(String(10), nullable=False)
    purpose = Column(String(20), nullable=False, default="register")  # register/login/reset_password
    is_used = Column(Boolean, default=False)
    expires_at = Column(TIMESTAMP, nullable=False)
    used_at = Column(TIMESTAMP, nullable=True)
    ip_address = Column(String(45))
    created_at = Column(TIMESTAMP, server_default=func.now())
