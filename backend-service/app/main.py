from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from contextlib import asynccontextmanager
import uvicorn
import logging
from pathlib import Path
import pandas as pd

from app.core.config import settings
from app.core.dependencies import get_logger
from app.core.database import init_db
from app.api import auth, upload, excel, ai, family_member, securities_report, investment_records, investors, investment_portfolios
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
    
    # 初始化数据库
    try:
        init_db()
        logger.info("[SUCCESS] 数据库初始化完成")
    except Exception as e:
        logger.error(f"[ERROR] 数据库初始化失败: {e}")
        raise
    
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

# 处理example.xlsx请求
@app.get("/api/example.xlsx")
async def get_example_excel():
    """返回示例Excel文件"""
    try:
        # 尝试从多个位置查找example.xlsx
        possible_paths = [
            Path("../example.xlsx"),
            Path("example.xlsx"),
            Path("outputs/example.xlsx"),
            Path("templates/example.xlsx")
        ]
        
        for file_path in possible_paths:
            if file_path.exists():
                return FileResponse(
                    path=file_path,
                    filename="example.xlsx",
                    media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
        
        # 如果找不到文件，创建一个示例Excel文件
        sample_data = {
            '交易日期': ['2024-01-15', '2024-01-16', '2024-01-17'],
            '证券代码': ['000001', '000002', '000003'],
            '证券名称': ['平安银行', '万科A', '国农科技'],
            '交易类型': ['买入', '卖出', '买入'],
            '交易数量': [1000, 500, 2000],
            '交易价格': [10.50, 25.30, 8.75],
            '交易金额': [10500.00, 12650.00, 17500.00]
        }
        
        df = pd.DataFrame(sample_data)
        output_path = Path("outputs")
        output_path.mkdir(exist_ok=True)
        excel_path = output_path / "example.xlsx"
        df.to_excel(excel_path, index=False)
        
        return FileResponse(
            path=excel_path,
            filename="example.xlsx",
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        logger.error(f"获取示例Excel文件失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取示例文件失败")

# 注册路由
app.include_router(auth.router, prefix="/api/v1/auth", tags=["认证"])
app.include_router(upload.router, prefix="/api/v1", tags=["文件上传"])
app.include_router(excel.router, prefix="/api/v1", tags=["Excel处理"])
app.include_router(ai.router, prefix="/api/v1", tags=["AI服务"])
app.include_router(family_member.router, prefix="/api/v1/family-members", tags=["家属亲戚管理"])
app.include_router(securities_report.router, prefix="/api/v1/securities-reports", tags=["证券填报管理"])
app.include_router(investment_records.router, prefix="/api/v1", tags=["投资记录管理"])
app.include_router(investors.router, prefix="/api/v1", tags=["投资人管理"])
app.include_router(investment_portfolios.router, prefix="/api/v1", tags=["投资组合管理"])

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
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": "请求的资源不存在",
            "status_code": 404
        }
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error(f"内部服务器错误: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "服务器内部错误",
            "status_code": 500
        }
    )

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