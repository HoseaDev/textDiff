"""
版本管理服务
"""
import hashlib
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import desc
from ..models.document import Document, Version, VersionTag
from ..schemas.document import (
    DocumentCreate,
    DocumentUpdate,
    VersionCreate,
    VersionTagCreate,
)


class VersionService:
    """版本管理服务类"""

    @staticmethod
    def create_document(db: Session, doc_data: DocumentCreate, owner_id: str) -> Document:
        """
        创建新文档，同时创建第一个版本

        Args:
            db: 数据库会话
            doc_data: 文档创建数据
            owner_id: 文档所有者ID

        Returns:
            创建的文档对象
        """
        # 创建文档
        document = Document(
            title=doc_data.title,
            owner_id=owner_id,
            current_version_number=1
        )
        db.add(document)
        db.flush()  # 获取文档ID

        # 创建初始版本
        initial_version = Version(
            document_id=document.id,
            version_number=1,
            content=doc_data.initial_content or "",
            content_hash=VersionService._compute_hash(doc_data.initial_content or ""),
            author=doc_data.author or "unknown",
            author_id=owner_id,
            commit_message="Initial version",
            save_type="manual",
        )
        db.add(initial_version)
        db.commit()
        db.refresh(document)

        return document

    @staticmethod
    def get_document(db: Session, document_id: str) -> Optional[Document]:
        """获取文档"""
        return db.query(Document).filter(Document.id == document_id).first()

    @staticmethod
    def get_all_documents(
        db: Session, skip: int = 0, limit: int = 20, sort_by: str = "updated_at"
    ) -> List[Document]:
        """获取所有文档（分页）"""
        query = db.query(Document)

        # 排序
        if sort_by == "created_at":
            query = query.order_by(desc(Document.created_at))
        elif sort_by == "title":
            query = query.order_by(Document.title)
        else:
            query = query.order_by(desc(Document.updated_at))

        return query.offset(skip).limit(limit).all()

    @staticmethod
    def get_user_documents(
        db: Session,
        user_id: str,
        skip: int = 0,
        limit: int = 20,
        sort_by: str = "updated_at",
        folder_id: str = None
    ) -> List[Document]:
        """
        获取指定用户的文档列表

        Args:
            db: 数据库会话
            user_id: 用户ID
            skip: 跳过数量
            limit: 限制数量
            sort_by: 排序字段
            folder_id: 文件夹ID筛选(可选)

        Returns:
            文档列表
        """
        query = db.query(Document).filter(Document.owner_id == user_id)

        # 文件夹筛选
        if folder_id:
            query = query.filter(Document.folder_id == folder_id)

        # 排序
        if sort_by == "created_at":
            query = query.order_by(desc(Document.created_at))
        elif sort_by == "title":
            query = query.order_by(Document.title)
        else:
            query = query.order_by(desc(Document.updated_at))

        return query.offset(skip).limit(limit).all()

    @staticmethod
    def update_document(
        db: Session, document_id: str, doc_data: DocumentUpdate
    ) -> Optional[Document]:
        """更新文档信息"""
        document = VersionService.get_document(db, document_id)
        if not document:
            return None

        if doc_data.title:
            document.title = doc_data.title

        db.commit()
        db.refresh(document)
        return document

    @staticmethod
    def delete_document(db: Session, document_id: str) -> bool:
        """删除文档（级联删除所有版本）"""
        document = VersionService.get_document(db, document_id)
        if not document:
            return False

        db.delete(document)
        db.commit()
        return True

    @staticmethod
    def create_version(
        db: Session,
        document_id: str,
        version_data: VersionCreate,
        author_id: str = None
    ) -> Optional[Version]:
        """
        创建新版本

        Args:
            db: 数据库会话
            document_id: 文档ID
            version_data: 版本数据
            author_id: 作者用户ID(可选)

        Returns:
            创建的版本对象，如果内容未变化则返回None
        """
        document = VersionService.get_document(db, document_id)
        if not document:
            return None

        # 计算内容哈希
        content_hash = VersionService._compute_hash(version_data.content)

        # 获取最新版本，检查内容是否真的变化
        latest_version = VersionService.get_latest_version(db, document_id)
        if latest_version and latest_version.content_hash == content_hash:
            # 内容未变化，不创建新版本
            return None

        # 创建新版本
        new_version_number = document.current_version_number + 1
        new_version = Version(
            document_id=document_id,
            version_number=new_version_number,
            content=version_data.content,
            content_hash=content_hash,
            author=version_data.author or "unknown",
            author_id=author_id,
            commit_message=version_data.commit_message,
            save_type=version_data.save_type,
            parent_version_id=latest_version.id if latest_version else None,
        )

        db.add(new_version)
        document.current_version_number = new_version_number
        db.commit()
        db.refresh(new_version)

        return new_version

    @staticmethod
    def get_version(db: Session, version_id: str) -> Optional[Version]:
        """获取指定版本"""
        return db.query(Version).filter(Version.id == version_id).first()

    @staticmethod
    def get_version_by_number(
        db: Session, document_id: str, version_number: int
    ) -> Optional[Version]:
        """根据版本号获取版本"""
        return (
            db.query(Version)
            .filter(
                Version.document_id == document_id,
                Version.version_number == version_number,
            )
            .first()
        )

    @staticmethod
    def get_latest_version(db: Session, document_id: str) -> Optional[Version]:
        """获取文档的最新版本"""
        return (
            db.query(Version)
            .filter(Version.document_id == document_id)
            .order_by(desc(Version.version_number))
            .first()
        )

    @staticmethod
    def get_versions(
        db: Session,
        document_id: str,
        skip: int = 0,
        limit: int = 50,
        save_type: Optional[str] = None,
    ) -> List[Version]:
        """
        获取文档的版本列表

        Args:
            db: 数据库会话
            document_id: 文档ID
            skip: 跳过数量
            limit: 限制数量
            save_type: 保存类型筛选 (manual, auto, draft)

        Returns:
            版本列表
        """
        query = db.query(Version).filter(Version.document_id == document_id)

        if save_type:
            query = query.filter(Version.save_type == save_type)

        return query.order_by(desc(Version.version_number)).offset(skip).limit(limit).all()

    @staticmethod
    def restore_version(db: Session, document_id: str, version_id: str) -> Optional[Version]:
        """
        恢复到指定版本（通过创建新版本的方式）

        Args:
            db: 数据库会话
            document_id: 文档ID
            version_id: 要恢复的版本ID

        Returns:
            新创建的版本
        """
        old_version = VersionService.get_version(db, version_id)
        if not old_version or old_version.document_id != document_id:
            return None

        # 创建新版本，内容与旧版本相同
        version_data = VersionCreate(
            content=old_version.content,
            commit_message=f"Restored from version {old_version.version_number}",
            save_type="manual",
            author=old_version.author,
        )

        return VersionService.create_version(db, document_id, version_data)

    @staticmethod
    def create_version_tag(
        db: Session, version_id: str, tag_data: VersionTagCreate
    ) -> Optional[VersionTag]:
        """为版本创建标签"""
        version = VersionService.get_version(db, version_id)
        if not version:
            return None

        tag = VersionTag(
            version_id=version_id,
            tag_name=tag_data.tag_name,
            description=tag_data.description,
        )

        db.add(tag)
        db.commit()
        db.refresh(tag)
        return tag

    @staticmethod
    def get_version_tags(db: Session, version_id: str) -> List[VersionTag]:
        """获取版本的所有标签"""
        return db.query(VersionTag).filter(VersionTag.version_id == version_id).all()

    @staticmethod
    def delete_version_tag(db: Session, tag_id: str) -> bool:
        """删除版本标签"""
        tag = db.query(VersionTag).filter(VersionTag.id == tag_id).first()
        if not tag:
            return False

        db.delete(tag)
        db.commit()
        return True

    @staticmethod
    def _compute_hash(content: str) -> str:
        """计算内容的MD5哈希值"""
        return hashlib.md5(content.encode("utf-8")).hexdigest()
