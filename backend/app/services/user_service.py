"""
用户服务模块
"""
import uuid
from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..models.user import User, UserSession, Folder
from ..models.document import Document, Version
from ..core.auth import AuthService
from ..schemas.user import UserCreate, UserUpdate, UserStats


class UserService:
    """用户服务类"""

    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User:
        """
        创建新用户

        Args:
            db: 数据库会话
            user_data: 用户创建数据

        Returns:
            创建的用户对象

        Raises:
            ValueError: 用户名或邮箱已存在
        """
        # 检查用户名是否已存在
        existing_user = db.query(User).filter(
            (User.username == user_data.username) | (User.email == user_data.email)
        ).first()

        if existing_user:
            if existing_user.username == user_data.username:
                raise ValueError("Username already exists")
            else:
                raise ValueError("Email already exists")

        # 创建新用户
        user = User(
            id=str(uuid.uuid4()),
            username=user_data.username,
            email=user_data.email,
            full_name=user_data.full_name,
            password_hash=AuthService.hash_password(user_data.password),
            timezone=user_data.timezone,
            is_active=True,
            is_superuser=False
        )

        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def get_user(db: Session, user_id: str) -> Optional[User]:
        """
        根据ID获取用户

        Args:
            db: 数据库会话
            user_id: 用户ID

        Returns:
            用户对象或None
        """
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """
        根据用户名获取用户

        Args:
            db: 数据库会话
            username: 用户名

        Returns:
            用户对象或None
        """
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """
        根据邮箱获取用户

        Args:
            db: 数据库会话
            email: 邮箱地址

        Returns:
            用户对象或None
        """
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def authenticate(db: Session, username: str, password: str) -> Optional[User]:
        """
        验证用户登录

        Args:
            db: 数据库会话
            username: 用户名或邮箱
            password: 密码

        Returns:
            验证成功返回用户对象,失败返回None
        """
        # 尝试通过用户名或邮箱查找用户
        user = db.query(User).filter(
            (User.username == username) | (User.email == username)
        ).first()

        if not user:
            return None

        # 验证密码
        if not AuthService.verify_password(password, user.password_hash):
            return None

        # 更新最后登录时间
        user.last_login_at = datetime.utcnow()
        db.commit()

        return user

    @staticmethod
    def update_user(db: Session, user_id: str, user_data: UserUpdate) -> Optional[User]:
        """
        更新用户信息

        Args:
            db: 数据库会话
            user_id: 用户ID
            user_data: 更新数据

        Returns:
            更新后的用户对象或None
        """
        user = UserService.get_user(db, user_id)
        if not user:
            return None

        # 更新字段
        update_data = user_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)

        user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def update_password(
        db: Session,
        user_id: str,
        old_password: str,
        new_password: str
    ) -> bool:
        """
        更新用户密码

        Args:
            db: 数据库会话
            user_id: 用户ID
            old_password: 旧密码
            new_password: 新密码

        Returns:
            是否更新成功
        """
        user = UserService.get_user(db, user_id)
        if not user:
            return False

        # 验证旧密码
        if not AuthService.verify_password(old_password, user.password_hash):
            return False

        # 更新密码
        user.password_hash = AuthService.hash_password(new_password)
        user.updated_at = datetime.utcnow()
        db.commit()
        return True

    @staticmethod
    def delete_user(db: Session, user_id: str) -> bool:
        """
        删除用户(软删除,设置为非活跃)

        Args:
            db: 数据库会话
            user_id: 用户ID

        Returns:
            是否删除成功
        """
        user = UserService.get_user(db, user_id)
        if not user:
            return False

        user.is_active = False
        user.updated_at = datetime.utcnow()
        db.commit()
        return True

    @staticmethod
    def list_users(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None
    ) -> List[User]:
        """
        获取用户列表

        Args:
            db: 数据库会话
            skip: 跳过数量
            limit: 限制数量
            is_active: 是否活跃(None表示全部)

        Returns:
            用户列表
        """
        query = db.query(User)

        if is_active is not None:
            query = query.filter(User.is_active == is_active)

        return query.order_by(User.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_user_documents(
        db: Session,
        user_id: str,
        folder_id: Optional[str] = None
    ) -> List[Document]:
        """
        获取用户的文档列表

        Args:
            db: 数据库会话
            user_id: 用户ID
            folder_id: 文件夹ID(可选)

        Returns:
            文档列表
        """
        query = db.query(Document).filter(Document.owner_id == user_id)

        if folder_id:
            query = query.filter(Document.folder_id == folder_id)

        return query.order_by(Document.updated_at.desc()).all()

    @staticmethod
    def get_user_stats(db: Session, user_id: str) -> UserStats:
        """
        获取用户统计信息

        Args:
            db: 数据库会话
            user_id: 用户ID

        Returns:
            用户统计信息
        """
        # 文档总数
        total_documents = db.query(func.count(Document.id)).filter(
            Document.owner_id == user_id
        ).scalar() or 0

        # 版本总数(通过文档关联)
        total_versions = db.query(func.count(Version.id)).join(
            Document, Version.document_id == Document.id
        ).filter(Document.owner_id == user_id).scalar() or 0

        # 文件夹总数
        total_folders = db.query(func.count(Folder.id)).filter(
            Folder.owner_id == user_id
        ).scalar() or 0

        # 存储使用量(所有版本的内容大小总和)
        storage_used = db.query(
            func.sum(func.length(Version.content))
        ).join(
            Document, Version.document_id == Document.id
        ).filter(Document.owner_id == user_id).scalar() or 0

        # 最后活跃时间(最近文档更新时间)
        last_active_doc = db.query(Document.updated_at).filter(
            Document.owner_id == user_id
        ).order_by(Document.updated_at.desc()).first()

        last_active = last_active_doc[0] if last_active_doc else None

        return UserStats(
            total_documents=total_documents,
            total_versions=total_versions,
            total_folders=total_folders,
            storage_used=storage_used,
            last_active=last_active
        )

    @staticmethod
    def create_session(
        db: Session,
        user_id: str,
        token: str,
        refresh_token: str,
        expires_at: datetime,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> UserSession:
        """
        创建用户会话

        Args:
            db: 数据库会话
            user_id: 用户ID
            token: 访问令牌
            refresh_token: 刷新令牌
            expires_at: 过期时间
            ip_address: IP地址
            user_agent: 用户代理

        Returns:
            会话对象
        """
        session = UserSession(
            id=str(uuid.uuid4()),
            user_id=user_id,
            token=token,
            refresh_token=refresh_token,
            expires_at=expires_at,
            ip_address=ip_address,
            user_agent=user_agent
        )

        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def get_session_by_token(db: Session, token: str) -> Optional[UserSession]:
        """
        根据令牌获取会话

        Args:
            db: 数据库会话
            token: 访问令牌或刷新令牌

        Returns:
            会话对象或None
        """
        return db.query(UserSession).filter(
            (UserSession.token == token) | (UserSession.refresh_token == token)
        ).first()

    @staticmethod
    def delete_session(db: Session, session_id: str) -> bool:
        """
        删除会话(登出)

        Args:
            db: 数据库会话
            session_id: 会话ID

        Returns:
            是否删除成功
        """
        session = db.query(UserSession).filter(UserSession.id == session_id).first()
        if not session:
            return False

        db.delete(session)
        db.commit()
        return True

    @staticmethod
    def delete_user_sessions(db: Session, user_id: str) -> int:
        """
        删除用户所有会话(全部登出)

        Args:
            db: 数据库会话
            user_id: 用户ID

        Returns:
            删除的会话数量
        """
        count = db.query(UserSession).filter(UserSession.user_id == user_id).delete()
        db.commit()
        return count
