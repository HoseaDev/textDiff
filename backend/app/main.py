"""
FastAPI 主应用
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from .core.config import settings
from .core.database import init_db
from .api.routes import documents, diff, websocket, auth, verification


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    print("Initializing database...")
    init_db()
    print("Database initialized successfully!")
    yield
    # 关闭时执行
    print("Shutting down...")


# 创建 FastAPI 应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="文本版本管理与差异比较系统 API",
    lifespan=lifespan,
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全局异常处理器"""
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": 500,
                "message": str(exc),
                "type": "InternalServerError",
            },
        },
    )


# 注册路由
app.include_router(auth.router, prefix="/api")  # 认证路由
app.include_router(verification.router, prefix="/api")  # 验证码路由
app.include_router(documents.router, prefix="/api")
app.include_router(diff.router, prefix="/api")
app.include_router(websocket.router)


# 健康检查端点
@app.get("/")
async def root():
    """根路径 - API 信息"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )
