"""
验证码相关API路由
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from ...core.database import get_db
from ...services.verification_service import VerificationService


router = APIRouter(prefix="/verification", tags=["verification"])


class SendCodeRequest(BaseModel):
    """发送验证码请求"""
    email: EmailStr
    purpose: str = "register"  # register/login/reset_password


class SendCodeResponse(BaseModel):
    """发送验证码响应"""
    success: bool
    message: str
    code_id: str | None = None


class VerifyCodeRequest(BaseModel):
    """验证验证码请求"""
    email: EmailStr
    code: str
    purpose: str = "register"


class VerifyCodeResponse(BaseModel):
    """验证验证码响应"""
    success: bool
    message: str


@router.post("/send", response_model=SendCodeResponse)
async def send_verification_code(
    request: Request,
    data: SendCodeRequest,
    db: Session = Depends(get_db)
):
    """
    发送验证码到邮箱

    防机器人机制:
    - 同一邮箱60秒内只能发送1次
    - 同一IP 1分钟内最多发送3次
    - 同一邮箱1小时内最多发送10次
    """
    # 获取客户端IP地址
    ip_address = request.client.host if request.client else None

    # 验证用途
    if data.purpose not in ["register", "login", "reset_password"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid purpose"
        )

    # 创建并发送验证码
    success, message, code_id = VerificationService.create_verification_code(
        db=db,
        email=data.email,
        purpose=data.purpose,
        ip_address=ip_address
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=message
        )

    return SendCodeResponse(
        success=True,
        message=message,
        code_id=code_id
    )


@router.post("/verify", response_model=VerifyCodeResponse)
async def verify_code(
    data: VerifyCodeRequest,
    db: Session = Depends(get_db)
):
    """
    验证验证码
    """
    success, message = VerificationService.verify_code(
        db=db,
        email=data.email,
        code=data.code,
        purpose=data.purpose
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )

    return VerifyCodeResponse(
        success=True,
        message=message
    )
