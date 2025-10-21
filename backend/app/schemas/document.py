"""
文档相关的 Pydantic 模式
"""
from pydantic import BaseModel, Field, ConfigDict, field_serializer
from typing import Optional, List
from datetime import datetime
from zoneinfo import ZoneInfo


# ============ Document Schemas ============

class DocumentBase(BaseModel):
    """文档基础模式"""
    title: str = Field(..., min_length=1, max_length=255)


class DocumentCreate(DocumentBase):
    """创建文档请求模式"""
    initial_content: Optional[str] = ""
    author: Optional[str] = "anonymous"


class DocumentUpdate(BaseModel):
    """更新文档请求模式"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)


class DocumentResponse(DocumentBase):
    """文档响应模式"""
    id: str
    created_at: datetime
    updated_at: datetime
    current_version_number: int

    model_config = ConfigDict(from_attributes=True)

    @field_serializer('created_at', 'updated_at')
    def serialize_datetime(self, value: datetime) -> str:
        """将 UTC 时间转换为本地时区并序列化为 ISO 格式字符串"""
        if value is None:
            return None
        # 假设数据库存储的是 UTC 时间
        if value.tzinfo is None:
            value = value.replace(tzinfo=ZoneInfo("UTC"))
        # 转换到上海时区
        local_time = value.astimezone(ZoneInfo("Asia/Shanghai"))
        return local_time.isoformat()


# ============ Version Schemas ============

class VersionBase(BaseModel):
    """版本基础模式"""
    content: str


class VersionCreate(VersionBase):
    """创建版本请求模式"""
    commit_message: Optional[str] = None
    save_type: str = Field(default="manual", pattern="^(manual|auto|draft)$")
    author: Optional[str] = "anonymous"


class VersionResponse(VersionBase):
    """版本响应模式"""
    id: str
    document_id: str
    version_number: int
    content_hash: str
    created_at: datetime
    author: str
    commit_message: Optional[str]
    save_type: str
    parent_version_id: Optional[str]

    model_config = ConfigDict(from_attributes=True)

    @field_serializer('created_at')
    def serialize_datetime(self, value: datetime) -> str:
        """将 UTC 时间转换为本地时区并序列化为 ISO 格式字符串"""
        if value is None:
            return None
        if value.tzinfo is None:
            value = value.replace(tzinfo=ZoneInfo("UTC"))
        local_time = value.astimezone(ZoneInfo("Asia/Shanghai"))
        return local_time.isoformat()


class VersionListItem(BaseModel):
    """版本列表项模式（不含内容）"""
    id: str
    version_number: int
    created_at: datetime
    author: str
    commit_message: Optional[str]
    save_type: str
    content_length: int

    model_config = ConfigDict(from_attributes=True)

    @field_serializer('created_at')
    def serialize_datetime(self, value: datetime) -> str:
        """将 UTC 时间转换为本地时区并序列化为 ISO 格式字符串"""
        if value is None:
            return None
        if value.tzinfo is None:
            value = value.replace(tzinfo=ZoneInfo("UTC"))
        local_time = value.astimezone(ZoneInfo("Asia/Shanghai"))
        return local_time.isoformat()


# ============ Version Tag Schemas ============

class VersionTagCreate(BaseModel):
    """创建版本标签请求模式"""
    tag_name: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None


class VersionTagResponse(BaseModel):
    """版本标签响应模式"""
    id: str
    version_id: str
    tag_name: str
    description: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============ Diff Schemas ============

class DiffRequest(BaseModel):
    """差异比较请求模式"""
    old_version_id: str
    new_version_id: str
    diff_mode: str = Field(default="semantic", pattern="^(character|word|line|semantic)$")
    ignore_whitespace: bool = False
    ignore_case: bool = False


class DiffChange(BaseModel):
    """差异变化项"""
    type: str  # 'added', 'deleted', 'modified', 'unchanged'
    old_text: Optional[str] = None
    new_text: Optional[str] = None
    old_line_start: Optional[int] = None
    old_line_end: Optional[int] = None
    new_line_start: Optional[int] = None
    new_line_end: Optional[int] = None


class DiffResponse(BaseModel):
    """差异比较响应模式"""
    old_version_id: str
    new_version_id: str
    old_version_number: int
    new_version_number: int
    changes: List[DiffChange]
    stats: dict  # 统计信息：添加行数、删除行数等


# ============ Common Response ============

class SuccessResponse(BaseModel):
    """成功响应模式"""
    success: bool = True
    message: str
    data: Optional[dict] = None


class ErrorResponse(BaseModel):
    """错误响应模式"""
    success: bool = False
    error: dict
