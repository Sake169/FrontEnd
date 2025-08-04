from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import uvicorn
import logging
from pathlib import Path

from app.core.config import settings
from app.core.dependencies import get_logger
from app.api import upload, excel, ai
from app.services.file_service import FileService
from app.services.excel_service import ExcelService
from app.services.ai_service import AIService

# 配置日志
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(settings.log_file)
    ]
)

logger = logging.getLogger(__name__)

# 全局服务实例
file_service = FileService()
excel_service = ExcelService()
ai_service = AIService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    logger.info("正在启动后端服务...")
    
    # 创建必要的目录
    Path(settings.upload_dir).mkdir(exist_ok=True)
    Path(settings.output_dir).mkdir(exist_ok=True)
    Path("logs").mkdir(exist_ok=True)
    
    # 配置AI服务
    ai_config = {
        "api_key": settings.ai_model_api_key,
        "endpoint": settings.ai_model_endpoint,
        "timeout": settings.ai_model_timeout
    }
    ai_service.configure(ai_config)
    
    logger.info(f"后端服务已启动，监听端口: {settings.port}")
    
    yield
    
    # 关闭时执行
    logger.info("正在关闭后端服务...")

# 创建FastAPI应用
app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件
if Path("static").exists():
    app.mount("/static", StaticFiles(directory="static"), name="static")

# 注册路由
app.include_router(upload.router, prefix="/api/v1", tags=["文件上传"])
app.include_router(excel.router, prefix="/api/v1", tags=["Excel处理"])
app.include_router(ai.router, prefix="/api/v1", tags=["AI服务"])

# 依赖注入
def get_file_service() -> FileService:
    return file_service

def get_excel_service() -> ExcelService:
    return excel_service

def get_ai_service() -> AIService:
    return ai_service

# 根路径
@app.get("/")
async def root():
    """根路径 - 服务状态"""
    return {
        "message": "Excel处理后端服务",
        "version": settings.app_version,
        "status": "running",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }

# 健康检查
@app.get("/health")
async def health_check():
    """健康检查端点"""
    try:
        # 检查各个服务的状态
        ai_health = await ai_service.health_check()
        
        return {
            "status": "healthy",
            "timestamp": ai_health["timestamp"],
            "services": {
                "file_service": "healthy",
                "excel_service": "healthy",
                "ai_service": ai_health["status"]
            },
            "version": settings.app_version
        }
    except Exception as e:
        logger.error(f"健康检查失败: {str(e)}")
        raise HTTPException(status_code=503, detail="服务不可用")

# 服务信息
@app.get("/info")
async def service_info():
    """获取服务信息"""
    return {
        "name": settings.app_name,
        "description": settings.app_description,
        "version": settings.app_version,
        "environment": "development" if settings.debug else "production",
        "features": {
            "file_upload": True,
            "excel_processing": True,
            "ai_analysis": bool(settings.ai_model_api_key),
            "cors_enabled": True
        },
        "limits": {
            "max_file_size": f"{settings.max_file_size // (1024*1024)}MB",
            "allowed_file_types": settings.allowed_file_types
        }
    }

# 错误处理
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {
        "error": "Not Found",
        "message": "请求的资源不存在",
        "status_code": 404
    }

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error(f"内部服务器错误: {str(exc)}")
    return {
        "error": "Internal Server Error",
        "message": "服务器内部错误",
        "status_code": 500
    }

# 开发模式下的调试信息
if settings.debug:
    @app.get("/debug/config")
    async def debug_config():
        """调试配置信息（仅开发模式）"""
        return {
            "project_name": settings.app_name,
            "debug": settings.debug,
            "host": settings.host,
            "port": settings.port,
            "upload_dir": settings.upload_dir,
            "output_dir": settings.output_dir,
            "max_file_size": settings.max_file_size,
            "allowed_file_types": settings.allowed_file_types,
            "ai_configured": bool(settings.ai_model_api_key),
            "cors_origins": settings.allowed_origins
        }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level.lower()
    )