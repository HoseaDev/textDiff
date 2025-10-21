"""
差异比较相关的API路由
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...schemas.document import DiffResponse, DiffChange
from ...services.version_service import VersionService
from ...services.diff_service import DiffService

router = APIRouter(prefix="/diff", tags=["diff"])


@router.get("/{version1_id}/{version2_id}", response_model=DiffResponse)
async def compare_versions_by_id(
    version1_id: str,
    version2_id: str,
    diff_mode: str = Query(
        default="semantic",
        pattern="^(character|word|line|semantic)$",
        description="差异模式: character, word, line, semantic",
    ),
    ignore_whitespace: bool = Query(
        default=False, description="是否忽略空白字符差异"
    ),
    ignore_case: bool = Query(default=False, description="是否忽略大小写"),
    db: Session = Depends(get_db),
):
    """
    比较两个版本的差异（通过版本ID）

    - **version1_id**: 旧版本ID
    - **version2_id**: 新版本ID
    - **diff_mode**: 差异粒度
      - `character`: 字符级差异（最细粒度）
      - `word`: 单词级差异
      - `line`: 行级差异（快速）
      - `semantic`: 语义级差异（推荐，智能）
    - **ignore_whitespace**: 忽略空白字符
    - **ignore_case**: 忽略大小写
    """
    # 获取版本
    version1 = VersionService.get_version(db, version1_id)
    version2 = VersionService.get_version(db, version2_id)

    if not version1 or not version2:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Version not found"
        )

    # 检查是否属于同一文档
    if version1.document_id != version2.document_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Versions must belong to the same document",
        )

    # 计算差异
    changes, stats = DiffService.compute_diff(
        version1.content,
        version2.content,
        diff_mode=diff_mode,
        ignore_whitespace=ignore_whitespace,
        ignore_case=ignore_case,
    )

    return DiffResponse(
        old_version_id=version1_id,
        new_version_id=version2_id,
        old_version_number=version1.version_number,
        new_version_number=version2.version_number,
        changes=changes,
        stats=stats,
    )


@router.get(
    "/document/{document_id}/number/{version_num1}/{version_num2}",
    response_model=DiffResponse,
)
async def compare_versions_by_number(
    document_id: str,
    version_num1: int,
    version_num2: int,
    diff_mode: str = Query(
        default="semantic", pattern="^(character|word|line|semantic)$"
    ),
    ignore_whitespace: bool = Query(default=False),
    ignore_case: bool = Query(default=False),
    db: Session = Depends(get_db),
):
    """
    比较两个版本的差异（通过版本号）

    更便捷的方式，直接使用版本号进行比较
    - **document_id**: 文档ID
    - **version_num1**: 旧版本号
    - **version_num2**: 新版本号
    """
    # 获取版本
    version1 = VersionService.get_version_by_number(db, document_id, version_num1)
    version2 = VersionService.get_version_by_number(db, document_id, version_num2)

    if not version1 or not version2:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Version not found"
        )

    # 计算差异
    changes, stats = DiffService.compute_diff(
        version1.content,
        version2.content,
        diff_mode=diff_mode,
        ignore_whitespace=ignore_whitespace,
        ignore_case=ignore_case,
    )

    return DiffResponse(
        old_version_id=version1.id,
        new_version_id=version2.id,
        old_version_number=version1.version_number,
        new_version_number=version2.version_number,
        changes=changes,
        stats=stats,
    )


@router.get("/document/{document_id}/latest/{version_id}", response_model=DiffResponse)
async def compare_with_latest(
    document_id: str,
    version_id: str,
    diff_mode: str = Query(default="semantic"),
    ignore_whitespace: bool = Query(default=False),
    ignore_case: bool = Query(default=False),
    db: Session = Depends(get_db),
):
    """
    将指定版本与最新版本比较

    快捷方式，用于查看历史版本与当前版本的差异
    """
    # 获取指定版本
    old_version = VersionService.get_version(db, version_id)
    if not old_version or old_version.document_id != document_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Version not found"
        )

    # 获取最新版本
    latest_version = VersionService.get_latest_version(db, document_id)
    if not latest_version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No latest version found"
        )

    # 如果是同一版本，返回空差异
    if old_version.id == latest_version.id:
        return DiffResponse(
            old_version_id=old_version.id,
            new_version_id=latest_version.id,
            old_version_number=old_version.version_number,
            new_version_number=latest_version.version_number,
            changes=[],
            stats={"added": 0, "deleted": 0, "modified": 0, "unchanged": 0},
        )

    # 计算差异
    changes, stats = DiffService.compute_diff(
        old_version.content,
        latest_version.content,
        diff_mode=diff_mode,
        ignore_whitespace=ignore_whitespace,
        ignore_case=ignore_case,
    )

    return DiffResponse(
        old_version_id=old_version.id,
        new_version_id=latest_version.id,
        old_version_number=old_version.version_number,
        new_version_number=latest_version.version_number,
        changes=changes,
        stats=stats,
    )
