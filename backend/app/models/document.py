"""
文档数据模型
"""
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Text, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base
import uuid


def generate_uuid():
    """生成UUID字符串"""
    return str(uuid.uuid4())


class Document(Base):
    """文档表模型"""

    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(255), nullable=False, index=True)
    owner_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    folder_id = Column(String(36), ForeignKey("folders.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    current_version_number = Column(Integer, default=0)

    # 关联关系
    versions = relationship("Version", back_populates="document", cascade="all, delete-orphan")
    owner = relationship("User", back_populates="documents")
    folder = relationship("Folder", back_populates="documents")

    def __repr__(self):
        return f"<Document(id={self.id}, title={self.title}, owner={self.owner_id})>"


class Version(Base):
    """版本表模型"""

    __tablename__ = "versions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    version_number = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    content_hash = Column(String(64), index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    author = Column(String(100), default="anonymous")  # 保留用于向后兼容
    author_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    commit_message = Column(Text)
    save_type = Column(String(20), default="manual")  # manual, auto, draft
    parent_version_id = Column(String(36), ForeignKey("versions.id"), nullable=True)

    # 关联关系
    document = relationship("Document", back_populates="versions")
    parent_version = relationship("Version", remote_side=[id], backref="child_versions")
    tags = relationship("VersionTag", back_populates="version", cascade="all, delete-orphan")
    author_user = relationship("User")

    # 创建复合索引
    __table_args__ = (
        Index("idx_document_version", "document_id", "version_number"),
        Index("idx_created_at", "created_at"),
    )

    def __repr__(self):
        return f"<Version(id={self.id}, doc_id={self.document_id}, v={self.version_number})>"


class VersionTag(Base):
    """版本标签表模型"""

    __tablename__ = "version_tags"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    version_id = Column(String(36), ForeignKey("versions.id", ondelete="CASCADE"), nullable=False)
    tag_name = Column(String(50), nullable=False, index=True)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关联关系
    version = relationship("Version", back_populates="tags")

    def __repr__(self):
        return f"<VersionTag(id={self.id}, tag={self.tag_name})>"
