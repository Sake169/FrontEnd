from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import logging
from .config import settings

# 配置日志
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(settings.log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# HTTP Bearer认证（预留）
security = HTTPBearer(auto_error=False)

async def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    """获取当前用户（预留认证功能）"""
    # 这里可以添加JWT token验证逻辑
    # 目前返回None，表示无需认证
    return None

def get_logger():
    """获取日志记录器"""
    return logger

def validate_file_size(file_size: int) -> bool:
    """验证文件大小"""
    return file_size <= settings.max_file_size

def validate_file_type(content_type: str) -> bool:
    """验证文件类型"""
    return content_type in settings.allowed_file_types

async def get_upload_path():
    """获取上传路径"""
    return settings.upload_dir

async def get_output_path():
    """获取输出路径"""
    return settings.output_dir