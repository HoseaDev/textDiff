"""
文档相关的API路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from ...core.database import get_db
from ...core.auth import get_current_active_user
from ...models.user import User
from ...schemas.document import (
    DocumentCreate,
    DocumentUpdate,
    DocumentResponse,
    VersionCreate,
    VersionResponse,
    VersionListItem,
    VersionTagCreate,
    VersionTagResponse,
    SuccessResponse,
)
from ...services.version_service import VersionService

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_document(
    doc_data: DocumentCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    创建新文档

    创建一个新文档并自动生成初始版本
    """
    document = VersionService.create_document(db, doc_data, owner_id=current_user.id)
    return document


@router.get("", response_model=List[DocumentResponse])
async def get_documents(
    skip: int = 0,
    limit: int = 20,
    sort_by: str = "updated_at",
    folder_id: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    获取当前用户的文档列表

    支持分页和排序
    - **skip**: 跳过的记录数
    - **limit**: 返回的最大记录数
    - **sort_by**: 排序字段 (updated_at, created_at, title)
    - **folder_id**: 文件夹ID筛选(可选)
    """
    documents = VersionService.get_user_documents(
        db, current_user.id, skip, limit, sort_by, folder_id
    )
    return documents


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    获取文档详情

    返回指定文档的详细信息(仅限所有者)
    """
    document = VersionService.get_document(db, document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
        )

    # 检查权限
    if document.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this document"
        )

    return document


@router.put("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: str,
    doc_data: DocumentUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    更新文档信息

    更新文档的基本信息（如标题）
    """
    document = VersionService.get_document(db, document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
        )

    # 检查权限
    if document.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this document"
        )

    updated_document = VersionService.update_document(db, document_id, doc_data)
    return updated_document


@router.delete("/{document_id}", response_model=SuccessResponse)
async def delete_document(
    document_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    删除文档

    删除文档及其所有版本（级联删除）
    """
    document = VersionService.get_document(db, document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
        )

    # 检查权限
    if document.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this document"
        )

    success = VersionService.delete_document(db, document_id)
    return SuccessResponse(success=True, message="Document deleted successfully")


# ============ 版本相关路由 ============


@router.post("/{document_id}/versions", response_model=VersionResponse)
async def create_version(
    document_id: str,
    version_data: VersionCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    创建新版本

    为文档创建新版本。如果内容未变化，则不创建新版本。
    """
    # 检查文档权限
    document = VersionService.get_document(db, document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
        )

    if document.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to modify this document"
        )

    version = VersionService.create_version(
        db, document_id, version_data, author_id=current_user.id
    )
    if not version:
        # 获取最新版本返回
        latest = VersionService.get_latest_version(db, document_id)
        if latest:
            return latest
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
        )
    return version


@router.get("/{document_id}/versions", response_model=List[VersionListItem])
async def get_versions(
    document_id: str,
    skip: int = 0,
    limit: int = 50,
    save_type: str = None,
    db: Session = Depends(get_db),
):
    """
    获取文档的版本列表

    返回文档的所有版本（不含内容，减少数据量）
    - **skip**: 跳过的记录数
    - **limit**: 返回的最大记录数
    - **save_type**: 筛选保存类型 (manual, auto, draft)
    """
    versions = VersionService.get_versions(db, document_id, skip, limit, save_type)

    # 转换为列表项格式（不包含完整内容）
    version_items = []
    for v in versions:
        version_items.append(
            VersionListItem(
                id=v.id,
                version_number=v.version_number,
                created_at=v.created_at,
                author=v.author,
                commit_message=v.commit_message,
                save_type=v.save_type,
                content_length=len(v.content),
            )
        )

    return version_items


@router.get("/{document_id}/versions/{version_id}", response_model=VersionResponse)
async def get_version(
    document_id: str, version_id: str, db: Session = Depends(get_db)
):
    """
    获取指定版本的完整内容
    """
    version = VersionService.get_version(db, version_id)
    if not version or version.document_id != document_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Version not found"
        )
    return version


@router.get(
    "/{document_id}/versions/number/{version_number}", response_model=VersionResponse
)
async def get_version_by_number(
    document_id: str, version_number: int, db: Session = Depends(get_db)
):
    """
    根据版本号获取版本
    """
    version = VersionService.get_version_by_number(db, document_id, version_number)
    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Version not found"
        )
    return version


@router.post(
    "/{document_id}/restore/{version_id}", response_model=VersionResponse
)
async def restore_version(
    document_id: str, version_id: str, db: Session = Depends(get_db)
):
    """
    恢复到指定版本

    通过创建新版本的方式恢复到历史版本
    """
    version = VersionService.restore_version(db, document_id, version_id)
    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Version not found or does not belong to this document",
        )
    return version


# ============ 版本标签相关路由 ============


@router.post(
    "/{document_id}/versions/{version_id}/tags",
    response_model=VersionTagResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_version_tag(
    document_id: str,
    version_id: str,
    tag_data: VersionTagCreate,
    db: Session = Depends(get_db),
):
    """
    为版本创建标签

    为重要版本添加标记和说明
    """
    tag = VersionService.create_version_tag(db, version_id, tag_data)
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Version not found"
        )
    return tag


@router.get(
    "/{document_id}/versions/{version_id}/tags",
    response_model=List[VersionTagResponse],
)
async def get_version_tags(
    document_id: str, version_id: str, db: Session = Depends(get_db)
):
    """
    获取版本的所有标签
    """
    tags = VersionService.get_version_tags(db, version_id)
    return tags


@router.delete("/tags/{tag_id}", response_model=SuccessResponse)
async def delete_version_tag(tag_id: str, db: Session = Depends(get_db)):
    """
    删除版本标签
    """
    success = VersionService.delete_version_tag(db, tag_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found"
        )
    return SuccessResponse(success=True, message="Tag deleted successfully")
